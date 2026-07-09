"""Universal Search Module with Lazy Loading.

This module provides a universal search interface for Congressional data that dynamically
loads search handlers only when needed, avoiding unnecessary imports and keeping the
memory footprint minimal.

The search system uses a registry-based architecture where each resource type (bills,
amendments, members, etc.) is mapped to a specific search handler function. These handlers
are only imported when first accessed, providing excellent performance characteristics.

Design Principles
-----------------
Lazy Loading
    Search handlers are imported only when first accessed, not at module import time.
    
Dynamic Dispatch
    Routes to the appropriate handler based on resource type string.
    
Extensible
    New resource types can be added to the registry without modifying core code.
    
Type-Safe
    Supports parameter aliases and validation for user-friendly API.

Supported Resource Types
------------------------
- ``bill`` : Bills and resolutions
- ``amendment`` : Amendments to bills
- ``member`` : Members of Congress
- ``committee`` : Congressional committees
- ``nomination`` : Presidential nominations
- ``treaty`` : International treaties
- ``hearing`` : Committee hearings
- ``committee-meeting`` : Committee meetings
- ``committee-report`` : Committee reports
- ``committee-print`` : Committee prints
- ``house-communication`` : House communications
- ``senate-communication`` : Senate communications
- ``congress`` : Congress sessions
- ``summary`` : Bill summaries

Examples
--------
Basic bill search by congress and bill number:

    >>> results = search('bill', congress=119, type='hr', number=176)
    >>> print(results.bill.title)

Search amendments with date filters:

    >>> results = search(
    ...     'amendment',
    ...     congress=118,
    ...     type='hamdt',
    ...     from_date_time='2023-01-01',
    ...     to_date_time='2023-12-31'
    ... )

Search with custom client and pagination:

    >>> from congressgov._client import AuthenticatedClient
    >>> client = AuthenticatedClient(base_url='https://api.congress.gov/v3', token='your_key')
    >>> results = search(
    ...     'member',
    ...     client=client,
    ...     state='CA',
    ...     limit=50,
    ...     offset=100
    ... )

Register a custom search handler:

    >>> register_search_handler(
    ...     'custom_resource',
    ...     'my_module.custom_search',
    ...     'custom_search_func',
    ...     param_aliases={'type': 'custom_type'}
    ... )

Module Attributes
-----------------
_SEARCH_REGISTRY : Dict[str, HandlerConfig]
    Global registry mapping resource types to handler configurations. This is the
    core of the lazy loading system. Handlers are defined here but not imported
    until first accessed. Use ``register_search_handler()`` and 
    ``unregister_search_handler()`` to modify this registry.
    
_HANDLER_CACHE : Dict[str, Callable]
    Legacy cache dictionary kept for backwards compatibility. Actual caching is
    now handled by the ``@lru_cache`` decorator on ``_load_search_handler()``.
    
logger : logging.Logger
    Module-level logger for debugging lazy loading operations. Set to DEBUG level
    to see when handlers are loaded: ``logging.getLogger('congressgov.services.core.search').setLevel(logging.DEBUG)``

Public Functions
----------------
search
    Universal search interface - main entry point for all searches
register_search_handler
    Register a new search handler for a custom resource type
unregister_search_handler
    Remove a search handler from the registry
get_registered_types
    Get list of all registered resource types

Type Definitions
----------------
HandlerConfig : TypedDict
    Configuration structure for search handlers in the registry

See Also
--------
get_registered_types : Get list of all available resource types
register_search_handler : Register a custom search handler
unregister_search_handler : Remove a search handler from the registry

Notes
-----
This module follows NumPy/SciPy documentation conventions for maximum compatibility
with documentation generators (Sphinx) and IDE IntelliSense systems.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, TypedDict, overload, Literal, TYPE_CHECKING
import importlib
import logging
from functools import lru_cache

# NOTE: Import ModelRegistry for lazy model loading in search handlers
from congressgov.services.core.model_registry import ModelRegistry

# NOTE: Configure module-level logger for debugging lazy loading
logger = logging.getLogger(__name__)

# ============================================================================
# TYPE CHECKING IMPORTS
# ============================================================================
# NOTE: These imports are only used for type checking and don't affect runtime
# This prevents circular imports and keeps lazy loading working

if TYPE_CHECKING:
    from congressgov.models.entities import Bills, Amendments, Members, Treaties, Congresses, Summaries
    from congressgov.models.committees import Committees
    from congressgov.models.nominations import Nominations
    from congressgov.models.documents import Hearings, CommitteeReports, CommitteePrints
    from congressgov.models.meetings import CommitteeMeetings
    from congressgov.models.communications import HouseCommunications, SenateCommunications


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

# NOTE: ResourceType literal provides autocomplete for valid resource type strings
ResourceType = Literal[
    'bill',
    'amendment',
    'member',
    'committee',
    'nomination',
    'treaty',
    'hearing',
    'committee-meeting',
    'committee-report',
    'committee-print',
    'house-communication',
    'senate-communication',
    'congress',
    'summary'
]
"""Type alias for all valid resource type identifiers.

This literal union provides IDE autocomplete and type checking for the
``resource_type`` parameter in the ``search()`` function. Using this type
ensures compile-time validation of resource type strings.

Valid values:
    - ``'bill'`` : Bills and resolutions
    - ``'amendment'`` : Amendments to bills
    - ``'member'`` : Members of Congress
    - ``'committee'`` : Congressional committees
    - ``'nomination'`` : Presidential nominations
    - ``'treaty'`` : International treaties
    - ``'hearing'`` : Committee hearings
    - ``'committee-meeting'`` : Committee meetings
    - ``'committee-report'`` : Committee reports
    - ``'committee-print'`` : Committee prints
    - ``'house-communication'`` : House communications
    - ``'senate-communication'`` : Senate communications
    - ``'congress'`` : Congress sessions
    - ``'summary'`` : Bill summaries

Examples
--------
>>> from congressgov.services.core.search import ResourceType, search
>>> # IDE provides autocomplete for valid types
>>> resource: ResourceType = 'bill'
>>> results = search(resource, congress=119)
"""


class HandlerConfig(TypedDict):
    """Configuration for a search handler in the registry.
    
    Attributes
    ----------
    module : str
        Full Python import path to the module containing the search function.
    function : str
        Name of the search function within the module.
    param_aliases : Dict[str, str]
        Mapping of user-friendly parameter names to canonical parameter names.
    """
    module: str
    function: str
    param_aliases: Dict[str, str]


# ============================================================================
# SEARCH HANDLER REGISTRY
# ============================================================================

_SEARCH_REGISTRY: Dict[str, HandlerConfig]
"""Global registry of search handlers for Congressional data resources.

This dictionary maps resource type identifiers (e.g., 'bill', 'amendment') to their
handler configurations. Each configuration specifies:

- ``module``: Python import path to the module containing the search function
- ``function``: Name of the search function within that module  
- ``param_aliases``: User-friendly parameter name mappings

The registry enables lazy loading: handlers are defined here but not imported until
first accessed. This keeps initial module import fast and memory usage minimal.

**Registry Structure:**
    
    .. code-block:: python
    
        {
            'bill': {
                'module': 'congressgov.services.bill',
                'function': 'billsearch',
                'param_aliases': {'type': 'bill_type', 'number': 'bill_number'}
            },
            ...
        }

**Adding Handlers:**

Use ``register_search_handler()`` to add new types:

    >>> register_search_handler(
    ...     'custom-type',
    ...     'my_module.search',
    ...     'custom_search',
    ...     param_aliases={'id': 'custom_id'}
    ... )

**Supported Resource Types:**

- bill, amendment, member, committee
- nomination, treaty, hearing
- committee-meeting, committee-report, committee-print
- house-communication, senate-communication
- congress, summary

See Also
--------
register_search_handler : Add new handlers to the registry
get_registered_types : List all registered types
HandlerConfig : TypedDict defining the configuration structure
"""

_SEARCH_REGISTRY = {
    'bill': {
        'module': 'congressgov.services.core.search',
        'function': 'billsearch',  # ✅ Updated to use local handler
        'param_aliases': {
            'type': 'bill_type',
            'number': 'bill_number',
        }
    },
    'amendment': {
        'module': 'congressgov.services.core.search',
        'function': 'amendmentsearch',  # ✅ Local handler
        'param_aliases': {
            'type': 'amendment_type',
            'number': 'amendment_number',
        }
    },
    'member': {
        'module': 'congressgov.services.core.search',
        'function': 'membersearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'committee': {
        'module': 'congressgov.services.core.search',
        'function': 'committeesearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'nomination': {
        'module': 'congressgov.services.core.search',
        'function': 'nominationsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'treaty': {
        'module': 'congressgov.services.core.search',
        'function': 'treatysearch',  # ✅ Local handler
        'param_aliases': {
            'number': 'treaty_number',
        }
    },
    'hearing': {
        'module': 'congressgov.services.core.search',
        'function': 'hearingsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'committee-meeting': {
        'module': 'congressgov.services.core.search',
        'function': 'committeemeetingsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'committee-report': {
        'module': 'congressgov.services.core.search',
        'function': 'committeereportsearch',  # ✅ Local handler
        'param_aliases': {
            'type': 'report_type',
        }
    },
    'committee-print': {
        'module': 'congressgov.services.core.search',
        'function': 'committeeprintsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'house-communication': {
        'module': 'congressgov.services.core.search',
        'function': 'housecommunicationsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'senate-communication': {
        'module': 'congressgov.services.core.search',
        'function': 'senatecommunicationsearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'congress': {
        'module': 'congressgov.services.core.search',
        'function': 'congresssearch',  # ✅ Local handler
        'param_aliases': {}
    },
    'summary': {
        'module': 'congressgov.services.core.search',
        'function': 'summariessearch',  # ✅ Local handler
        'param_aliases': {
            'type': 'bill_type',
        }
    },
    'bound-congressional-record': {
        'module': 'congressgov.services.core.search',
        'function': 'boundcongressionalrecordsearch',
        'param_aliases': {},
    },
    'congressional-record': {
        'module': 'congressgov.services.core.search',
        'function': 'congressionalrecordsearch',
        'param_aliases': {
            'year': 'y',
            'month': 'm',
            'day': 'd',
        }
    },
    'crs-report': {
        'module': 'congressgov.services.core.search',
        'function': 'crsreportsearch',
        'param_aliases': {},
    },
    'house-requirement': {
        'module': 'congressgov.services.core.search',
        'function': 'houserequirementsearch',
        'param_aliases': {},
    },
    'house-vote': {
        'module': 'congressgov.services.core.search',
        'function': 'housevotesearch',
        'param_aliases': {},
    },
}

# NOTE: Cache for loaded search functions is managed by @lru_cache decorator on
# _load_search_handler(). This explicit cache dict is no longer used but kept for
# backwards compatibility if any external code references it.
_HANDLER_CACHE: Dict[str, Callable] = {}


def _attach_client_to_search_result(result: Any, client: Any) -> Any:
    """Attach *client* to a search result and any nested list-of-model items.

    Individual search handlers resolve a client internally to make their API
    call, but most only attach it to single-item results (e.g. a specific
    Bill), leaving list results (e.g. ``Bills``, ``Members``) without a
    ``.client`` set. That breaks downstream extension/expand methods that
    rely on ``target.client`` for fallback client resolution. Centralizing
    the attachment here (rather than in every handler) keeps the fix in one
    place regardless of which handler produced the result.
    """
    if client is None or result is None:
        return result

    from congressgov.models.base.model import Model

    if isinstance(result, Model) and getattr(result, "client", None) is None:
        result.client = client

    model_fields = getattr(type(result), "model_fields", None) or {}
    for field_name in model_fields:
        value = getattr(result, field_name, None)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, Model) and getattr(item, "client", None) is None:
                    item.client = client

    return result


# ============================================================================
# LAZY LOADING UTILITIES
# ============================================================================

@lru_cache(maxsize=32)
def _load_search_handler(resource_type: str) -> Callable[..., Any]:
    """Lazily load and cache a search handler function for a given resource type.
    
    This function uses dynamic imports to load search handlers only when they are
    first needed, significantly reducing initial import overhead and memory usage.
    The loaded handlers are cached using LRU caching to optimize repeated access.
    
    The caching strategy prevents redundant imports for frequently used resource
    types while keeping memory usage bounded. The cache is automatically cleared
    when the registry is modified to ensure consistency.
    
    Parameters
    ----------
    resource_type : str
        The type of Congressional resource to search for. Must be one of the
        registered resource types (e.g., 'bill', 'amendment', 'member', 'committee').
        Use ``get_registered_types()`` to see all available types.
        
    Returns
    -------
    Callable[..., Any]
        The search handler function for the specified resource type. The function
        signature varies by handler but generally accepts parameters like congress,
        type, number, limit, offset, and client.
        
    Raises
    ------
    ValueError
        If the specified ``resource_type`` is not registered in the search registry.
        The error message includes a list of available resource types.
    ImportError
        If the module containing the search handler cannot be imported. This may
        indicate a missing dependency or incorrect module path in the registry.
    AttributeError
        If the specified function name doesn't exist in the loaded module. This
        indicates a configuration error in the registry.
        
    Notes
    -----
    - Uses ``@lru_cache`` decorator to memoize loaded handlers (max 32 entries)
    - Cache is cleared when handlers are registered/unregistered
    - Thread-safe due to LRU cache implementation
    - Logging at DEBUG level tracks module loading operations
    
    Examples
    --------
    >>> handler = _load_search_handler('bill')
    >>> results = handler(None, congress=119, bill_type='hr', bill_number=176)
    
    >>> # Get handler for amendments
    >>> amdt_handler = _load_search_handler('amendment')
    >>> # Subsequent calls return cached version (fast!)
    >>> amdt_handler_again = _load_search_handler('amendment')
    >>> assert amdt_handler is amdt_handler_again
    
    See Also
    --------
    get_registered_types : Get all registered resource types
    register_search_handler : Register a new search handler
    """
    # --- <VALIDATE RESOURCE TYPE> ---
    if resource_type not in _SEARCH_REGISTRY:
        available = ', '.join(_SEARCH_REGISTRY.keys())
        raise ValueError(
            f"Unknown resource type '{resource_type}'. "
            f"Available types: {available}"
        )
    
    handler_config = _SEARCH_REGISTRY[resource_type]
    module_path = handler_config['module']
    function_name = handler_config['function']
    
    # --- <LAZY IMPORT MODULE> ---
    # NOTE: This is the key to lazy loading - we only import when needed
    logger.debug(f"Loading search handler: {module_path}.{function_name}")
    
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(
            f"Failed to import module '{module_path}' for resource type '{resource_type}': {e}"
        )
    
    # --- <EXTRACT FUNCTION FROM MODULE> ---
    try:
        handler_func = getattr(module, function_name)
    except AttributeError as e:
        raise AttributeError(
            f"Function '{function_name}' not found in module '{module_path}': {e}"
        )
    
    logger.debug(f"Successfully loaded search handler for '{resource_type}'")
    return handler_func


def _normalize_parameters(
    resource_type: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Normalize parameter names using registered aliases for the resource type.
    
    Converts user-friendly parameter names to the canonical names expected by
    the underlying search handler functions. This allows users to use intuitive
    parameter names (like 'type' and 'number') which are automatically mapped to
    resource-specific names (like 'bill_type' and 'bill_number').
    
    The alias mappings are defined in the search registry for each resource type.
    Parameters without aliases are passed through unchanged.
    
    Parameters
    ----------
    resource_type : str
        The type of Congressional resource being searched (e.g., 'bill', 'amendment').
        Must be a registered resource type.
    params : Dict[str, Any]
        Dictionary of search parameters with user-friendly names. These are the
        keyword arguments passed to the ``search()`` function.
        
    Returns
    -------
    Dict[str, Any]
        Dictionary with normalized parameter names. User-friendly aliases are
        converted to canonical names expected by the search handler.
        
    Notes
    -----
    - Parameters without registered aliases are passed through unchanged
    - The function does not validate parameter values, only transforms names
    - Case-sensitive parameter name matching
    - Original params dict is not modified (returns new dict)
    
    Examples
    --------
    Normalize bill search parameters:
    
    >>> params = {'type': 'hr', 'number': 176, 'congress': 119}
    >>> normalized = _normalize_parameters('bill', params)
    >>> print(normalized)
    {'bill_type': 'hr', 'bill_number': 176, 'congress': 119}
    
    Parameters without aliases pass through:
    
    >>> params = {'state': 'CA', 'party': 'D', 'limit': 50}
    >>> normalized = _normalize_parameters('member', params)
    >>> print(normalized)
    {'state': 'CA', 'party': 'D', 'limit': 50}
    
    Amendment type normalization:
    
    >>> params = {'type': 'hamdt', 'number': 123}
    >>> normalized = _normalize_parameters('amendment', params)
    >>> print(normalized)
    {'amendment_type': 'hamdt', 'amendment_number': 123}
    
    See Also
    --------
    search : Main search function that uses this for parameter normalization
    register_search_handler : Define param_aliases when registering handlers
    """
    handler_config = _SEARCH_REGISTRY[resource_type]
    param_aliases = handler_config.get('param_aliases', {})
    
    normalized = {}
    
    for key, value in params.items():
        # --- <RESOLVE PARAMETER ALIAS> ---
        # If there's an alias mapping, use the canonical name
        canonical_key = param_aliases.get(key, key)
        normalized[canonical_key] = value
    
    return normalized


# ============================================================================
# UNIVERSAL SEARCH INTERFACE
# ============================================================================

# NOTE: Type overloads provide IntelliSense for each resource type
# Each overload specifies the exact parameters and return type for that resource

@overload
def search(
    resource_type: Literal['bill'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    type: str | None = None,
    number: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> Bills:
    ...


@overload
def search(
    resource_type: Literal['amendment'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    type: str | None = None,
    number: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> Amendments:
    ...


@overload
def search(
    resource_type: Literal['member'],
    self: Any = None,
    *,
    client: Any = None,
    state: str | None = None,
    district: int | None = None,
    congress: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    current_member: str | None = None
) -> Members:
    ...


@overload
def search(
    resource_type: Literal['committee'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    chamber: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None
) -> Committees:
    ...


@overload
def search(
    resource_type: Literal['nomination'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> Nominations:
    ...


@overload
def search(
    resource_type: Literal['treaty'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    number: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> Treaties:
    ...


@overload
def search(
    resource_type: Literal['hearing'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    chamber: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    sort: str | None = None
) -> Hearings:
    ...


@overload
def search(
    resource_type: Literal['committee-meeting'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    chamber: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None
) -> CommitteeMeetings:
    ...


@overload
def search(
    resource_type: Literal['committee-report'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    type: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> CommitteeReports:
    ...


@overload
def search(
    resource_type: Literal['committee-print'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    chamber: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None
) -> CommitteePrints:
    ...


@overload
def search(
    resource_type: Literal['house-communication'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None
) -> HouseCommunications:
    ...


@overload
def search(
    resource_type: Literal['senate-communication'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    communication_type: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None
) -> SenateCommunications:
    ...


@overload
def search(
    resource_type: Literal['congress'],
    self: Any = None,
    *,
    client: Any = None,
    current: bool | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None
) -> Congresses:
    ...


@overload
def search(
    resource_type: Literal['summary'],
    self: Any = None,
    *,
    client: Any = None,
    congress: int | None = None,
    type: str | None = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None
) -> Summaries:
    ...


def search(
    resource_type: ResourceType,
    self: Any = None,
    **kwargs: Any
) -> Any:
    """Universal search interface for Congressional data with lazy loading.
    
    This function provides a single, unified entry point for searching any type of
    Congressional resource (bills, amendments, members, committees, etc.). It
    dynamically loads the appropriate search handler based on the resource type and
    routes the request to the correct API endpoint.
    
    The function uses lazy loading to import search handlers only when first needed,
    making the initial module import fast and keeping memory usage minimal. Subsequent
    searches reuse cached handlers for optimal performance.
    
    Parameters
    ----------
    resource_type : str
        The type of Congressional resource to search for. Must be one of the registered
        types. Common values include:
        
        - ``'bill'`` : Bills and resolutions
        - ``'amendment'`` : Amendments to bills
        - ``'member'`` : Members of Congress
        - ``'committee'`` : Congressional committees
        - ``'nomination'`` : Presidential nominations
        - ``'treaty'`` : International treaties
        - ``'hearing'`` : Committee hearings
        - ``'committee-meeting'`` : Committee meetings
        - ``'committee-report'`` : Committee reports
        - ``'committee-print'`` : Committee prints
        - ``'house-communication'`` : House communications
        - ``'senate-communication'`` : Senate communications
        - ``'congress'`` : Congress sessions
        - ``'summary'`` : Bill summaries
        
        Use ``get_registered_types()`` for the complete list.
        
    self : Any, optional
        Optional context object for method-style calls. Used when integrating the
        search function as a method on a service or client class. Default is None
        for standalone function calls.
        
    **kwargs : Any
        Search parameters specific to the resource type. Common parameters include:
        
        **Common Parameters (most resource types)**
            - ``congress`` (int): Congress number (e.g., 118, 119)
            - ``limit`` (int): Maximum number of results to return (default varies)
            - ``offset`` (int): Number of results to skip for pagination (default 0)
            - ``format`` (str): Response format, usually 'json' (default 'json')
            - ``client`` (AuthenticatedClient): Custom API client instance
        
        **Bill-Specific Parameters**
            - ``type`` (str): Bill type ('hr', 's', 'hjres', 'sjres', 'hconres', 'sconres', 'hres', 'sres')
            - ``number`` (int): Bill number within the congress and type
            - ``from_date_time`` (str): Filter bills updated after this datetime (ISO format)
            - ``to_date_time`` (str): Filter bills updated before this datetime (ISO format)
        
        **Amendment-Specific Parameters**
            - ``type`` (str): Amendment type ('hamdt', 'samdt', 'suamdt')
            - ``number`` (int): Amendment number
            - ``from_date_time`` (str): Filter by update date/time
            - ``to_date_time`` (str): Filter by update date/time
        
        **Member-Specific Parameters**
            - ``state`` (str): Two-letter state code (e.g., 'CA', 'NY')
            - ``district`` (int): Congressional district number
            - ``party`` (str): Party affiliation ('D', 'R', 'I', etc.)
            - ``current_member`` (bool): Filter for current members only
        
        **Committee-Specific Parameters**
            - ``chamber`` (str): Chamber ('house', 'senate', 'joint')
            - ``committee_code`` (str): Official committee code
        
        **Date/Time Filtering** (where supported)
            - Format: ISO 8601 strings like '2023-01-01T00:00:00Z'
            - Both ``from_date_time`` and ``to_date_time`` are inclusive
        
        Note: Parameter names are automatically normalized using registered aliases.
        For example, ``type='hr'`` for bills is converted to ``bill_type='hr'``
        internally.
        
    Returns
    -------
    Any
        Search results from the appropriate handler. The return type varies by resource
        but is typically a Pydantic model containing:
        
        - The requested resource data (e.g., ``bill``, ``amendment``, ``member``)
        - Pagination information (``pagination`` object with count, next, prev)
        - Request metadata (``request`` object with URL, content type)
        
        For specific searches (with congress + type + number), returns the single
        resource. For list searches, returns a collection with pagination.
        
    Raises
    ------
    ValueError
        - If ``resource_type`` is not registered in the search system
        - If required parameters are missing for the specific resource type
        - If parameter values are invalid (e.g., invalid bill type)
    ImportError
        If the search handler module cannot be loaded. This typically indicates
        a configuration error in the registry or a missing dependency.
    AttributeError
        If the search handler function doesn't exist in the loaded module.
    requests.exceptions.RequestException
        If the API request fails due to network issues, authentication problems,
        or server errors.
        
    Notes
    -----
    **Lazy Loading Behavior**
        - Search handlers are only imported when first used for a resource type
        - Subsequent calls reuse cached handlers for optimal performance
        - Unrelated search functions are never loaded, reducing memory usage
        
    **Parameter Aliases**
        - Supports user-friendly parameter names (e.g., 'type' instead of 'bill_type')
        - Aliases are automatically normalized before passing to handlers
        - Alias mappings are defined per resource type in the registry
        
    **API Client**
        - If no ``client`` is provided, a default client is created automatically
        - The default client uses the API key from environment variable ``CONGRESS_API_KEY``
        - You can pass a custom client instance for advanced configuration
        
    **Pagination**
        - Use ``limit`` and ``offset`` for paginated results
        - Default ``limit`` is typically 20 (varies by endpoint)
        - Maximum ``limit`` is 250 for most endpoints
        - Check the ``pagination`` object in results for total count and navigation
    
    Examples
    --------
    **Basic bill search by congress and bill number:**
    
    >>> results = search('bill', congress=119, type='hr', number=176)
    >>> print(f"Title: {results.bill.title}")
    >>> print(f"Introduced: {results.bill.introduced_date}")
    
    **Search for all House bills in the 119th Congress:**
    
    >>> results = search('bill', congress=119, type='hr', limit=100)
    >>> for bill in results.bills:
    ...     print(f"{bill.number}: {bill.title}")
    
    **Amendment search with date range filters:**
    
    >>> results = search(
    ...     'amendment',
    ...     congress=118,
    ...     type='hamdt',
    ...     from_date_time='2023-01-01T00:00:00Z',
    ...     to_date_time='2023-12-31T23:59:59Z',
    ...     limit=50
    ... )
    >>> print(f"Found {len(results.amendments)} amendments")
    
    **Search for members by state and party:**
    
    >>> results = search('member', state='CA', party='D', current_member=True)
    >>> for member in results.members:
    ...     print(f"{member.name} - {member.district}")
    
    **Search with custom API client:**
    
    >>> from congressgov._client import AuthenticatedClient
    >>> client = AuthenticatedClient(base_url='https://api.congress.gov/v3', token='your_api_key_here')
    >>> results = search('committee', chamber='senate', client=client)
    
    **Paginated search through all results:**
    
    >>> offset = 0
    >>> limit = 100
    >>> all_bills = []
    >>> while True:
    ...     results = search('bill', congress=119, limit=limit, offset=offset)
    ...     all_bills.extend(results.bills)
    ...     if len(results.bills) < limit:
    ...         break
    ...     offset += limit
    >>> print(f"Retrieved {len(all_bills)} bills total")
    
    **Using as a method (with service/client integration):**
    
    >>> # If integrated into a service class
    >>> service.search('nomination', congress=118, limit=25)
    
    See Also
    --------
    get_registered_types : Get list of all available resource types
    register_search_handler : Register a custom search handler
    _load_search_handler : Internal function that loads handlers lazily
    _normalize_parameters : Internal function that normalizes parameter names
    """
    # --- <LAZY LOAD SEARCH HANDLER> ---
    # NOTE: This is where lazy loading happens - handler is imported only now
    handler = _load_search_handler(resource_type)
    
    # --- <NORMALIZE PARAMETERS> ---
    # Convert user-friendly aliases to canonical parameter names
    normalized_params = _normalize_parameters(resource_type, kwargs)
    
    # --- <DISPATCH TO HANDLER> ---
    # If 'self' is provided, call as a method; otherwise call as a function
    if self is not None:
        logger.debug(f"Calling {resource_type} search handler with context object")
        result = handler(self, **normalized_params)
    else:
        logger.debug(f"Calling {resource_type} search handler as standalone function")
        # NOTE: Pass None as first arg since handlers expect 'self' parameter
        result = handler(None, **normalized_params)

    # --- <ATTACH CLIENT TO RESULT> ---
    # NOTE: The handler already resolved a client to make its API call (or it
    # would have raised); re-resolving here is safe and lets us backfill
    # `.client` on results the handler itself didn't attach it to.
    from congressgov.services.core.api_service import ApiService

    try:
        resolved_client = ApiService._resolve_client(self, normalized_params.get("client"))
    except Exception:
        resolved_client = normalized_params.get("client")

    return _attach_client_to_search_result(result, resolved_client)


# ============================================================================
# REGISTRY MANAGEMENT
# ============================================================================

def register_search_handler(
    resource_type: str,
    module_path: str,
    function_name: str,
    param_aliases: Optional[Dict[str, str]] = None
) -> None:
    """Register a new search handler in the universal search registry.
    
    This function allows you to extend the search system with custom resource types
    without modifying the core search module. Once registered, the new resource type
    can be used with the ``search()`` function just like built-in types.
    
    The handler will be lazily loaded when first accessed, maintaining the performance
    benefits of the lazy loading system.
    
    Parameters
    ----------
    resource_type : str
        Unique identifier for the resource type. This is the string users will pass
        to ``search()`` as the first argument. Use lowercase with hyphens for
        multi-word types (e.g., 'committee-meeting', 'house-communication').
        
        If this resource type is already registered, it will be overwritten with
        the new handler configuration.
        
    module_path : str
        Full Python import path to the module containing the search function.
        Examples:
        
        - ``'congressgov.services.core.search'``
        - ``'my_package.my_module'``
        - ``'extensions.custom_search'``
        
    function_name : str
        Name of the search function within the specified module. The function should
        have a signature compatible with the universal search interface:
        
        .. code-block:: python
        
            def my_search(self, congress=None, limit=20, offset=0, **kwargs):
                # Implementation
                pass
                
    param_aliases : Optional[Dict[str, str]], optional
        Dictionary mapping user-friendly parameter names to the canonical names
        expected by your search function. This enables intuitive parameter names
        for users. Default is None (no aliases).
        
        Example:
        
        .. code-block:: python
        
            param_aliases = {
                'type': 'treaty_type',      # 'type' -> 'treaty_type'
                'number': 'treaty_number',  # 'number' -> 'treaty_number'
            }
            
    Returns
    -------
    None
        This function modifies the registry in-place and returns nothing.
        
    Notes
    -----
    - Registering a new handler clears the LRU cache to ensure consistency
    - Overwrites existing handlers with the same ``resource_type`` name
    - The module is not imported until the handler is first used
    - Thread-safe as long as registration happens before multi-threaded access
    - Use ``unregister_search_handler()`` to remove a handler
    
    Warnings
    --------
    - The module and function must exist and be importable, but this is not
      validated until the handler is first accessed
    - Make sure your search function signature is compatible with the expected
      interface (accepts ``self``, common parameters, and ``**kwargs``)
    
    Examples
    --------
    **Register a custom treaty search handler:**
    
    >>> register_search_handler(
    ...     resource_type='treaty',
    ...     module_path='congressgov.services.treaty',
    ...     function_name='treatysearch',
    ...     param_aliases={'number': 'treaty_number'}
    ... )
    >>> # Now you can use it
    >>> results = search('treaty', congress=118, number=5)
    
    **Register a handler without aliases:**
    
    >>> register_search_handler(
    ...     resource_type='house-requirement',
    ...     module_path='congressgov.services.house_requirement',
    ...     function_name='search_requirements'
    ... )
    
    **Register a handler from a custom extension:**
    
    >>> register_search_handler(
    ...     resource_type='budget-resolution',
    ...     module_path='my_extensions.budget',
    ...     function_name='budget_search',
    ...     param_aliases={'fiscal_year': 'year', 'type': 'resolution_type'}
    ... )
    
    **Overwrite an existing handler:**
    
    >>> # This replaces the built-in bill handler with a custom one
    >>> register_search_handler(
    ...     resource_type='bill',
    ...     module_path='my_custom.bill_search',
    ...     function_name='enhanced_bill_search'
    ... )
    
    See Also
    --------
    unregister_search_handler : Remove a handler from the registry
    get_registered_types : List all registered resource types
    search : Main search function that uses registered handlers
    """
    # --- <CLEAR CACHE FOR THIS RESOURCE TYPE> ---
    # If we're overwriting an existing handler, invalidate its cache
    _load_search_handler.cache_clear()
    
    _SEARCH_REGISTRY[resource_type] = {
        'module': module_path,
        'function': function_name,
        'param_aliases': param_aliases or {}
    }
    
    logger.info(f"Registered search handler for '{resource_type}': {module_path}.{function_name}")


def get_registered_types() -> list[str]:
    """Get a list of all registered resource types available for searching.
    
    Returns a sorted list of all resource type identifiers that have been registered
    with the universal search system. These are the valid values that can be passed
    as the ``resource_type`` parameter to the ``search()`` function.
    
    This function is useful for:
    
    - Discovering what resource types are available
    - Validating user input before calling ``search()``
    - Generating documentation or help text
    - Testing and debugging custom handlers
    
    Returns
    -------
    list[str]
        Sorted list of registered resource type identifiers (e.g., ['amendment', 
        'bill', 'committee', 'member', ...]). The list is sorted alphabetically
        for consistent ordering.
        
    Notes
    -----
    - Returns only registered types; does not validate if handlers are working
    - Includes both built-in and custom registered handlers
    - The returned list is a new list (safe to modify)
    - List is always sorted alphabetically
    
    Examples
    --------
    **Display all available resource types:**
    
    >>> types = get_registered_types()
    >>> print("Available resource types:")
    >>> for t in types:
    ...     print(f"  - {t}")
    Available resource types:
      - amendment
      - bill
      - committee
      - committee-meeting
      - committee-print
      - committee-report
      - congress
      - hearing
      - house-communication
      - member
      - nomination
      - senate-communication
      - summary
      - treaty
    
    **Validate user input:**
    
    >>> user_input = 'bill'
    >>> if user_input in get_registered_types():
    ...     results = search(user_input, congress=119)
    ... else:
    ...     print(f"Unknown resource type: {user_input}")
    
    **Count available handlers:**
    
    >>> num_types = len(get_registered_types())
    >>> print(f"{num_types} resource types available")
    
    **Check if a custom handler is registered:**
    
    >>> if 'custom-resource' in get_registered_types():
    ...     print("Custom handler is available")
    ... else:
    ...     print("Custom handler not found")
    
    See Also
    --------
    search : Main search function that uses these resource types
    register_search_handler : Register a new resource type
    unregister_search_handler : Remove a resource type
    """
    return sorted(_SEARCH_REGISTRY.keys())


def unregister_search_handler(resource_type: str) -> None:
    """Remove a search handler from the universal search registry.
    
    This function removes a previously registered search handler, making that
    resource type unavailable for searching. This is useful for:
    
    - Removing custom handlers that are no longer needed
    - Cleaning up test handlers after testing
    - Temporarily disabling certain resource types
    - Reclaiming memory by clearing the handler cache
    
    After unregistering, any attempts to search for that resource type will
    raise a ``ValueError`` until it is registered again.
    
    Parameters
    ----------
    resource_type : str
        The resource type identifier to remove from the registry. Must be an
        exact match (case-sensitive) to a currently registered type.
        
    Returns
    -------
    None
        This function modifies the registry in-place and returns nothing.
        
    Raises
    ------
    KeyError
        If the specified ``resource_type`` is not currently registered in the
        search system. Use ``get_registered_types()`` to check what types are
        available.
        
    Notes
    -----
    - Clears the LRU cache to free memory and ensure consistency
    - Cannot unregister a type that isn't registered (raises KeyError)
    - After unregistering, the type can be re-registered with different settings
    - Logging at INFO level tracks unregistration operations
    - Thread-safe as long as unregistration happens before multi-threaded access
    
    Warnings
    --------
    - Be careful when unregistering built-in resource types, as this will break
      code that depends on them
    - Unregistering clears the entire handler cache, not just the specific handler
    
    Examples
    --------
    **Remove a custom handler:**
    
    >>> register_search_handler('custom', 'my_module.custom', 'custom_search')
    >>> # Use it...
    >>> results = search('custom', param1='value')
    >>> # Clean up when done
    >>> unregister_search_handler('custom')
    >>> # Now 'custom' is no longer available
    
    **Temporarily disable a resource type:**
    
    >>> # Save the configuration first
    >>> bill_config = _SEARCH_REGISTRY['bill'].copy()
    >>> unregister_search_handler('bill')
    >>> # Bill searches are now disabled
    >>> # Later, restore it
    >>> register_search_handler('bill', **bill_config)
    
    **Clean up test handlers:**
    
    >>> def cleanup_test_handlers():
    ...     test_types = ['test-resource-1', 'test-resource-2']
    ...     for t in test_types:
    ...         if t in get_registered_types():
    ...             unregister_search_handler(t)
    
    **Handle unregistration errors:**
    
    >>> try:
    ...     unregister_search_handler('nonexistent-type')
    ... except KeyError as e:
    ...     print(f"Handler not found: {e}")
    Handler not found: Resource type 'nonexistent-type' is not registered
    
    **Verify unregistration:**
    
    >>> resource_type = 'my-custom-type'
    >>> if resource_type in get_registered_types():
    ...     unregister_search_handler(resource_type)
    ...     print(f"Successfully unregistered {resource_type}")
    ... else:
    ...     print(f"{resource_type} was not registered")
    
    See Also
    --------
    register_search_handler : Register a new search handler
    get_registered_types : List all registered resource types
    search : Main search function affected by registration changes
    """
    if resource_type not in _SEARCH_REGISTRY:
        raise KeyError(f"Resource type '{resource_type}' is not registered")
    
    # --- <CLEAR CACHE AND REMOVE FROM REGISTRY> ---
    _load_search_handler.cache_clear()
    del _SEARCH_REGISTRY[resource_type]
    
    logger.info(f"Unregistered search handler for '{resource_type}'")


# ============================================================================
# PUBLIC API EXPORTS
# ============================================================================
# These are the symbols available when using "from congressgov.services.core.search import *"
# and are what IDEs will show in autocomplete for this module.

# ============================================================================
# SEARCH HANDLER IMPLEMENTATIONS
# ============================================================================
# These handlers are loaded lazily by the universal search system.
# Each handler follows the same pattern: resolve client, route to appropriate
# endpoint based on parameters, and return validated model.


def billsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    bill_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for bills using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        bill_type (str, optional): Bill type to filter by (e.g., 'hr', 's').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Bills: Parsed Bills model from API response.
    """
    # --- <LAZY IMPORT: Only load bill endpoints when actually needed> ---
    from congressgov._client.api.bill import (
        bill_list_all_sync,
        bill_list_by_congress_sync,
        bill_list_by_type_sync
    )
    
    # --- <LAZY LOAD MODEL> ---
    from congressgov.services.core.api_service import ApiService
    BillsModel = ModelRegistry.get_model("Bills")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_bill_format import GetBillFormat
    from congressgov._client.models.get_bill_congress_format import GetBillCongressFormat
    from congressgov._client.models.get_bill_congress_bill_type_format import (
        GetBillCongressBillTypeFormat,
    )

    if sort is not None:
        raise ValueError(
            "sort is not supported for bill list search; "
            "Congress.gov bill list endpoints are fixed to latest-action order"
        )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        if bill_type is not None:
            resp = bill_list_by_type_sync(
                client=resolved_client,
                congress=congress,
                bill_type=bill_type,
                format_=resolve_response_format(format_, GetBillCongressBillTypeFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
            )
        else:
            resp = bill_list_by_congress_sync(
                client=resolved_client,
                congress=congress,
                format_=resolve_response_format(format_, GetBillCongressFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
            )
    else:
        resp = bill_list_all_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetBillFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
        )
    
    from congressgov.models.base.model import ApiEnvelope
    import json
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return BillsModel.model_validate(api_env.data)


def amendmentsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    amendment_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for amendments using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        amendment_type (str, optional): Amendment type to filter by (e.g., 'hamdt', 'samdt').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Amendments: Parsed Amendments model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.amendments import (
        amendment_list_sync,
        amendment_congress_sync,
        amendment_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    AmendmentsModel = ModelRegistry.get_model("Amendments")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_amendment_format import GetAmendmentFormat
    from congressgov._client.models.get_amendment_congress_format import GetAmendmentCongressFormat
    from congressgov._client.models.get_amendment_congress_amendment_type_format import (
        GetAmendmentCongressAmendmentTypeFormat,
    )

    if amendment_type is not None and congress is None:
        raise ValueError(
            "amendment_type requires congress "
            "(e.g. search(congress=118, amendment_type='hamdt'))"
        )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        if amendment_type is not None:
            resp = amendment_list_sync(
                client=resolved_client,
                congress=congress,
                amendment_type=amendment_type,
                format_=resolve_response_format(
                    format_, GetAmendmentCongressAmendmentTypeFormat
                ),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time
            )
        else:
            resp = amendment_congress_sync(
                client=resolved_client,
                congress=congress,
                format_=resolve_response_format(format_, GetAmendmentCongressFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time
            )
    else:
        resp = amendment_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetAmendmentFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return AmendmentsModel.model_validate(api_env.data)


def membersearch(
    self,
    *,
    client: Any = None,
    state: str = None,
    district: int = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    current_member: str = None
):
    """
    Search for members using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        state (str, optional): State abbreviation to filter by (e.g., 'CA', 'NY').
        district (int, optional): District number to filter by.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        current_member (str, optional): Filter for current members ("true" or "false").

    Returns:
        Members: Parsed Members model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.member import (
        member_list_sync,
        member_list_by_state_sync,
        member_list_by_state_and_district_sync,
        member_list_by_congress_state_district_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    MembersModel = ModelRegistry.get_model("Members")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and state is not None and district is not None:
        resp = member_list_by_congress_state_district_sync(
            client=resolved_client,
            congress=congress,
            state_code=state,
            district=district,
            format_=format_,
            limit=limit
        )
    elif state is not None and district is not None:
        resp = member_list_by_state_and_district_sync(
            client=resolved_client,
            state_code=state,
            district=district,
            format_=format_,
            current_member=current_member
        )
    elif state is not None:
        resp = member_list_by_state_sync(
            client=resolved_client,
            state_code=state,
            format_=format_,
            limit=limit,
            current_member=current_member
        )
    else:
        resp = member_list_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            current_member=current_member
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return MembersModel.model_validate(api_env.data)


def committeesearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for committees using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate', 'joint').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Committees: Parsed Committees model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee import (
        committee_list_sync,
        committee_list_by_chamber_sync,
        committee_list_by_congress_sync,
        committee_list_by_congress_chamber_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteesModel = ModelRegistry.get_model("Committees")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_committee_chamber_chamber import GetCommitteeChamberChamber
    from congressgov._client.models.get_committee_chamber_format import GetCommitteeChamberFormat
    from congressgov._client.models.get_committee_congress_chamber_chamber import (
        GetCommitteeCongressChamberChamber,
    )
    from congressgov._client.models.get_committee_congress_chamber_format import (
        GetCommitteeCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_congress_format import GetCommitteeCongressFormat
    from congressgov._client.models.get_committee_format import GetCommitteeFormat

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        chamber_param = (
            GetCommitteeCongressChamberChamber(chamber.lower())
            if isinstance(chamber, str)
            else chamber
        )
        resp = committee_list_by_congress_chamber_sync(
            client=resolved_client,
            congress=congress,
            chamber=chamber_param,
            format_=resolve_response_format(format_, GetCommitteeCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = committee_list_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteeCongressFormat),
            offset=offset,
            limit=limit
        )
    elif chamber is not None:
        chamber_param = (
            GetCommitteeChamberChamber(chamber.lower())
            if isinstance(chamber, str)
            else chamber
        )
        resp = committee_list_by_chamber_sync(
            client=resolved_client,
            chamber=chamber_param,
            format_=resolve_response_format(format_, GetCommitteeChamberFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = committee_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteeFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteesModel.model_validate(api_env.data)


def nominationsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for nominations using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Nominations: Parsed Nominations model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.nomination import (
        nomination_list_sync,
        nomination_list_by_congress_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    NominationsModel = ModelRegistry.get_model("Nominations")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        resp = nomination_list_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    else:
        resp = nomination_list_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return NominationsModel.model_validate(api_env.data)


def treatysearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for treaties using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Treaties: Parsed Treaties model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.treaty import (
        treaty_list_sync,
        treaty_list_by_congress_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    TreatiesModel = ModelRegistry.get_model("Treaties")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_treaty_format import GetTreatyFormat
    from congressgov._client.models.get_treaty_congress_format import GetTreatyCongressFormat

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        resp = treaty_list_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetTreatyCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = treaty_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetTreatyFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return TreatiesModel.model_validate(api_env.data)


def hearingsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    sort: str = None
):
    """
    Search for hearings using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Hearings: Parsed Hearings model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.hearing import (
        hearing_list_sync,
        hearing_list_by_congress_sync,
        hearing_list_by_congress_chamber_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    HearingsModel = ModelRegistry.get_model("Hearings")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_hearing_format import GetHearingFormat
    from congressgov._client.models.get_hearing_congress_format import GetHearingCongressFormat
    from congressgov._client.models.get_hearing_congress_chamber_format import (
        GetHearingCongressChamberFormat,
    )
    from congressgov._client.models.get_hearing_congress_chamber_chamber import (
        GetHearingCongressChamberChamber,
    )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = hearing_list_by_congress_chamber_sync(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetHearingCongressChamberChamber),
            format_=resolve_response_format(format_, GetHearingCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = hearing_list_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetHearingCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = hearing_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetHearingFormat),
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HearingsModel.model_validate(api_env.data)


def committeemeetingsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for committee meetings using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        CommitteeMeetings: Parsed CommitteeMeetings model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_meeting import (
        committee_meeting_list_sync,
        committee_meeting_congress_sync,
        committee_meeting_congress_chamber_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteeMeetingsModel = ModelRegistry.get_model("CommitteeMeetings")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_committee_meeting_congress_chamber_chamber import (
        GetCommitteeMeetingCongressChamberChamber,
    )
    from congressgov._client.models.get_committee_meeting_congress_chamber_format import (
        GetCommitteeMeetingCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_meeting_congress_format import (
        GetCommitteeMeetingCongressFormat,
    )
    from congressgov._client.models.get_committee_meeting_format import GetCommitteeMeetingFormat
    from congressgov.services.exceptions import APIError

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = committee_meeting_congress_chamber_sync(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetCommitteeMeetingCongressChamberChamber),
            format_=resolve_response_format(format_, GetCommitteeMeetingCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = committee_meeting_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteeMeetingCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = committee_meeting_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteeMeetingFormat),
            offset=offset,
            limit=limit
        )

    if resp.status_code != 200:
        raise APIError(
            f"Committee meeting search failed with HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_body=resp.content.decode(errors="replace")[:500],
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    if isinstance(api_env.data, str):
        raise APIError(
            "Committee meeting API returned an error message instead of meeting data",
            response_body=api_env.data[:500],
        )
    return CommitteeMeetingsModel.model_validate(api_env.data)


def committeereportsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    report_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None
):
    """
    Search for committee reports using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        report_type (str, optional): Report type to filter by ('hrpt', 'srpt', 'erpt').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        CommitteeReports: Parsed CommitteeReports model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_report import (
        committee_reports_sync,
        committee_reports_by_congress_sync,
        committee_reports_by_congress_rpt_type_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteeReportsModel = ModelRegistry.get_model("CommitteeReports")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and report_type is not None:
        resp = committee_reports_by_congress_rpt_type_sync(
            client=resolved_client,
            congress=congress,
            report_type=report_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = committee_reports_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    else:
        resp = committee_reports_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteeReportsModel.model_validate(api_env.data)


def committeeprintsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for committee prints using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate', 'joint').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        CommitteePrints: Parsed CommitteePrints model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_print import (
        committee_print_list_sync,
        committee_prints_by_congress_sync,
        committee_prints_by_congress_chamber_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteePrintsModel = ModelRegistry.get_model("CommitteePrints")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_committee_print_format import GetCommitteePrintFormat
    from congressgov._client.models.get_committee_print_congress_format import (
        GetCommitteePrintCongressFormat,
    )
    from congressgov._client.models.get_committee_print_congress_chamber_format import (
        GetCommitteePrintCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_print_congress_chamber_chamber import (
        GetCommitteePrintCongressChamberChamber,
    )
    from congressgov.services.exceptions import APIError

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = committee_prints_by_congress_chamber_sync(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetCommitteePrintCongressChamberChamber),
            format_=resolve_response_format(format_, GetCommitteePrintCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = committee_prints_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteePrintCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = committee_print_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteePrintFormat),
            offset=offset,
            limit=limit
        )

    if resp.status_code != 200:
        raise APIError(
            f"Committee print search failed with HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_body=resp.content.decode(errors="replace")[:500],
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    if isinstance(api_env.data, str):
        raise APIError(
            "Committee print API returned an error message instead of print data",
            response_body=api_env.data[:500],
        )
    return CommitteePrintsModel.model_validate(api_env.data)


def housecommunicationsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    communication_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for house communications using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        HouseCommunications: Parsed HouseCommunications model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.house_communication import (
        house_communication_sync,
        house_communication_congress_sync,
        house_communication_list_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    HouseCommunicationsModel = ModelRegistry.get_model("HouseCommunications")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    # NOTE: Route to the correct endpoint based on which parameters are provided:
    # - Both congress AND communication_type → house_communication_list_sync
    # - Only congress → house_communication_congress_sync
    # - Neither → house_communication_sync
    if congress is not None and communication_type is not None:
        resp = house_communication_list_sync(
            client=resolved_client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = house_communication_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = house_communication_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseCommunicationsModel.model_validate(api_env.data)


def senatecommunicationsearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    communication_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for senate communications using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        communication_type (str, optional): Communication type to filter by (e.g., 'ec', 'pm', 'pom').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        SenateCommunications: Parsed SenateCommunications model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.senate_communication import (
        senate_communication_sync,
        senate_communication_congress_sync,
        senate_communication_list_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    SenateCommunicationsModel = ModelRegistry.get_model("SenateCommunications")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    # NOTE: Route to the correct endpoint based on which parameters are provided:
    # - Both congress AND communication_type → senate_communication_list_sync
    # - Only congress → senate_communication_congress_sync
    # - Neither → senate_communication_sync
    if congress is not None and communication_type is not None:
        resp = senate_communication_list_sync(
            client=resolved_client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = senate_communication_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = senate_communication_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return SenateCommunicationsModel.model_validate(api_env.data)


def congresssearch(
    self,
    *,
    client: Any = None,
    current: bool = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for congresses using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        current (bool, optional): If True, only return current congress.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        Congresses: Parsed Congresses model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.congress import (
        congress_list_sync,
        congress_current_list_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CongressesModel = ModelRegistry.get_model("Congresses")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if current:
        resp = congress_current_list_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = congress_list_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CongressesModel.model_validate(api_env.data)


def boundcongressionalrecordsearch(
    self,
    *,
    client: Any = None,
    year: int = None,
    month: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search bound congressional records by year and optional month."""
    from congressgov._client.api.bound_congressional_record import (
        bound_congressional_record_list_sync,
        bound_congressional_record_list_by_year_sync,
        bound_congressional_record_list_by_year_and_month_sync,
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    BoundCongressionalRecordsModel = ModelRegistry.get_model("BoundCongressionalRecords")
    resolved_client = ApiService._resolve_client(self, client)

    if year is not None and month is not None:
        resp = bound_congressional_record_list_by_year_and_month_sync(
            client=resolved_client,
            year=str(year),
            month=str(month),
            format_=format_,
            offset=offset,
            limit=limit,
        )
    elif year is not None:
        resp = bound_congressional_record_list_by_year_sync(
            client=resolved_client,
            year=str(year),
            format_=format_,
            offset=offset,
            limit=limit,
        )
    else:
        resp = bound_congressional_record_list_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return BoundCongressionalRecordsModel.model_validate(api_env.data)


def congressionalrecordsearch(
    self,
    *,
    client: Any = None,
    y: int = None,
    m: int = None,
    d: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search daily congressional record issues by date filters."""
    from congressgov._client.api.congressional_record import (
        congressional_record_list_sync,
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    DailyCongressionalRecordModel = ModelRegistry.get_model("DailyCongressionalRecord")
    resolved_client = ApiService._resolve_client(self, client)

    resp = congressional_record_list_sync(
        client=resolved_client,
        format_=format_,
        y=y,
        m=m,
        d=d,
        offset=offset,
        limit=limit,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return DailyCongressionalRecordModel.model_validate(api_env.data)


def crsreportsearch(
    self,
    *,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
):
    """Search CRS reports."""
    from congressgov._client.api.crsreport import crsreport_sync
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    CRSReportsModel = ModelRegistry.get_model("CRSReports")
    resolved_client = ApiService._resolve_client(self, client)

    resp = crsreport_sync(
        client=resolved_client,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CRSReportsModel.model_validate(api_env.data)


def houserequirementsearch(
    self,
    *,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search House requirements."""
    from congressgov._client.api.house_requirement import house_requirement_sync
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    HouseRequirementsModel = ModelRegistry.get_model("HouseRequirements")
    resolved_client = ApiService._resolve_client(self, client)

    resp = house_requirement_sync(
        client=resolved_client,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseRequirementsModel.model_validate(api_env.data)


def housevotesearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search House roll call votes."""
    from congressgov._client.api.house_vote import (
        house_vote_list_sync,
        house_vote_list_congress_sync,
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    HouseVotesModel = ModelRegistry.get_model("HouseVotes")
    resolved_client = ApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_house_vote_format import GetHouseVoteFormat
    from congressgov._client.models.get_house_vote_congress_format import (
        GetHouseVoteCongressFormat,
    )

    if congress is not None:
        resp = house_vote_list_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetHouseVoteCongressFormat),
            offset=offset,
            limit=limit,
        )
    else:
        resp = house_vote_list_sync(
            client=resolved_client,
            format_=resolve_response_format(format_, GetHouseVoteFormat),
            offset=offset,
            limit=limit,
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseVotesModel.model_validate(api_env.data)


def summariessearch(
    self,
    *,
    client: Any = None,
    congress: int = None,
    bill_type: str = None,
    format_: str = 'json',  # ✅ Default to 'json' format
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for bill summaries using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        bill_type (str, optional): Bill type to filter by (e.g., 'hr', 's').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Summaries: Parsed Summaries model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.summaries import (
        bill_summaries_all_sync,
        bill_summaries_by_congress_sync,
        bill_summaries_by_type_sync
    )
    from congressgov.services.core.api_service import ApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    SummariesModel = ModelRegistry.get_model("Summaries")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = ApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and bill_type is not None:
        resp = bill_summaries_by_type_sync(
            client=resolved_client,
            congress=congress,
            bill_type=bill_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = bill_summaries_by_congress_sync(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )
    else:
        resp = bill_summaries_all_sync(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )
    
    # --- <ERROR HANDLING> ---
    # Check if response is successful before parsing
    if resp.status_code != 200:
        error_msg = f"API returned status code {resp.status_code}"
        try:
            error_content = resp.content.decode('utf-8')
            if error_content:
                error_msg += f": {error_content}"
        except Exception:
            pass
        raise ValueError(error_msg)
    
    # --- <PARSE RESPONSE> ---
    # Ensure response content is not empty before parsing JSON
    if not resp.content:
        raise ValueError("API returned empty response")
    
    try:
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        return SummariesModel.model_validate(api_env.data)
    except json.JSONDecodeError as e:
        # Provide helpful error message with response preview
        content_preview = resp.content[:500].decode('utf-8', errors='replace')
        raise ValueError(f"Failed to parse API response as JSON: {e}. Response content: {content_preview}")


# ============================================================================
# PUBLIC API EXPORTS
# ============================================================================
# These are the symbols available when using "from congressgov.services.core.search import *"
# and are what IDEs will show in autocomplete for this module.

__all__ = [
    # Main search interface
    'search',
    
    # Registry management functions
    'register_search_handler',
    'unregister_search_handler',
    'get_registered_types',
    
    # Type definitions for type hints
    'HandlerConfig',
    'ResourceType',
]

# ============================================================================
# ASYNC SEARCH HANDLERS (auto-generated)
async def billsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    bill_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for bills using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        bill_type (str, optional): Bill type to filter by (e.g., 'hr', 's').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Bills: Parsed Bills model from API response.
    """
    # --- <LAZY IMPORT: Only load bill endpoints when actually needed> ---
    from congressgov._client.api.bill import (
        bill_list_all_async,
        bill_list_by_congress_async,
        bill_list_by_type_async
    )
    
    # --- <LAZY LOAD MODEL> ---
    from congressgov.services.core.async_api_service import AsyncApiService
    BillsModel = ModelRegistry.get_model("Bills")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_bill_format import GetBillFormat
    from congressgov._client.models.get_bill_congress_format import GetBillCongressFormat
    from congressgov._client.models.get_bill_congress_bill_type_format import (
        GetBillCongressBillTypeFormat,
    )

    if sort is not None:
        raise ValueError(
            "sort is not supported for bill list search; "
            "Congress.gov bill list endpoints are fixed to latest-action order"
        )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        if bill_type is not None:
            resp = await bill_list_by_type_async(
                client=resolved_client,
                congress=congress,
                bill_type=bill_type,
                format_=resolve_response_format(format_, GetBillCongressBillTypeFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
            )
        else:
            resp = await bill_list_by_congress_async(
                client=resolved_client,
                congress=congress,
                format_=resolve_response_format(format_, GetBillCongressFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
            )
    else:
        resp = await bill_list_all_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetBillFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
        )
    
    from congressgov.models.base.model import ApiEnvelope
    import json
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return BillsModel.model_validate(api_env.data)




async def amendmentsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    amendment_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for amendments using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        amendment_type (str, optional): Amendment type to filter by (e.g., 'hamdt', 'samdt').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Amendments: Parsed Amendments model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.amendments import (
        amendment_list_async,
        amendment_congress_async,
        amendment_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    AmendmentsModel = ModelRegistry.get_model("Amendments")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_amendment_format import GetAmendmentFormat
    from congressgov._client.models.get_amendment_congress_format import GetAmendmentCongressFormat
    from congressgov._client.models.get_amendment_congress_amendment_type_format import (
        GetAmendmentCongressAmendmentTypeFormat,
    )

    if amendment_type is not None and congress is None:
        raise ValueError(
            "amendment_type requires congress "
            "(e.g. search(congress=118, amendment_type='hamdt'))"
        )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        if amendment_type is not None:
            resp = await amendment_list_async(
                client=resolved_client,
                congress=congress,
                amendment_type=amendment_type,
                format_=resolve_response_format(
                    format_, GetAmendmentCongressAmendmentTypeFormat
                ),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time
            )
        else:
            resp = await amendment_congress_async(
                client=resolved_client,
                congress=congress,
                format_=resolve_response_format(format_, GetAmendmentCongressFormat),
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time
            )
    else:
        resp = await amendment_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetAmendmentFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return AmendmentsModel.model_validate(api_env.data)




async def membersearch_async(
    self,
    *,
    client: Any = None,
    state: str = None,
    district: int = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    current_member: str = None
):
    """
    Search for members using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        state (str, optional): State abbreviation to filter by (e.g., 'CA', 'NY').
        district (int, optional): District number to filter by.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        current_member (str, optional): Filter for current members ("true" or "false").

    Returns:
        Members: Parsed Members model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.member import (
        member_list_async,
        member_list_by_state_async,
        member_list_by_state_and_district_async,
        member_list_by_congress_state_district_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    MembersModel = ModelRegistry.get_model("Members")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and state is not None and district is not None:
        resp = await member_list_by_congress_state_district_async(
            client=resolved_client,
            congress=congress,
            state_code=state,
            district=district,
            format_=format_,
            limit=limit
        )
    elif state is not None and district is not None:
        resp = await member_list_by_state_and_district_async(
            client=resolved_client,
            state_code=state,
            district=district,
            format_=format_,
            current_member=current_member
        )
    elif state is not None:
        resp = await member_list_by_state_async(
            client=resolved_client,
            state_code=state,
            format_=format_,
            limit=limit,
            current_member=current_member
        )
    else:
        resp = await member_list_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            current_member=current_member
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return MembersModel.model_validate(api_env.data)




async def committeesearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for committees using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate', 'joint').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Committees: Parsed Committees model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee import (
        committee_list_async,
        committee_list_by_chamber_async,
        committee_list_by_congress_async,
        committee_list_by_congress_chamber_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteesModel = ModelRegistry.get_model("Committees")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_committee_chamber_chamber import GetCommitteeChamberChamber
    from congressgov._client.models.get_committee_chamber_format import GetCommitteeChamberFormat
    from congressgov._client.models.get_committee_congress_chamber_chamber import (
        GetCommitteeCongressChamberChamber,
    )
    from congressgov._client.models.get_committee_congress_chamber_format import (
        GetCommitteeCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_congress_format import GetCommitteeCongressFormat
    from congressgov._client.models.get_committee_format import GetCommitteeFormat

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        chamber_param = (
            GetCommitteeCongressChamberChamber(chamber.lower())
            if isinstance(chamber, str)
            else chamber
        )
        resp = await committee_list_by_congress_chamber_async(
            client=resolved_client,
            congress=congress,
            chamber=chamber_param,
            format_=resolve_response_format(format_, GetCommitteeCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await committee_list_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteeCongressFormat),
            offset=offset,
            limit=limit
        )
    elif chamber is not None:
        chamber_param = (
            GetCommitteeChamberChamber(chamber.lower())
            if isinstance(chamber, str)
            else chamber
        )
        resp = await committee_list_by_chamber_async(
            client=resolved_client,
            chamber=chamber_param,
            format_=resolve_response_format(format_, GetCommitteeChamberFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = await committee_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteeFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteesModel.model_validate(api_env.data)




async def nominationsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for nominations using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Nominations: Parsed Nominations model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.nomination import (
        nomination_list_async,
        nomination_list_by_congress_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    NominationsModel = ModelRegistry.get_model("Nominations")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        resp = await nomination_list_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    else:
        resp = await nomination_list_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return NominationsModel.model_validate(api_env.data)




async def treatysearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for treaties using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Treaties: Parsed Treaties model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.treaty import (
        treaty_list_async,
        treaty_list_by_congress_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    TreatiesModel = ModelRegistry.get_model("Treaties")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_treaty_format import GetTreatyFormat
    from congressgov._client.models.get_treaty_congress_format import GetTreatyCongressFormat

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None:
        resp = await treaty_list_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetTreatyCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = await treaty_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetTreatyFormat),
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return TreatiesModel.model_validate(api_env.data)




async def hearingsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    sort: str = None
):
    """
    Search for hearings using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Hearings: Parsed Hearings model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.hearing import (
        hearing_list_async,
        hearing_list_by_congress_async,
        hearing_list_by_congress_chamber_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    HearingsModel = ModelRegistry.get_model("Hearings")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_hearing_format import GetHearingFormat
    from congressgov._client.models.get_hearing_congress_format import GetHearingCongressFormat
    from congressgov._client.models.get_hearing_congress_chamber_format import (
        GetHearingCongressChamberFormat,
    )
    from congressgov._client.models.get_hearing_congress_chamber_chamber import (
        GetHearingCongressChamberChamber,
    )

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = await hearing_list_by_congress_chamber_async(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetHearingCongressChamberChamber),
            format_=resolve_response_format(format_, GetHearingCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await hearing_list_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetHearingCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = await hearing_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetHearingFormat),
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HearingsModel.model_validate(api_env.data)




async def committeemeetingsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for committee meetings using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        CommitteeMeetings: Parsed CommitteeMeetings model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_meeting import (
        committee_meeting_list_async,
        committee_meeting_congress_async,
        committee_meeting_congress_chamber_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteeMeetingsModel = ModelRegistry.get_model("CommitteeMeetings")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_committee_meeting_congress_chamber_chamber import (
        GetCommitteeMeetingCongressChamberChamber,
    )
    from congressgov._client.models.get_committee_meeting_congress_chamber_format import (
        GetCommitteeMeetingCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_meeting_congress_format import (
        GetCommitteeMeetingCongressFormat,
    )
    from congressgov._client.models.get_committee_meeting_format import GetCommitteeMeetingFormat
    from congressgov.services.exceptions import APIError

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = await committee_meeting_congress_chamber_async(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetCommitteeMeetingCongressChamberChamber),
            format_=resolve_response_format(format_, GetCommitteeMeetingCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await committee_meeting_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteeMeetingCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = await committee_meeting_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteeMeetingFormat),
            offset=offset,
            limit=limit
        )

    if resp.status_code != 200:
        raise APIError(
            f"Committee meeting search failed with HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_body=resp.content.decode(errors="replace")[:500],
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    if isinstance(api_env.data, str):
        raise APIError(
            "Committee meeting API returned an error message instead of meeting data",
            response_body=api_env.data[:500],
        )
    return CommitteeMeetingsModel.model_validate(api_env.data)




async def committeereportsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    report_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None
):
    """
    Search for committee reports using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        report_type (str, optional): Report type to filter by ('hrpt', 'srpt', 'erpt').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        CommitteeReports: Parsed CommitteeReports model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_report import (
        committee_reports_async,
        committee_reports_by_congress_async,
        committee_reports_by_congress_rpt_type_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteeReportsModel = ModelRegistry.get_model("CommitteeReports")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and report_type is not None:
        resp = await committee_reports_by_congress_rpt_type_async(
            client=resolved_client,
            congress=congress,
            report_type=report_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await committee_reports_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    else:
        resp = await committee_reports_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteeReportsModel.model_validate(api_env.data)




async def committeeprintsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    chamber: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for committee prints using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        chamber (str, optional): Chamber to filter by ('house', 'senate', 'joint').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        CommitteePrints: Parsed CommitteePrints model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.committee_print import (
        committee_print_list_async,
        committee_prints_by_congress_async,
        committee_prints_by_congress_chamber_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CommitteePrintsModel = ModelRegistry.get_model("CommitteePrints")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_chamber, resolve_response_format
    from congressgov._client.models.get_committee_print_format import GetCommitteePrintFormat
    from congressgov._client.models.get_committee_print_congress_format import (
        GetCommitteePrintCongressFormat,
    )
    from congressgov._client.models.get_committee_print_congress_chamber_format import (
        GetCommitteePrintCongressChamberFormat,
    )
    from congressgov._client.models.get_committee_print_congress_chamber_chamber import (
        GetCommitteePrintCongressChamberChamber,
    )
    from congressgov.services.exceptions import APIError

    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and chamber is not None:
        resp = await committee_prints_by_congress_chamber_async(
            client=resolved_client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetCommitteePrintCongressChamberChamber),
            format_=resolve_response_format(format_, GetCommitteePrintCongressChamberFormat),
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await committee_prints_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCommitteePrintCongressFormat),
            offset=offset,
            limit=limit
        )
    else:
        resp = await committee_print_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCommitteePrintFormat),
            offset=offset,
            limit=limit
        )

    if resp.status_code != 200:
        raise APIError(
            f"Committee print search failed with HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_body=resp.content.decode(errors="replace")[:500],
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    if isinstance(api_env.data, str):
        raise APIError(
            "Committee print API returned an error message instead of print data",
            response_body=api_env.data[:500],
        )
    return CommitteePrintsModel.model_validate(api_env.data)


async def housecommunicationsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    communication_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for house communications using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        HouseCommunications: Parsed HouseCommunications model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.house_communication import (
        house_communication_async,
        house_communication_congress_async,
        house_communication_list_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    HouseCommunicationsModel = ModelRegistry.get_model("HouseCommunications")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    # NOTE: Route to the correct endpoint based on which parameters are provided:
    # - Both congress AND communication_type → house_communication_list_async
    # - Only congress → house_communication_congress_async
    # - Neither → house_communication_async
    if congress is not None and communication_type is not None:
        resp = await house_communication_list_async(
            client=resolved_client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await house_communication_congress_async(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = await house_communication_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseCommunicationsModel.model_validate(api_env.data)




async def senatecommunicationsearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    communication_type: str = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for senate communications using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        communication_type (str, optional): Communication type to filter by (e.g., 'ec', 'pm', 'pom').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        SenateCommunications: Parsed SenateCommunications model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.senate_communication import (
        senate_communication_async,
        senate_communication_congress_async,
        senate_communication_list_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    SenateCommunicationsModel = ModelRegistry.get_model("SenateCommunications")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    # NOTE: Route to the correct endpoint based on which parameters are provided:
    # - Both congress AND communication_type → senate_communication_list_async
    # - Only congress → senate_communication_congress_async
    # - Neither → senate_communication_async
    if congress is not None and communication_type is not None:
        resp = await senate_communication_list_async(
            client=resolved_client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await senate_communication_congress_async(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = await senate_communication_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return SenateCommunicationsModel.model_validate(api_env.data)




async def congresssearch_async(
    self,
    *,
    client: Any = None,
    current: bool = None,
    format_: str = None,
    offset: int = None,
    limit: int = None
):
    """
    Search for congresses using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        current (bool, optional): If True, only return current congress.
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.

    Returns:
        Congresses: Parsed Congresses model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.congress import (
        congress_list_async,
        congress_current_list_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    CongressesModel = ModelRegistry.get_model("Congresses")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if current:
        resp = await congress_current_list_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    else:
        resp = await congress_list_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit
        )
    
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CongressesModel.model_validate(api_env.data)




async def boundcongressionalrecordsearch_async(
    self,
    *,
    client: Any = None,
    year: int = None,
    month: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search bound congressional records by year and optional month."""
    from congressgov._client.api.bound_congressional_record import (
        bound_congressional_record_list_async,
        bound_congressional_record_list_by_year_async,
        bound_congressional_record_list_by_year_and_month_async,
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    BoundCongressionalRecordsModel = ModelRegistry.get_model("BoundCongressionalRecords")
    resolved_client = await AsyncApiService._resolve_client(self, client)

    if year is not None and month is not None:
        resp = await bound_congressional_record_list_by_year_and_month_async(
            client=resolved_client,
            year=str(year),
            month=str(month),
            format_=format_,
            offset=offset,
            limit=limit,
        )
    elif year is not None:
        resp = await bound_congressional_record_list_by_year_async(
            client=resolved_client,
            year=str(year),
            format_=format_,
            offset=offset,
            limit=limit,
        )
    else:
        resp = await bound_congressional_record_list_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return BoundCongressionalRecordsModel.model_validate(api_env.data)




async def congressionalrecordsearch_async(
    self,
    *,
    client: Any = None,
    y: int = None,
    m: int = None,
    d: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search daily congressional record issues by date filters."""
    from congressgov._client.api.congressional_record import (
        congressional_record_list_async,
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    DailyCongressionalRecordModel = ModelRegistry.get_model("DailyCongressionalRecord")
    resolved_client = await AsyncApiService._resolve_client(self, client)

    resp = await congressional_record_list_async(
        client=resolved_client,
        format_=format_,
        y=y,
        m=m,
        d=d,
        offset=offset,
        limit=limit,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return DailyCongressionalRecordModel.model_validate(api_env.data)




async def crsreportsearch_async(
    self,
    *,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
):
    """Search CRS reports."""
    from congressgov._client.api.crsreport import crsreport_async
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    CRSReportsModel = ModelRegistry.get_model("CRSReports")
    resolved_client = await AsyncApiService._resolve_client(self, client)

    resp = await crsreport_async(
        client=resolved_client,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CRSReportsModel.model_validate(api_env.data)




async def houserequirementsearch_async(
    self,
    *,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search House requirements."""
    from congressgov._client.api.house_requirement import house_requirement_async
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    HouseRequirementsModel = ModelRegistry.get_model("HouseRequirements")
    resolved_client = await AsyncApiService._resolve_client(self, client)

    resp = await house_requirement_async(
        client=resolved_client,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseRequirementsModel.model_validate(api_env.data)




async def housevotesearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    format_: str = None,
    offset: int = None,
    limit: int = None,
):
    """Search House roll call votes."""
    from congressgov._client.api.house_vote import (
        house_vote_list_async,
        house_vote_list_congress_async,
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json

    HouseVotesModel = ModelRegistry.get_model("HouseVotes")
    resolved_client = await AsyncApiService._resolve_client(self, client)

    from congressgov.services.api_format import resolve_response_format
    from congressgov._client.models.get_house_vote_format import GetHouseVoteFormat
    from congressgov._client.models.get_house_vote_congress_format import (
        GetHouseVoteCongressFormat,
    )

    if congress is not None:
        resp = await house_vote_list_congress_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetHouseVoteCongressFormat),
            offset=offset,
            limit=limit,
        )
    else:
        resp = await house_vote_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetHouseVoteFormat),
            offset=offset,
            limit=limit,
        )

    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseVotesModel.model_validate(api_env.data)




async def summariessearch_async(
    self,
    *,
    client: Any = None,
    congress: int = None,
    bill_type: str = None,
    format_: str = 'json',  # ✅ Default to 'json' format
    offset: int = None,
    limit: int = None,
    from_date_time: str = None,
    to_date_time: str = None,
    sort: str = None
):
    """
    Search for bill summaries using the appropriate API endpoint based on provided arguments.

    Args:
        client: The API client instance. If None, will use self.client if available.
        congress (int, optional): Congress number to filter by.
        bill_type (str, optional): Bill type to filter by (e.g., 'hr', 's').
        format_ (str, optional): Response format.
        offset (int, optional): Offset for pagination.
        limit (int, optional): Limit for pagination.
        from_date_time (str, optional): Start date/time filter.
        to_date_time (str, optional): End date/time filter.
        sort (str, optional): Sort order.

    Returns:
        Summaries: Parsed Summaries model from API response.
    """
    # --- <LAZY IMPORT> ---
    from congressgov._client.api.summaries import (
        bill_summaries_all_async,
        bill_summaries_by_congress_async,
        bill_summaries_by_type_async
    )
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.models.base.model import ApiEnvelope
    import json
    
    # --- <LAZY LOAD MODEL> ---
    SummariesModel = ModelRegistry.get_model("Summaries")
    
    # --- <RESOLVE CLIENT> ---
    resolved_client = await AsyncApiService._resolve_client(self, client)
    
    # --- <ROUTE TO APPROPRIATE ENDPOINT> ---
    if congress is not None and bill_type is not None:
        resp = await bill_summaries_by_type_async(
            client=resolved_client,
            congress=congress,
            bill_type=bill_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
    elif congress is not None:
        resp = await bill_summaries_by_congress_async(
            client=resolved_client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )
    else:
        resp = await bill_summaries_all_async(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )
    
    # --- <ERROR HANDLING> ---
    # Check if response is successful before parsing
    if resp.status_code != 200:
        error_msg = f"API returned status code {resp.status_code}"
        try:
            error_content = resp.content.decode('utf-8')
            if error_content:
                error_msg += f": {error_content}"
        except Exception:
            pass
        raise ValueError(error_msg)
    
    # --- <PARSE RESPONSE> ---
    # Ensure response content is not empty before parsing JSON
    if not resp.content:
        raise ValueError("API returned empty response")
    
    try:
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        return SummariesModel.model_validate(api_env.data)
    except json.JSONDecodeError as e:
        # Provide helpful error message with response preview
        content_preview = resp.content[:500].decode('utf-8', errors='replace')
        raise ValueError(f"Failed to parse API response as JSON: {e}. Response content: {content_preview}")


# ============================================================================
# PUBLIC API EXPORTS
# ============================================================================
# These are the symbols available when using "from congressgov.services.core.search import *"
# and are what IDEs will show in autocomplete for this module.

__all__ = [
    # Main search interface
    'search',
    
    # Registry management functions
    'register_search_handler',
    'unregister_search_handler',
    'get_registered_types',
    
    # Type definitions for type hints
    'HandlerConfig',
    'ResourceType',
]


async def search_async(resource_type: str, self: Any = None, **kwargs: Any) -> Any:
    """Async universal search — mirrors search() with async handlers."""
    handler_name = _SEARCH_REGISTRY[resource_type]["function"] + "_async"
    handler = globals()[handler_name]
    normalized_params = _normalize_parameters(resource_type, kwargs)
    if self is not None:
        result = await handler(self, **normalized_params)
    else:
        result = await handler(None, **normalized_params)

    # NOTE: mirrors the client-attachment backfill in search() — see
    # _attach_client_to_search_result for why this is needed centrally.
    from congressgov.services.core.async_api_service import AsyncApiService

    try:
        resolved_client = await AsyncApiService._resolve_client(
            self, normalized_params.get("client")
        )
    except Exception:
        resolved_client = normalized_params.get("client")

    return _attach_client_to_search_result(result, resolved_client)

