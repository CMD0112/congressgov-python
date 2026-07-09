"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_congress_current import sync_detailed as congress_current_list_sync
from .get_congress_congress import sync_detailed as congress_details_sync
from .get_congress import sync_detailed as congress_list_sync

from .get_congress_current import asyncio_detailed as congress_current_list_async
from .get_congress_congress import asyncio_detailed as congress_details_async
from .get_congress import asyncio_detailed as congress_list_async

# Backward compatibility aliases (without _sync suffix)
congress_current_list = congress_current_list_sync
congress_details = congress_details_sync
congress_list = congress_list_sync

__all__ = [
    "congress_current_list_sync",
    "congress_details_sync",
    "congress_list_sync",
    "congress_current_list_async",
    "congress_details_async",
    "congress_list_async",
    "congress_current_list",
    "congress_details",
    "congress_list",
]

