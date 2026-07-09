"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_summaries import sync_detailed as bill_summaries_all_sync
from .get_summaries_congress import sync_detailed as bill_summaries_by_congress_sync
from .get_summaries_congress_bill_type import sync_detailed as bill_summaries_by_type_sync

from .get_summaries import asyncio_detailed as bill_summaries_all_async
from .get_summaries_congress import asyncio_detailed as bill_summaries_by_congress_async
from .get_summaries_congress_bill_type import asyncio_detailed as bill_summaries_by_type_async

# Backward compatibility aliases (without _sync suffix)
bill_summaries_all = bill_summaries_all_sync
bill_summaries_by_congress = bill_summaries_by_congress_sync
bill_summaries_by_type = bill_summaries_by_type_sync

__all__ = [
    "bill_summaries_all_sync",
    "bill_summaries_by_congress_sync",
    "bill_summaries_by_type_sync",
    "bill_summaries_all_async",
    "bill_summaries_by_congress_async",
    "bill_summaries_by_type_async",
    "bill_summaries_all",
    "bill_summaries_by_congress",
    "bill_summaries_by_type",
]

