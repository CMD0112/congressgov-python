"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_hearing_congress_chamber_jacket_number import sync_detailed as hearing_detail_sync
from .get_hearing_congress_chamber import sync_detailed as hearing_list_by_congress_chamber_sync
from .get_hearing_congress import sync_detailed as hearing_list_by_congress_sync
from .get_hearing import sync_detailed as hearing_list_sync

from .get_hearing_congress_chamber_jacket_number import asyncio_detailed as hearing_detail_async
from .get_hearing_congress_chamber import asyncio_detailed as hearing_list_by_congress_chamber_async
from .get_hearing_congress import asyncio_detailed as hearing_list_by_congress_async
from .get_hearing import asyncio_detailed as hearing_list_async

# Backward compatibility aliases (without _sync suffix)
hearing_detail = hearing_detail_sync
hearing_list_by_congress_chamber = hearing_list_by_congress_chamber_sync
hearing_list_by_congress = hearing_list_by_congress_sync
hearing_list = hearing_list_sync

__all__ = [
    "hearing_detail_sync",
    "hearing_list_by_congress_chamber_sync",
    "hearing_list_by_congress_sync",
    "hearing_list_sync",
    "hearing_detail_async",
    "hearing_list_by_congress_chamber_async",
    "hearing_list_by_congress_async",
    "hearing_list_async",
    "hearing_detail",
    "hearing_list_by_congress_chamber",
    "hearing_list_by_congress",
    "hearing_list",
]

