"""
Query and convenience methods for the Bill and Bills models.

These methods are dynamically registered on the Bill and Bills classes,
keeping the model files clean and focused on data validation.

The query builder (BillsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Field Mappings:
- type: Supports both codes ("hr") and full names ("HR")
  Uses LegislationType enum for automatic expansion
- originChamber: Supports chamber variations ("House", "H", "House of Representatives")
  Uses Chamber enum for automatic expansion

Methods registered on Bills (collection):
- Query methods: filter(), query(), group_by()
- Convenience methods: by_type(), by_congress(), by_chamber(), etc.
- Utility methods: enacted(), house_bills(), senate_bills()
- List as plain list: query().to_list()
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__ (collections_registry)

Methods registered on Bill (singular instance):
- expand(): Expand bill attributes (actions, amendments, committees, etc.)
- expand_specific_attributes(): Expand only specific attributes
- get_available_attributes(): List expandable attributes
- get_actions(), get_amendments(), get_committees(): Fetch related data
- get_cosponsors(), get_related_bills(), get_subjects(), get_summaries()
- get_text_versions(), get_titles()
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bills, Bill

# Import the actual classes for registration
from congressgov.models.entities.bill import Bills, Bill
import congressgov.models.entities.bill as bill_module

# Import enums for field mapping
from congressgov.models.base.enums import LegislationType, Chamber

# Import API functions and models for Bill instance methods
from congressgov._client.api.bill import (
    bill_actions_sync,
    bill_amendments_sync,
    bill_committees_sync,
    bill_cosponsors_sync,
    bill_relatedbills_sync,
    bill_subjects_sync,
    bill_summaries_sync,
    bill_text_sync,
    bill_titles_sync
)
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.expansion_helpers import (
    assign_collection_items_to_attribute,
    bind_bill_subresource,
    expand_sync_instance,
)
from congressgov.services.core.api_service import ApiService

# NOTE: Import BILL_MAPPINGS and BILL_PARAMETERS from congressgov.services.bill
# This avoids circular imports while allowing extensions to use these configs
# The import is done lazily inside functions to prevent import-time issues
def _get_bill_config():
    """Lazy import of bill configuration to avoid circular imports."""
    from congressgov.services.bill import BILL_MAPPINGS, BILL_PARAMETERS
    return BILL_MAPPINGS, BILL_PARAMETERS

# NOTE: Get model classes from registry for use in Bill instance methods
ActionsModel = ModelRegistry.get_model("Actions")
AmendmentsModel = ModelRegistry.get_model("Amendments")


def _normalize_bill_amendments(bill: Bill, client: Any = None) -> None:
    """Store ``list[Amendment]`` on ``bill.amendments`` when expand fetched a wrapper."""
    value = getattr(bill, "amendments", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = ApiService._resolve_client(bill, client)
    assign_collection_items_to_attribute(
        bill,
        attribute_name="amendments",
        wrapper=value,
        items_field="amendments",
        client=resolved_client,
    )


def _post_expand_bill(bill: Bill, client: Any = None) -> None:
    _normalize_bill_amendments(bill, client)


CommitteesModel = ModelRegistry.get_model("Committees")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
BillsModel = ModelRegistry.get_model("Bills")
SubjectModel = ModelRegistry.get_model("Subject")
SummariesModel = ModelRegistry.get_model("Summaries")
TextVersionsModel = ModelRegistry.get_model("TextVersions")
TitlesModel = ModelRegistry.get_model("Titles")

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# Import Bill class for validation

# NOTE: Create the BillsQuery class using the generic query builder
# NOTE: Field mappings enable shorthand queries (e.g., type="hr" matches "HR")
# NOTE: item_class enables field validation to catch typos early
BillsQuery = create_query_builder(
    collection_class=Bills,
    items_field="bills",
    item_class=Bill,
    field_mappings={
        "type": FieldMapping(enum_class=LegislationType),
        "originChamber": FieldMapping(enum_class=Chamber),
        # NOTE: Add more field mappings here as needed
    }
)

# NOTE: Set it on the module so it can be imported
bill_module.BillsQuery = BillsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['BillsQuery'] = BillsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Bills)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        # Start a query chain (lazy by default on query builder)
        bills.query().filter(type="hr", lazy=True).order_by("number").execute()
    
    Returns:
        BillsQuery instance for chaining operations
    """
    return BillsQuery(self.bills or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Bills)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter bills by field values.
    
    Args:
        lazy: If True, return BillsQuery for chaining. If False, return Bills object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Bills object
        hr_bills = bills.filter(type="hr")
        
        # Lazy - returns builder for chaining
        query = bills.filter(type="hr", lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        Bills object (if eager) or BillsQuery (if lazy)
    
    Raises:
        TypeError: If lazy parameter is not a boolean or if a callable is passed
        ValueError: If any field name is invalid
    
    Note:
        For predicate/lambda-based filtering, use .query().where() instead:
        bills.query().where(lambda bill: 5735 <= bill.number <= 5740)
    """
    # NOTE: Type safety - validate lazy parameter early
    if not isinstance(lazy, bool):
        raise TypeError(
            f"filter() 'lazy' parameter must be a boolean, got {type(lazy).__name__}. "
            f"If you're trying to pass a lambda or function, use .query().where() instead:\n"
            f"  ❌ bills.filter(lambda bill: ...)\n"
            f"  ✅ bills.query().where(lambda bill: ...)"
        )
    
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Bills)
def by_type(self, bill_type: str) -> Bills:
    """
    Get bills of a specific type (always eager, returns Bills).
    
    Args:
        bill_type: Bill type code (e.g., "hr", "s", "hjres", "sjres")
    
    Returns:
        Filtered Bills object
    
    Example:
        house_bills = bills.by_type("hr")
    """
    return self.query().filter(type=bill_type)


@register_method(Bills)
def by_congress(self, congress: int) -> Bills:
    """
    Get bills from a specific Congress (always eager, returns Bills).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered Bills object
    
    Example:
        congress_118 = bills.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(Bills)
def by_chamber(self, chamber: str) -> Bills:
    """
    Get bills by originating chamber (always eager, returns Bills).
    
    Args:
        chamber: Chamber name ("House", "Senate", "House of Representatives", "H", "S")
    
    Returns:
        Filtered Bills object
    
    Example:
        house_bills = bills.by_chamber("House")
    """
    return self.query().filter(originChamber=chamber)


@register_method(Bills)
def house_bills(self) -> Bills:
    """
    Get all House bills (hr, hres, hjres, hconres) (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing only House bills
    
    Example:
        house = bills.house_bills()
    """
    def is_house_bill(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["HR", "HRES", "HJRES", "HCONRES"]
    
    return self.query().where(is_house_bill)


@register_method(Bills)
def senate_bills(self) -> Bills:
    """
    Get all Senate bills (s, sres, sjres, sconres) (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing only Senate bills
    
    Example:
        senate = bills.senate_bills()
    """
    def is_senate_bill(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["S", "SRES", "SJRES", "SCONRES"]
    
    return self.query().where(is_senate_bill)


@register_method(Bills)
def resolutions(self) -> Bills:
    """
    Get all resolutions (hres, sres, hjres, sjres, hconres, sconres) (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing only resolutions
    
    Example:
        all_resolutions = bills.resolutions()
    """
    def is_resolution(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return "RES" in bill_type.upper()
    
    return self.query().where(is_resolution)


@register_method(Bills)
def joint_resolutions(self) -> Bills:
    """
    Get joint resolutions only (hjres, sjres) (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing only joint resolutions
    
    Example:
        joint = bills.joint_resolutions()
    """
    def is_joint_resolution(b: Bill) -> bool:
        if not b.type:
            return False
        bill_type = b.type.value if hasattr(b.type, 'value') else str(b.type)
        return bill_type.upper() in ["HJRES", "SJRES"]
    
    return self.query().where(is_joint_resolution)


@register_method(Bills)
def enacted(self) -> Bills:
    """
    Get bills that became law (have laws attribute populated) (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing only enacted bills
    
    Example:
        laws = bills.enacted()
    """
    def has_laws(b: Bill) -> bool:
        # Check if the bill has laws associated with it
        if not hasattr(b, 'laws') or b.laws is None:
            return False
        # Handle CountRef case (has count attribute)
        if hasattr(b.laws, 'count'):
            return (b.laws.count or 0) > 0
        # Handle list case
        if isinstance(b.laws, list):
            return len(b.laws) > 0
        return False
    
    return self.query().where(has_laws)


@register_method(Bills)
def with_actions(self) -> Bills:
    """
    Get bills that have actions recorded (always eager, returns Bills).
    
    Returns:
        Filtered Bills object containing bills with actions
    
    Example:
        active_bills = bills.with_actions()
    """
    def has_actions(b: Bill) -> bool:
        if not hasattr(b, 'actions') or b.actions is None:
            return False
        # Handle CountRef case
        if hasattr(b.actions, 'count'):
            return (b.actions.count or 0) > 0
        # Handle list case
        if isinstance(b.actions, list):
            return len(b.actions) > 0
        return False
    
    return self.query().where(has_actions)


@register_method(Bills)
def by_sponsor(self, sponsor_name: str) -> Bills:
    """
    Get bills by sponsor name (partial match, case-insensitive) (always eager, returns Bills).
    
    Args:
        sponsor_name: Sponsor's name or partial name to search for
    
    Returns:
        Filtered Bills object containing bills by that sponsor
    
    Example:
        pelosi_bills = bills.by_sponsor("Pelosi")
    """
    def has_sponsor(b: Bill) -> bool:
        if not hasattr(b, 'sponsors') or not b.sponsors:
            return False
        # Handle list of sponsors
        if isinstance(b.sponsors, list):
            for sponsor in b.sponsors:
                if hasattr(sponsor, 'fullName') and sponsor.fullName:
                    if sponsor_name.lower() in sponsor.fullName.lower():
                        return True
                # Also check firstName and lastName
                if hasattr(sponsor, 'firstName') and sponsor.firstName:
                    if sponsor_name.lower() in sponsor.firstName.lower():
                        return True
                if hasattr(sponsor, 'lastName') and sponsor.lastName:
                    if sponsor_name.lower() in sponsor.lastName.lower():
                        return True
        return False
    
    return self.query().where(has_sponsor)


@register_method(Bills)
def group_by(self, field: str):
    """
    Group bills by field.
    Returns dict mapping field values to Bills objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Bills objects
    
    Example:
        by_type = bills.group_by("type")
        # Returns: {"HR": Bills(...), "S": Bills(...), ...}
    """
    return self.query().group_by(field)


# ========================================
# BILL (SINGULAR) INSTANCE METHODS
# ========================================
# NOTE: These methods operate on individual Bill instances
# NOTE: They provide convenient access to related data via the API


@register_method(Bill)
def expand(
    self: 'Bill',
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any
) -> 'Bill':
    """
    Expand attributes of this Bill instance by fetching additional data from the API.
    
    This method fetches related data (actions, amendments, committees, etc.) and
    populates the corresponding attributes on the Bill instance.
    
    The method uses BILL_PARAMETERS to support parameter aliases:
    - congress: maps to self.congress
    - bill_type: tries self.bill_type (property) then self.type (field) as fallback
    - bill_number: tries self.bill_number (property) then self.number (field) as fallback
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        attributes: Optional list of specific attributes to expand. If None, expands all available.
        **kwargs: Additional keyword arguments to pass to API functions.
        
    Returns:
        A deepcopy of this Bill instance with expanded attributes.
        
    Raises:
        ValueError: If required attributes (congress, bill_type, bill_number) are missing.
        AttributeError: If this instance doesn't have the required bill identification attributes.
        
    Examples:
        >>> # Expand all attributes
        >>> expanded_bill = bill.expand(client=my_client)
        
        >>> # Expand specific attributes only
        >>> expanded_bill = bill.expand(client=my_client, attributes=['actions', 'cosponsors'])
        
        >>> # If client was attached during fetch, no need to pass it
        >>> bill = Bill(client).get(congress=118, bill_type="hr", bill_number=1)
        >>> expanded_bill = bill.expand()  # Uses attached client
    """
    BILL_MAPPINGS, BILL_PARAMETERS = _get_bill_config()
    return expand_sync_instance(
        self,
        mapping=BILL_MAPPINGS,
        parameters=BILL_PARAMETERS,
        client=client,
        attributes=attributes,
        normalize_params=["bill_type"],
        entity_name="Bill",
        post_expand=_post_expand_bill,
        **kwargs,
    )


@register_method(Bill)
def expand_specific_attributes(
    self: 'Bill',
    *attributes: str,
    client: Any = None,
    **kwargs: Any
) -> 'Bill':
    """
    Convenience method to expand only specific attributes using varargs.
    
    Args:
        *attributes: Specific attribute names to expand (e.g., 'actions', 'cosponsors').
        client: The API client instance. If None, will use self.client if available.
        **kwargs: Additional keyword arguments to pass to API functions.
        
    Returns:
        A deepcopy of this instance with the specified attributes expanded.
        
    Examples:
        >>> # Expand specific attributes
        >>> expanded_bill = bill.expand_specific_attributes('actions', 'cosponsors', client=my_client)
        
        >>> # With attached client
        >>> bill = Bill(client).get(congress=118, bill_type="hr", bill_number=1)
        >>> expanded_bill = bill.expand_specific_attributes('actions', 'titles')
    """
    return self.expand(client=client, attributes=list(attributes), **kwargs)


@register_method(Bill)
def get_available_attributes(self) -> list[str]:
    """
    Returns a list of all available attributes that can be expanded.
    
    Returns:
        List of attribute names that can be expanded using expand() or expand_specific_attributes().
        
    Example:
        >>> attributes = bill.get_available_attributes()
        >>> print(attributes)
        ['actions', 'amendments', 'committees', 'cosponsors', 'relatedBills', 'subjects', 'summaries', 'textVersions', 'titles']
    """
    BILL_MAPPINGS, _ = _get_bill_config()
    return list(BILL_MAPPINGS.keys())


# ========================================
# BILL INSTANCE METHODS - FETCH RELATED DATA
# ========================================
# NOTE: These methods fetch specific types of related data from the API
# NOTE: They are converted from the old standalone functions


@register_method(Bill)
def get_actions(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'ActionsModel':
    """
    Get the actions for this bill.
    
    Fetches all legislative actions taken on this bill from the Congress.gov API.
    Actions include introductions, committee referrals, floor votes, and final passage.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format (default: json).
        refresh: When True, refetch even if actions are already loaded.
        **kwargs: Additional keyword arguments to pass to API function.
        
    Returns:
        Actions model containing the bill's legislative actions with full details.
        
    Raises:
        ClientNotFoundError: If no client is available for API calls
        APIError: If the API request fails
        
    Example:
        >>> from congressgov import Bill
        >>> from congressgov._client import AuthenticatedClient
        >>> 
        >>> client = AuthenticatedClient(token="your-api-key")
        >>> bill_service = Bill(client=client)
        >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
        >>> 
        >>> # Get all actions for the bill
        >>> actions = bill.get_actions()
        >>> print(f"Bill has {len(actions.actions or [])} actions")
        >>> 
        >>> # Actions are ordered chronologically
        >>> for action in actions.actions or []:
        ...     print(f"{action.actionDate}: {action.text}")
    """
    return bind_bill_subresource(
        self,
        attribute_name="actions",
        model_class=ActionsModel,
        api_function=bill_actions_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_amendments(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> list[Any]:
    """
    Get the amendments for this bill.
    
    Fetches all amendments proposed to this bill from the Congress.gov API.
    Amendments can be proposed by members during committee markup or floor consideration.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format (default: json).
        offset: Number of records to skip for pagination (default: 0).
        limit: Maximum number of amendments to return (default: 20).
        from_date_time: Return amendments proposed after this datetime (ISO format).
        to_date_time: Return amendments proposed before this datetime (ISO format).
        sort: Sort order for results (e.g., 'updateDate+asc', 'updateDate+desc').
        **kwargs: Additional keyword arguments to pass to API function.
        
    Returns:
        ``list[Amendment]`` stored on ``bill.amendments``.
        
    Raises:
        ClientNotFoundError: If no client is available for API calls
        APIError: If the API request fails
        
    Example:
        >>> from congressgov import Bill
        >>> from congressgov._client import AuthenticatedClient
        >>> 
        >>> client = AuthenticatedClient(token="your-api-key")
        >>> bill_service = Bill(client=client)
        >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
        >>> 
        >>> # Get all amendments for the bill
        >>> amendments = bill.get_amendments(limit=50)
        >>> print(f"Bill has {len(amendments)} amendments")
        >>> 
        >>> # Filter amendments by date
        >>> recent_amendments = bill.get_amendments(
        ...     from_date_time="2023-01-01T00:00:00Z",
        ...     limit=10
        ... )
    """
    from congressgov.models.base.types import CountRef

    current = getattr(self, "amendments", None)
    if not refresh and current is not None and not isinstance(current, CountRef):
        if isinstance(current, list):
            return current
        resolved_client = ApiService._resolve_client(self, client)
        return assign_collection_items_to_attribute(
            self,
            attribute_name="amendments",
            wrapper=current,
            items_field="amendments",
            client=resolved_client,
        )

    wrapper = bind_bill_subresource(
        self,
        attribute_name="amendments",
        model_class=AmendmentsModel,
        api_function=bill_amendments_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )
    resolved_client = ApiService._resolve_client(self, client)
    return assign_collection_items_to_attribute(
        self,
        attribute_name="amendments",
        wrapper=wrapper,
        items_field="amendments",
        client=resolved_client,
    )


@register_method(Bill)
def get_committees(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'CommitteesModel':
    """
    Get the committees for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        **kwargs: Additional keyword arguments.
        
    Returns:
        Committees model containing the committees that reviewed this bill.
        
    Example:
        >>> committees = bill.get_committees(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="committees",
        model_class=CommitteesModel,
        api_function=bill_committees_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_cosponsors(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'CosponsorsModel':
    """
    Get the cosponsors for this bill.
    
    Fetches all members who have cosponsored this bill from the Congress.gov API.
    Cosponsors are members who support the bill but are not the primary sponsor.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format (default: json).
        offset: Number of records to skip for pagination (default: 0).
        limit: Maximum number of cosponsors to return (default: 20).
        from_date_time: Return cosponsors added after this datetime (ISO format).
        to_date_time: Return cosponsors added before this datetime (ISO format).
        sort: Sort order for results (e.g., 'cosponsorDate+asc', 'cosponsorDate+desc').
        **kwargs: Additional keyword arguments to pass to API function.
        
    Returns:
        Cosponsors model containing the bill's cosponsors with member details.
        
    Raises:
        ClientNotFoundError: If no client is available for API calls
        APIError: If the API request fails
        
    Example:
        >>> from congressgov import Bill
        >>> from congressgov._client import AuthenticatedClient
        >>> 
        >>> client = AuthenticatedClient(token="your-api-key")
        >>> bill_service = Bill(client=client)
        >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
        >>> 
        >>> # Get all cosponsors for the bill
        >>> cosponsors = bill.get_cosponsors(limit=100)
        >>> print(f"Bill has {len(cosponsors.cosponsors or [])} cosponsors")
        >>> 
        >>> # Get recent cosponsors
        >>> recent_cosponsors = bill.get_cosponsors(
        ...     from_date_time="2023-01-01T00:00:00Z",
        ...     limit=20
        ... )
    """
    return bind_bill_subresource(
        self,
        attribute_name="cosponsors",
        model_class=CosponsorsModel,
        api_function=bill_cosponsors_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_related_bills(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'BillsModel':
    """
    Get the related bills for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        offset: Offset for pagination.
        limit: Limit for pagination.
        from_date_time: Start date/time filter.
        to_date_time: End date/time filter.
        sort: Sort order.
        **kwargs: Additional keyword arguments.
        
    Returns:
        Bills model containing related bills.
        
    Example:
        >>> related = bill.get_related_bills(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="relatedBills",
        model_class=BillsModel,
        api_function=bill_relatedbills_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_subjects(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'SubjectModel':
    """
    Get the subjects for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        offset: Offset for pagination.
        limit: Limit for pagination.
        from_date_time: Start date/time filter.
        to_date_time: End date/time filter.
        sort: Sort order.
        **kwargs: Additional keyword arguments.
        
    Returns:
        Subject model containing the bill's policy subjects.
        
    Example:
        >>> subjects = bill.get_subjects(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="subjects",
        model_class=SubjectModel,
        api_function=bill_subjects_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_summaries(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date_time: str | None = None,
    to_date_time: str | None = None,
    sort: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'SummariesModel':
    """
    Get the summaries for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        offset: Offset for pagination.
        limit: Limit for pagination.
        from_date_time: Start date/time filter.
        to_date_time: End date/time filter.
        sort: Sort order.
        **kwargs: Additional keyword arguments.
        
    Returns:
        Summaries model containing CRS summaries of the bill.
        
    Example:
        >>> summaries = bill.get_summaries(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="summaries",
        model_class=SummariesModel,
        api_function=bill_summaries_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
        sort=sort,
        **kwargs,
    )


@register_method(Bill)
def get_text_versions(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'TextVersionsModel':
    """
    Get the text versions for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        **kwargs: Additional keyword arguments.
        
    Returns:
        TextVersions model containing available text versions of the bill.
        
    Example:
        >>> text_versions = bill.get_text_versions(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="textVersions",
        model_class=TextVersionsModel,
        api_function=bill_text_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_method(Bill)
def get_titles(
    self: 'Bill',
    client: Any = None,
    format_: str | None = None,
    refresh: bool = False,
    **kwargs: Any
) -> 'TitlesModel':
    """
    Get the titles for this bill.
    
    Args:
        client: The API client instance. If None, will use self.client if available.
        format_: Response format.
        **kwargs: Additional keyword arguments.
        
    Returns:
        Titles model containing all titles associated with this bill.
        
    Example:
        >>> titles = bill.get_titles(client=my_client)
    """
    return bind_bill_subresource(
        self,
        attribute_name="titles",
        model_class=TitlesModel,
        api_function=bill_titles_sync,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )
