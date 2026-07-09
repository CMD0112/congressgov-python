"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_treaty_congress_treaty_number_actions import sync_detailed as treaty_action_sync
from .get_treaty_congress_treaty_number_treaty_suffix_actions import sync_detailed as treaty_actions_sync
from .get_treaty_congress_treaty_number_committees import sync_detailed as treaty_committee_sync
from .get_treaty_congress_treaty_number import sync_detailed as treaty_detail_sync
from .get_treaty_congress_treaty_number_treaty_suffix import sync_detailed as treaty_details_sync
from .get_treaty_congress import sync_detailed as treaty_list_by_congress_sync
from .get_treaty import sync_detailed as treaty_list_sync

from .get_treaty_congress_treaty_number_actions import asyncio_detailed as treaty_action_async
from .get_treaty_congress_treaty_number_treaty_suffix_actions import asyncio_detailed as treaty_actions_async
from .get_treaty_congress_treaty_number_committees import asyncio_detailed as treaty_committee_async
from .get_treaty_congress_treaty_number import asyncio_detailed as treaty_detail_async
from .get_treaty_congress_treaty_number_treaty_suffix import asyncio_detailed as treaty_details_async
from .get_treaty_congress import asyncio_detailed as treaty_list_by_congress_async
from .get_treaty import asyncio_detailed as treaty_list_async

# Backward compatibility aliases (without _sync suffix)
treaty_action = treaty_action_sync
treaty_actions = treaty_actions_sync
treaty_committee = treaty_committee_sync
treaty_detail = treaty_detail_sync
treaty_details = treaty_details_sync
treaty_list_by_congress = treaty_list_by_congress_sync
treaty_list = treaty_list_sync

__all__ = [
    "treaty_action_sync",
    "treaty_actions_sync",
    "treaty_committee_sync",
    "treaty_detail_sync",
    "treaty_details_sync",
    "treaty_list_by_congress_sync",
    "treaty_list_sync",
    "treaty_action_async",
    "treaty_actions_async",
    "treaty_committee_async",
    "treaty_detail_async",
    "treaty_details_async",
    "treaty_list_by_congress_async",
    "treaty_list_async",
    "treaty_action",
    "treaty_actions",
    "treaty_committee",
    "treaty_detail",
    "treaty_details",
    "treaty_list_by_congress",
    "treaty_list",
]

