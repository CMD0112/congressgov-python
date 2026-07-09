"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_senate_communication_congress import sync_detailed as senate_communication_congress_sync
from .get_senate_communication_congress_communication_type_communication_number import sync_detailed as senate_communication_detail_sync
from .get_senate_communication_congress_communication_type import sync_detailed as senate_communication_list_sync
from .get_senate_communication import sync_detailed as senate_communication_sync

from .get_senate_communication_congress import asyncio_detailed as senate_communication_congress_async
from .get_senate_communication_congress_communication_type_communication_number import asyncio_detailed as senate_communication_detail_async
from .get_senate_communication_congress_communication_type import asyncio_detailed as senate_communication_list_async
from .get_senate_communication import asyncio_detailed as senate_communication_async

# Backward compatibility aliases (without _sync suffix)
senate_communication_congress = senate_communication_congress_sync
senate_communication_detail = senate_communication_detail_sync
senate_communication_list = senate_communication_list_sync
senate_communication = senate_communication_sync

__all__ = [
    "senate_communication_congress_sync",
    "senate_communication_detail_sync",
    "senate_communication_list_sync",
    "senate_communication_sync",
    "senate_communication_congress_async",
    "senate_communication_detail_async",
    "senate_communication_list_async",
    "senate_communication_async",
    "senate_communication_congress",
    "senate_communication_detail",
    "senate_communication_list",
    "senate_communication",
]

