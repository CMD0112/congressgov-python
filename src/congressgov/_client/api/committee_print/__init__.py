"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_committee_print_congress_chamber_jacket_number import sync_detailed as committee_print_detail_sync
from .get_committee_print import sync_detailed as committee_print_list_sync
from .get_committee_print_congress_chamber_jacket_number_text import sync_detailed as committee_print_text_sync
from .get_committee_print_congress_chamber import sync_detailed as committee_prints_by_congress_chamber_sync
from .get_committee_print_congress import sync_detailed as committee_prints_by_congress_sync

from .get_committee_print_congress_chamber_jacket_number import asyncio_detailed as committee_print_detail_async
from .get_committee_print import asyncio_detailed as committee_print_list_async
from .get_committee_print_congress_chamber_jacket_number_text import asyncio_detailed as committee_print_text_async
from .get_committee_print_congress_chamber import asyncio_detailed as committee_prints_by_congress_chamber_async
from .get_committee_print_congress import asyncio_detailed as committee_prints_by_congress_async

# Backward compatibility aliases (without _sync suffix)
committee_print_detail = committee_print_detail_sync
committee_print_list = committee_print_list_sync
committee_print_text = committee_print_text_sync
committee_prints_by_congress_chamber = committee_prints_by_congress_chamber_sync
committee_prints_by_congress = committee_prints_by_congress_sync

__all__ = [
    "committee_print_detail_sync",
    "committee_print_list_sync",
    "committee_print_text_sync",
    "committee_prints_by_congress_chamber_sync",
    "committee_prints_by_congress_sync",
    "committee_print_detail_async",
    "committee_print_list_async",
    "committee_print_text_async",
    "committee_prints_by_congress_chamber_async",
    "committee_prints_by_congress_async",
    "committee_print_detail",
    "committee_print_list",
    "committee_print_text",
    "committee_prints_by_congress_chamber",
    "committee_prints_by_congress",
]

