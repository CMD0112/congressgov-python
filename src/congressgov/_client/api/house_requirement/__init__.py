"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_house_requirement_requirement_number_matching_communications import sync_detailed as house_requirement_communication_list_sync
from .get_house_requirement_requirement_number import sync_detailed as house_requirement_detail_sync
from .get_house_requirement import sync_detailed as house_requirement_sync

from .get_house_requirement_requirement_number_matching_communications import asyncio_detailed as house_requirement_communication_list_async
from .get_house_requirement_requirement_number import asyncio_detailed as house_requirement_detail_async
from .get_house_requirement import asyncio_detailed as house_requirement_async

# Backward compatibility aliases (without _sync suffix)
house_requirement_communication_list = house_requirement_communication_list_sync
house_requirement_detail = house_requirement_detail_sync
house_requirement = house_requirement_sync

__all__ = [
    "house_requirement_communication_list_sync",
    "house_requirement_detail_sync",
    "house_requirement_sync",
    "house_requirement_communication_list_async",
    "house_requirement_detail_async",
    "house_requirement_async",
    "house_requirement_communication_list",
    "house_requirement_detail",
    "house_requirement",
]

