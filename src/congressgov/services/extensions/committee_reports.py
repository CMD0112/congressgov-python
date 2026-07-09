"""
Query and convenience methods for the CommitteeReports model.

Registered dynamically via ``_registry`` so CommitteeReports stay plain data models.

Methods registered:
- Query methods: filter(), query(), group_by()
- Convenience methods: by_congress(), by_type(), house_reports(), senate_reports(), etc.
- Python protocols: __iter__, __len__, __getitem__, __bool__, __repr__
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ._registry import register_method
from ._query_builder import create_query_builder

# Import for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.documents.reports import CommitteeReports, CommitteeReport

# Import the actual class for registration
from congressgov.models.documents.reports import CommitteeReports
import congressgov.models.documents.reports as reports_module

# Import CommitteeReport class for validation
from congressgov.models.documents.reports import CommitteeReport


CommitteeReportsQuery = create_query_builder(
    collection_class=CommitteeReports,
    items_field="reports",
    item_class=CommitteeReport,
    field_mappings={
    }
)

# Expose the query class from both the model module and this module's
# globals, since callers import it from either location.
reports_module.CommitteeReportsQuery = CommitteeReportsQuery

if not TYPE_CHECKING:
    globals()['CommitteeReportsQuery'] = CommitteeReportsQuery


@register_method(CommitteeReports)
def query(self):
    """Return a query builder for chained filtering."""
    return CommitteeReportsQuery(self.reports or [])


@register_method(CommitteeReports)
def filter(self, *, lazy: bool = False, **kwargs):
    """
    Filter committee reports by field values.
    
    Args:
        lazy: If True, return CommitteeReportsQuery for chaining. If False, return CommitteeReports object (keyword-only).
        **kwargs: Field-value pairs to filter by.
    
    Examples:
        # Eager (default) - returns CommitteeReports object
        house_reports = reports.filter(type="HRPT")
        
        # Lazy - returns builder for chaining
        query = reports.filter(type="HRPT", lazy=True).order_by("number")
        results = query.execute()
    
    Returns:
        CommitteeReports object (if eager) or CommitteeReportsQuery (if lazy)
    """
    return self.query().filter(lazy=lazy, **kwargs)


@register_method(CommitteeReports)
def by_congress(self, congress: int) -> CommitteeReports:
    """Get reports from a specific Congress."""
    return self.query().filter(congress=congress)


@register_method(CommitteeReports)
def by_type(self, report_type: str) -> CommitteeReports:
    """Get reports of a specific type."""
    return self.query().filter(type=report_type)


@register_method(CommitteeReports)
def house_reports(self) -> CommitteeReports:
    """Get all House reports (HRPT)."""
    def is_house_report(r: CommitteeReport) -> bool:
        if not hasattr(r, 'type') or not r.type:
            return False
        report_type = r.type.value if hasattr(r.type, 'value') else str(r.type)
        return report_type.upper() == "HRPT"
    
    return self.query().where(is_house_report)


@register_method(CommitteeReports)
def senate_reports(self) -> CommitteeReports:
    """Get all Senate reports (SRPT)."""
    def is_senate_report(r: CommitteeReport) -> bool:
        if not hasattr(r, 'type') or not r.type:
            return False
        report_type = r.type.value if hasattr(r.type, 'value') else str(r.type)
        return report_type.upper() == "SRPT"
    
    return self.query().where(is_senate_report)


@register_method(CommitteeReports)
def by_committee(self, committee_name: str) -> CommitteeReports:
    """Get reports by committee name (partial match, case-insensitive)."""
    def committee_matches(r: CommitteeReport) -> bool:
        # Check committees list
        if hasattr(r, 'committees') and r.committees:
            if isinstance(r.committees, list):
                for committee in r.committees:
                    if hasattr(committee, 'name') and committee.name:
                        if committee_name.lower() in committee.name.lower():
                            return True
        return False
    
    return self.query().where(committee_matches)


@register_method(CommitteeReports)
def group_by(self, field: str):
    """
    Group committee reports by field.
    Returns dict mapping field values to CommitteeReports objects.
    
    Args:
        field: Field name to group by
    
    Returns:
        Dictionary mapping field values to CommitteeReports objects
    
    Example:
        by_type = reports.group_by("type")
        # Returns: {"HRPT": CommitteeReports(...), "SRPT": CommitteeReports(...)}
    """
    return self.query().group_by(field)


from typing import Any, Optional

from congressgov.models.documents.reports import CommitteeReport
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import (
    assign_collection_items_to_attribute,
    expand_sync_instance,
)


def _get_committee_report_config():
    from congressgov.services.committee_report import (
        COMMITTEE_REPORT_MAPPINGS,
        COMMITTEE_REPORT_PARAMETERS,
    )
    return COMMITTEE_REPORT_MAPPINGS, COMMITTEE_REPORT_PARAMETERS


def _normalize_committee_report_text(report: CommitteeReport, client: Any = None) -> None:
    value = getattr(report, "text", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = ApiService._resolve_client(report, client)
    assign_collection_items_to_attribute(
        report,
        attribute_name="text",
        wrapper=value,
        items_field="text",
        client=resolved_client,
    )


def _post_expand_committee_report(report: CommitteeReport, client: Any = None) -> None:
    _normalize_committee_report_text(report, client)


@register_method(CommitteeReport)
def expand(
    self: CommitteeReport,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> CommitteeReport:
    """Expand attributes of this committee report (e.g. ``text``)."""
    mappings, parameters = _get_committee_report_config()
    return expand_sync_instance(
        self,
        mapping=mappings,
        parameters=parameters,
        client=client,
        attributes=attributes,
        normalize_params=["report_type"],
        entity_name="CommitteeReport",
        post_expand=_post_expand_committee_report,
        **kwargs,
    )


@register_method(CommitteeReport)
def get_text(self: CommitteeReport, client: Any = None, **kwargs: Any) -> Any:
    """Fetch text versions and store them on ``self.text``."""
    from congressgov.services.committee_report import CommitteeReport as CommitteeReportService

    resolved_client = ApiService._resolve_client(self, client)
    service = CommitteeReportService(client=resolved_client)
    items = service.get_text(
        client=client,
        congress=self.congress,
        report_type=getattr(self, "type", None),
        report_number=self.number,
        **kwargs,
    )
    text_list = items if isinstance(items, list) else [items]
    if resolved_client is not None:
        for item in text_list:
            if getattr(item, "client", None) is None:
                item.client = resolved_client
    self.text = text_list
    return self.text

