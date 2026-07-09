"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_committee_report_congress_report_type_report_number import sync_detailed as committee_report_details_sync
from .get_committee_report_congress_report_type_report_number_text import sync_detailed as committee_report_id_text_sync
from .get_committee_report_congress_report_type import sync_detailed as committee_reports_by_congress_rpt_type_sync
from .get_committee_report_congress import sync_detailed as committee_reports_by_congress_sync
from .get_committee_report import sync_detailed as committee_reports_sync

from .get_committee_report_congress_report_type_report_number import asyncio_detailed as committee_report_details_async
from .get_committee_report_congress_report_type_report_number_text import asyncio_detailed as committee_report_id_text_async
from .get_committee_report_congress_report_type import asyncio_detailed as committee_reports_by_congress_rpt_type_async
from .get_committee_report_congress import asyncio_detailed as committee_reports_by_congress_async
from .get_committee_report import asyncio_detailed as committee_reports_async

# Backward compatibility aliases (without _sync suffix)
committee_report_details = committee_report_details_sync
committee_report_id_text = committee_report_id_text_sync
committee_reports_by_congress_rpt_type = committee_reports_by_congress_rpt_type_sync
committee_reports_by_congress = committee_reports_by_congress_sync
committee_reports = committee_reports_sync

__all__ = [
    "committee_report_details_sync",
    "committee_report_id_text_sync",
    "committee_reports_by_congress_rpt_type_sync",
    "committee_reports_by_congress_sync",
    "committee_reports_sync",
    "committee_report_details_async",
    "committee_report_id_text_async",
    "committee_reports_by_congress_rpt_type_async",
    "committee_reports_by_congress_async",
    "committee_reports_async",
    "committee_report_details",
    "committee_report_id_text",
    "committee_reports_by_congress_rpt_type",
    "committee_reports_by_congress",
    "committee_reports",
]

