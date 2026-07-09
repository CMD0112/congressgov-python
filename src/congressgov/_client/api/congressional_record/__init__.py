"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_congressional_record import sync_detailed as congressional_record_list_sync

from .get_congressional_record import asyncio_detailed as congressional_record_list_async

# Backward compatibility aliases (without _sync suffix)
congressional_record_list = congressional_record_list_sync

__all__ = [
    "congressional_record_list_sync",
    "congressional_record_list_async",
    "congressional_record_list",
]

