"""
Query and convenience methods for the Nominations model.

These methods are dynamically registered on the Nominations class,
keeping the model file clean and focused on data validation.

The query builder (NominationsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_organization(), confirmed(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.nominations.nomination import Nominations, Nomination

# Import the actual class for registration
from congressgov.models.nominations.nomination import Nominations
import congressgov.models.nominations.nomination as nomination_module

# Import Nomination class for validation
from congressgov.models.nominations.nomination import Nomination

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the NominationsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
NominationsQuery = create_query_builder(
    collection_class=Nominations,
    items_field="nominations",
    item_class=Nomination,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
nomination_module.NominationsQuery = NominationsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['NominationsQuery'] = NominationsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Nominations)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        nominations.query().filter(congress=118, lazy=True).order_by("number").execute()
    
    Returns:
        NominationsQuery instance for chaining operations
    """
    return NominationsQuery(self.nominations or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Nominations)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter nominations by field values.
    
    Args:
        lazy: If True, return NominationsQuery for chaining. If False, return Nominations object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Nominations object
        congress_118 = nominations.filter(congress=118)
        
        # Lazy - returns builder for chaining
        query = nominations.filter(congress=118, lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        Nominations object (if eager) or NominationsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Nominations)
def by_congress(self, congress: int) -> Nominations:
    """
    Get nominations from a specific Congress (always eager, returns Nominations).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered Nominations object
    
    Example:
        congress_118 = nominations.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(Nominations)
def by_organization(self, organization: str) -> Nominations:
    """
    Get nominations for a specific organization (partial match, case-insensitive) (always eager, returns Nominations).
    
    Args:
        organization: Organization name or partial name to search for
    
    Returns:
        Filtered Nominations object
    
    Example:
        state_dept = nominations.by_organization("State Department")
    """
    def organization_matches(n: Nomination) -> bool:
        if not hasattr(n, 'organization') or not n.organization:
            return False
        return organization.lower() in n.organization.lower()
    
    return self.query().where(organization_matches)


@register_method(Nominations)
def confirmed(self) -> Nominations:
    """
    Get confirmed nominations (always eager, returns Nominations).
    
    Returns:
        Filtered Nominations object containing only confirmed nominations
    
    Example:
        confirmed = nominations.confirmed()
    """
    def is_confirmed(n: Nomination) -> bool:
        # Check latest action for confirmation
        if hasattr(n, 'latestAction') and n.latestAction:
            if hasattr(n.latestAction, 'text') and n.latestAction.text:
                text_lower = n.latestAction.text.lower()
                return 'confirmed' in text_lower or 'confirmation' in text_lower
        return False
    
    return self.query().where(is_confirmed)


@register_method(Nominations)
def with_hearings(self) -> Nominations:
    """
    Get nominations that have hearings scheduled or completed (always eager, returns Nominations).
    
    Returns:
        Filtered Nominations object containing nominations with hearings
    
    Example:
        with_hearings = nominations.with_hearings()
    """
    def has_hearings(n: Nomination) -> bool:
        if not hasattr(n, 'hearings') or n.hearings is None:
            return False
        # Handle CountRef case
        if hasattr(n.hearings, 'count'):
            return (n.hearings.count or 0) > 0
        # Handle list case
        if isinstance(n.hearings, list):
            return len(n.hearings) > 0
        return False
    
    return self.query().where(has_hearings)


@register_method(Nominations)
def group_by(self, field: str):
    """
    Group nominations by field.
    Returns dict mapping field values to Nominations objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Nominations objects
    
    Example:
        by_congress = nominations.group_by("congress")
    """
    return self.query().group_by(field)


# ========================================
# NOMINATION (SINGULAR) INSTANCE METHODS
# ========================================

import json
from typing import Any, Optional
from congressgov._client.api.nomination import (
    nomination_actions_sync,
    nomination_committees_sync,
    nomination_hearings_sync
)
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import expand_sync_instance

ActionsModelSingular = ModelRegistry.get_model("Actions")
CommitteesModelSingular = ModelRegistry.get_model("Committees")
HearingsModelSingular = ModelRegistry.get_model("Hearings")


def _get_nomination_config():
    """Lazy import of nomination configuration."""
    from congressgov.services.nomination import NOMINATION_MAPPINGS, NOMINATION_PARAMETERS
    return NOMINATION_MAPPINGS, NOMINATION_PARAMETERS


@register_method(Nomination)
def expand(self, client: Any = None, attributes: Optional[list[str]] = None, **kwargs: Any) -> Nomination:
    """Expand attributes of this Nomination instance."""
    NOMINATION_MAPPINGS, NOMINATION_PARAMETERS = _get_nomination_config()
    return expand_sync_instance(
        self,
        mapping=NOMINATION_MAPPINGS,
        parameters=NOMINATION_PARAMETERS,
        client=client,
        attributes=attributes,
        entity_name="Nomination",
        **kwargs,
    )


@register_method(Nomination)
def get_actions(self, client: Any = None, **kwargs: Any) -> Any:
    """Get actions for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_actions_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return ActionsModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_committees(self, client: Any = None, **kwargs: Any) -> Any:
    """Get committees for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_committees_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteesModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_hearings(self, client: Any = None, **kwargs: Any) -> Any:
    """Get hearings for this nomination."""
    resolved_client = ApiService._resolve_client(self, client)
    congress = getattr(self, 'congress', None)
    nomination_number = getattr(self, 'nomination_number', getattr(self, 'number', None))
    resp = nomination_hearings_sync(client=resolved_client, congress=congress, nomination_number=nomination_number, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HearingsModelSingular.model_validate(api_env.data)


@register_method(Nomination)
def get_available_attributes(self) -> list[str]:
    """Returns list of expandable attributes."""
    NOMINATION_MAPPINGS, _ = _get_nomination_config()
    return list(NOMINATION_MAPPINGS.keys())