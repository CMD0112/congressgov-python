"""
Query and convenience methods for the CommitteePrints model.

These methods are dynamically registered on the CommitteePrints class,
keeping the model file clean and focused on data validation.

The query builder (CommitteePrintsQuery) is created using the generic
CollectionQuery class from _query_builder.py, eliminating the
need for custom query class implementations.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_chamber(), house_prints(), senate_prints(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.documents.prints import CommitteePrints, CommitteePrint

# Import the actual class for registration
from congressgov.models.documents.prints import CommitteePrints
import congressgov.models.documents.prints as prints_module

# Import CommitteePrint class for validation
from congressgov.models.documents.prints import CommitteePrint

# ========================================
# CREATE QUERY BUILDER WITH FIELD MAPPINGS
# ========================================

# NOTE: Create the CommitteePrintsQuery class using the generic query builder
# NOTE: item_class enables field validation to catch typos early
CommitteePrintsQuery = create_query_builder(
    collection_class=CommitteePrints,
    items_field="committeePrints",
    item_class=CommitteePrint,
    field_mappings={
        # NOTE: Add field mappings here as enums become available
    }
)

# NOTE: Set it on the module so it can be imported
prints_module.CommitteePrintsQuery = CommitteePrintsQuery

# NOTE: Make it available for use in this module
if not TYPE_CHECKING:
    globals()['CommitteePrintsQuery'] = CommitteePrintsQuery

# ========================================
# QUERY BUILDER ACCESS
# ========================================

@register_method(CommitteePrints)
def query(self):
    """
    Get query builder for chaining operations.
    
    Example:
        prints.query().filter(chamber="House", lazy=True).order_by("number").execute()
    
    Returns:
        CommitteePrintsQuery instance for chaining operations
    """
    return CommitteePrintsQuery(self.committeePrints or [])


# ========================================
# CONVENIENCE METHODS (Eager by default)
# ========================================

@register_method(CommitteePrints)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter committee prints by field values.
    
    Args:
        lazy: If True, return CommitteePrintsQuery for chaining. If False, return CommitteePrints object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns CommitteePrints object
        house_prints = prints.filter(chamber="House")
        
        # Lazy - returns builder for chaining
        query = prints.filter(chamber="House", lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        CommitteePrints object (if eager) or CommitteePrintsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(CommitteePrints)
def by_congress(self, congress: int) -> CommitteePrints:
    """
    Get prints from a specific Congress (always eager, returns CommitteePrints).
    
    Args:
        congress: Congress number (e.g., 118 for 118th Congress)
    
    Returns:
        Filtered CommitteePrints object
    
    Example:
        congress_118 = prints.by_congress(118)
    """
    return self.query().filter(congress=congress)


@register_method(CommitteePrints)
def by_chamber(self, chamber: str) -> CommitteePrints:
    """
    Get prints from a specific chamber (always eager, returns CommitteePrints).
    
    Args:
        chamber: Chamber name ("House", "Senate")
    
    Returns:
        Filtered CommitteePrints object
    
    Example:
        house_prints = prints.by_chamber("House")
    """
    return self.query().filter(chamber=chamber)


@register_method(CommitteePrints)
def house_prints(self) -> CommitteePrints:
    """
    Get all House committee prints (always eager, returns CommitteePrints).
    
    Returns:
        Filtered CommitteePrints object containing only House prints
    
    Example:
        house = prints.house_prints()
    """
    def is_house_print(p: CommitteePrint) -> bool:
        if not hasattr(p, 'chamber') or not p.chamber:
            return False
        chamber_str = p.chamber.value if hasattr(p.chamber, 'value') else str(p.chamber)
        return chamber_str.lower() in ["house", "h", "house of representatives"]
    
    return self.query().where(is_house_print)


@register_method(CommitteePrints)
def senate_prints(self) -> CommitteePrints:
    """
    Get all Senate committee prints (always eager, returns CommitteePrints).
    
    Returns:
        Filtered CommitteePrints object containing only Senate prints
    
    Example:
        senate = prints.senate_prints()
    """
    def is_senate_print(p: CommitteePrint) -> bool:
        if not hasattr(p, 'chamber') or not p.chamber:
            return False
        chamber_str = p.chamber.value if hasattr(p.chamber, 'value') else str(p.chamber)
        return chamber_str.lower() in ["senate", "s"]
    
    return self.query().where(is_senate_print)


@register_method(CommitteePrints)
def by_committee(self, committee_name: str) -> CommitteePrints:
    """
    Get prints by committee name (partial match, case-insensitive) (always eager, returns CommitteePrints).
    
    Args:
        committee_name: Committee name or partial name to search for
    
    Returns:
        Filtered CommitteePrints object
    
    Example:
        judiciary = prints.by_committee("Judiciary")
    """
    def committee_matches(p: CommitteePrint) -> bool:
        # Check committees list
        if hasattr(p, 'committees') and p.committees:
            if isinstance(p.committees, list):
                for committee in p.committees:
                    if hasattr(committee, 'name') and committee.name:
                        if committee_name.lower() in committee.name.lower():
                            return True
        return False
    
    return self.query().where(committee_matches)


@register_method(CommitteePrints)
def group_by(self, field: str):
    """
    Group committee prints by field.
    Returns dict mapping field values to CommitteePrints objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to CommitteePrints objects
    
    Example:
        by_chamber = prints.group_by("chamber")
    """
    return self.query().group_by(field)


# ========================================
# COMMITTEE PRINT (SINGULAR) INSTANCE METHODS
# ========================================

from typing import Any, Optional

from congressgov.models.documents.prints import CommitteePrint
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import (
    assign_collection_items_to_attribute,
    expand_sync_instance,
)


def _get_committee_print_config():
    from congressgov.services.committee_print import (
        COMMITTEE_PRINT_MAPPINGS,
        COMMITTEE_PRINT_PARAMETERS,
    )
    return COMMITTEE_PRINT_MAPPINGS, COMMITTEE_PRINT_PARAMETERS


def _normalize_committee_print_text(committee_print: CommitteePrint, client: Any = None) -> None:
    value = getattr(committee_print, "text", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = ApiService._resolve_client(committee_print, client)
    assign_collection_items_to_attribute(
        committee_print,
        attribute_name="text",
        wrapper=value,
        items_field="text",
        client=resolved_client,
    )


def _post_expand_committee_print(committee_print: CommitteePrint, client: Any = None) -> None:
    _normalize_committee_print_text(committee_print, client)


@register_method(CommitteePrint)
def expand(
    self: CommitteePrint,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> CommitteePrint:
    """Expand attributes of this committee print (e.g. ``text``)."""
    mappings, parameters = _get_committee_print_config()
    return expand_sync_instance(
        self,
        mapping=mappings,
        parameters=parameters,
        client=client,
        attributes=attributes,
        normalize_params=["chamber"],
        entity_name="CommitteePrint",
        post_expand=_post_expand_committee_print,
        **kwargs,
    )


@register_method(CommitteePrint)
def get_text(self: CommitteePrint, client: Any = None, **kwargs: Any) -> Any:
    """Fetch text versions and store them on ``self.text``."""
    from congressgov.services.committee_print import CommitteePrint as CommitteePrintService

    resolved_client = ApiService._resolve_client(self, client)
    service = CommitteePrintService(client=resolved_client)
    items = service.get_text(
        client=client,
        congress=self.congress,
        chamber=self.chamber,
        jacket_number=self.jacketNumber,
        **kwargs,
    )
    text_list = items if isinstance(items, list) else [items]
    if resolved_client is not None:
        for item in text_list:
            if getattr(item, "client", None) is None:
                item.client = resolved_client
    self.text = text_list
    return self.text

