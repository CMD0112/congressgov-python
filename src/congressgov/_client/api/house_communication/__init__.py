"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_house_communication_congress import sync_detailed as house_communication_congress_sync
from .get_house_communication_congress_communication_type_communication_number import sync_detailed as house_communication_detail_sync
from .get_house_communication_congress_communication_type import sync_detailed as house_communication_list_sync
from .get_house_communication import sync_detailed as house_communication_sync

from .get_house_communication_congress import asyncio_detailed as house_communication_congress_async
from .get_house_communication_congress_communication_type_communication_number import asyncio_detailed as house_communication_detail_async
from .get_house_communication_congress_communication_type import asyncio_detailed as house_communication_list_async
from .get_house_communication import asyncio_detailed as house_communication_async

# Backward compatibility aliases (without _sync suffix)
house_communication_congress = house_communication_congress_sync
house_communication_detail = house_communication_detail_sync
house_communication_list = house_communication_list_sync
house_communication = house_communication_sync

__all__ = [
    "house_communication_congress_sync",
    "house_communication_detail_sync",
    "house_communication_list_sync",
    "house_communication_sync",
    "house_communication_congress_async",
    "house_communication_detail_async",
    "house_communication_list_async",
    "house_communication_async",
    "house_communication_congress",
    "house_communication_detail",
    "house_communication_list",
    "house_communication",
]

