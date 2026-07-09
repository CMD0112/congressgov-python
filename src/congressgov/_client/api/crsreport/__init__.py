"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_crsreport_report_number import sync_detailed as crsreport_details_sync
from .get_crsreport import sync_detailed as crsreport_sync

from .get_crsreport_report_number import asyncio_detailed as crsreport_details_async
from .get_crsreport import asyncio_detailed as crsreport_async

# Backward compatibility aliases (without _sync suffix)
crsreport_details = crsreport_details_sync
crsreport = crsreport_sync

__all__ = [
    "crsreport_details_sync",
    "crsreport_sync",
    "crsreport_details_async",
    "crsreport_async",
    "crsreport_details",
    "crsreport",
]

