"""
Query and convenience methods for the Committees model.

These methods are dynamically registered on the Committees class,
keeping the model file clean and focused on data validation.

The query builder (CommitteesQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Field Mappings:
- chamber: Supports chamber variations ("House", "Senate", "H", "S")
  Uses Chamber enum for automatic expansion (if available)

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_chamber(), house_committees(), senate_committees(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder, FieldMapping

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.committees.committee import Committees, Committee

# Import the actual class for registration
from congressgov.models.committees.committee import Committees
import congressgov.models.committees.committee as committee_module

# Import Committee class for validation
from congressgov.models.committees.committee import Committee

# Import enum for chamber mapping (if available)
try:
    from congressgov.models.base.enums import Chamber
    CHAMBER_ENUM = Chamber
except ImportError:
    CHAMBER_ENUM = None

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the CommitteesQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
field_mappings = {}
if CHAMBER_ENUM:
    field_mappings["chamber"] = FieldMapping(enum_class=CHAMBER_ENUM)

CommitteesQuery = create_query_builder(
    collection_class=Committees,
    items_field="committees",
    item_class=Committee,
    field_mappings=field_mappings
)

# NOTE: Set it on the module so it can be imported
committee_module.CommitteesQuery = CommitteesQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['CommitteesQuery'] = CommitteesQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(Committees)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        committees.query().filter(chamber="House", lazy=True).order_by("name").execute()
    
    Returns:
        CommitteesQuery instance for chaining operations
    """
    return CommitteesQuery(self.committees or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(Committees)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter committees by field values.
    
    Args:
        lazy: If True, return CommitteesQuery for chaining. If False, return Committees object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns Committees object
        house_committees = committees.filter(chamber="House")
        
        # Lazy - returns builder for chaining
        query = committees.filter(chamber="House", lazy=True).order_by("name")
        results = query.execute()
    
    Returns:
        Committees object (if eager) or CommitteesQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(Committees)
def by_chamber(self, chamber: str) -> Committees:
    """
    Get committees from a specific chamber (always eager, returns Committees).
    
    Args:
        chamber: Chamber name ("House", "Senate", "H", "S", "House of Representatives")
    
    Returns:
        Filtered Committees object
    
    Example:
        house_committees = committees.by_chamber("House")
    """
    return self.query().filter(chamber=chamber)


@register_method(Committees)
def house_committees(self) -> Committees:
    """
    Get all House committees (always eager, returns Committees).
    
    Returns:
        Filtered Committees object containing only House committees
    
    Example:
        house = committees.house_committees()
    """
    def is_house_committee(c: Committee) -> bool:
        if not hasattr(c, 'chamber') or not c.chamber:
            return False
        chamber_str = c.chamber.value if hasattr(c.chamber, 'value') else str(c.chamber)
        return chamber_str.lower() in ["house", "h", "house of representatives"]
    
    return self.query().where(is_house_committee)


@register_method(Committees)
def senate_committees(self) -> Committees:
    """
    Get all Senate committees (always eager, returns Committees).
    
    Returns:
        Filtered Committees object containing only Senate committees
    
    Example:
        senate = committees.senate_committees()
    """
    def is_senate_committee(c: Committee) -> bool:
        if not hasattr(c, 'chamber') or not c.chamber:
            return False
        chamber_str = c.chamber.value if hasattr(c.chamber, 'value') else str(c.chamber)
        return chamber_str.lower() in ["senate", "s"]
    
    return self.query().where(is_senate_committee)


@register_method(Committees)
def by_name(self, name: str) -> Committees:
    """
    Get committees by name (partial match, case-insensitive) (always eager, returns Committees).
    
    Args:
        name: Committee name or partial name to search for
    
    Returns:
        Filtered Committees object
    
    Example:
        judiciary = committees.by_name("Judiciary")
    """
    def name_matches(c: Committee) -> bool:
        if not hasattr(c, 'name') or not c.name:
            return False
        return name.lower() in c.name.lower()
    
    return self.query().where(name_matches)


@register_method(Committees)
def subcommittees(self) -> Committees:
    """
    Get only subcommittees (always eager, returns Committees).
    
    Returns:
        Filtered Committees object containing only subcommittees
    
    Example:
        subs = committees.subcommittees()
    """
    def is_subcommittee(c: Committee) -> bool:
        # Check if isCurrent indicates it's a subcommittee
        if hasattr(c, 'committeeTypeCode') and c.committeeTypeCode:
            type_code = c.committeeTypeCode.value if hasattr(c.committeeTypeCode, 'value') else str(c.committeeTypeCode)
            return type_code.lower() == 'subcommittee'
        # Fall back to checking parent committee
        if hasattr(c, 'parent') and c.parent:
            return True
        return False
    
    return self.query().where(is_subcommittee)


@register_method(Committees)
def parent_committees(self) -> Committees:
    """
    Get only parent/standing committees (no subcommittees) (always eager, returns Committees).
    
    Returns:
        Filtered Committees object containing only parent committees
    
    Example:
        parents = committees.parent_committees()
    """
    def is_parent_committee(c: Committee) -> bool:
        # Check if it's NOT a subcommittee
        if hasattr(c, 'committeeTypeCode') and c.committeeTypeCode:
            type_code = c.committeeTypeCode.value if hasattr(c.committeeTypeCode, 'value') else str(c.committeeTypeCode)
            return type_code.lower() != 'subcommittee'
        # Fall back to checking parent committee
        if hasattr(c, 'parent') and c.parent:
            return False
        return True
    
    return self.query().where(is_parent_committee)


@register_method(Committees)
def group_by(self, field: str):
    """
    Group committees by field.
    Returns dict mapping field values to Committees objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to Committees objects
    
    Example:
        by_chamber = committees.group_by("chamber")
        # Returns: {"House": Committees(...), "Senate": Committees(...)}
    """
    return self.query().group_by(field)


# ========================================
# COMMITTEE (SINGULAR) INSTANCE METHODS
# ========================================

import json
from typing import Any, Optional
from congressgov._client.api.committee import (
    committee_bills_list_sync,
    committee_reports_by_committee_sync,
    house_communications_by_committee_sync,
    senate_communications_by_committee_sync,
    nomination_by_committee_sync
)
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import expand_sync_instance

# Get model classes
BillsModelSingular = ModelRegistry.get_model("Bills")
CommitteeReportsModelSingular = ModelRegistry.get_model("CommitteeReports")
HouseCommunicationsModelSingular = ModelRegistry.get_model("HouseCommunications")
SenateCommunicationsModelSingular = ModelRegistry.get_model("SenateCommunications")
NominationsModelSingular = ModelRegistry.get_model("Nominations")


def _get_committee_config():
    """Lazy import of committee configuration."""
    from congressgov.services.committee import COMMITTEE_MAPPINGS, COMMITTEE_PARAMETERS
    return COMMITTEE_MAPPINGS, COMMITTEE_PARAMETERS


@register_method(Committee)
def expand(self, client: Any = None, attributes: Optional[list[str]] = None, **kwargs: Any) -> Committee:
    """Expand attributes of this Committee instance."""
    COMMITTEE_MAPPINGS, COMMITTEE_PARAMETERS = _get_committee_config()
    return expand_sync_instance(
        self,
        mapping=COMMITTEE_MAPPINGS,
        parameters=COMMITTEE_PARAMETERS,
        client=client,
        attributes=attributes,
        entity_name="Committee",
        **kwargs,
    )


@register_method(Committee)
def get_bills(self, client: Any = None, **kwargs: Any) -> Any:
    """Get bills associated with this committee."""
    resolved_client = ApiService._resolve_client(self, client)
    chamber = getattr(self, 'chamber', None)
    committee_code = getattr(self, 'committee_code', getattr(self, 'committeeCode', None))
    resp = committee_bills_list_sync(client=resolved_client, chamber=chamber, committee_code=committee_code, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return BillsModelSingular.model_validate(api_env.data)


@register_method(Committee)
def get_reports(self, client: Any = None, **kwargs: Any) -> Any:
    """Get reports associated with this committee."""
    resolved_client = ApiService._resolve_client(self, client)
    chamber = getattr(self, 'chamber', None)
    committee_code = getattr(self, 'committee_code', getattr(self, 'committeeCode', None))
    resp = committee_reports_by_committee_sync(client=resolved_client, chamber=chamber, committee_code=committee_code, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return CommitteeReportsModelSingular.model_validate(api_env.data)


@register_method(Committee)
def get_house_communications(self, client: Any = None, **kwargs: Any) -> Any:
    """Get House communications for this committee."""
    resolved_client = ApiService._resolve_client(self, client)
    chamber = getattr(self, 'chamber', None)
    committee_code = getattr(self, 'committee_code', getattr(self, 'committeeCode', None))
    resp = house_communications_by_committee_sync(client=resolved_client, chamber=chamber, committee_code=committee_code, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return HouseCommunicationsModelSingular.model_validate(api_env.data)


@register_method(Committee)
def get_senate_communications(self, client: Any = None, **kwargs: Any) -> Any:
    """Get Senate communications for this committee."""
    resolved_client = ApiService._resolve_client(self, client)
    chamber = getattr(self, 'chamber', None)
    committee_code = getattr(self, 'committee_code', getattr(self, 'committeeCode', None))
    resp = senate_communications_by_committee_sync(client=resolved_client, chamber=chamber, committee_code=committee_code, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return SenateCommunicationsModelSingular.model_validate(api_env.data)


@register_method(Committee)
def get_nominations(self, client: Any = None, **kwargs: Any) -> Any:
    """Get nominations associated with this committee."""
    resolved_client = ApiService._resolve_client(self, client)
    chamber = getattr(self, 'chamber', None)
    committee_code = getattr(self, 'committee_code', getattr(self, 'committeeCode', None))
    resp = nomination_by_committee_sync(client=resolved_client, chamber=chamber, committee_code=committee_code, **kwargs)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return NominationsModelSingular.model_validate(api_env.data)


@register_method(Committee)
def get_available_attributes(self) -> list[str]:
    """Returns list of expandable attributes."""
    COMMITTEE_MAPPINGS, _ = _get_committee_config()
    return list(COMMITTEE_MAPPINGS.keys())