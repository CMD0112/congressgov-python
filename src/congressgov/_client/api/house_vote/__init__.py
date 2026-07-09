"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_house_vote_congress_session_vote_number import sync_detailed as house_vote_details_sync
from .get_house_vote_congress_session import sync_detailed as house_vote_list_congress_session_sync
from .get_house_vote_congress import sync_detailed as house_vote_list_congress_sync
from .get_house_vote import sync_detailed as house_vote_list_sync
from .get_house_vote_congress_session_vote_number_members import sync_detailed as house_vote_members_sync

from .get_house_vote_congress_session_vote_number import asyncio_detailed as house_vote_details_async
from .get_house_vote_congress_session import asyncio_detailed as house_vote_list_congress_session_async
from .get_house_vote_congress import asyncio_detailed as house_vote_list_congress_async
from .get_house_vote import asyncio_detailed as house_vote_list_async
from .get_house_vote_congress_session_vote_number_members import asyncio_detailed as house_vote_members_async

# Backward compatibility aliases (without _sync suffix)
house_vote_details = house_vote_details_sync
house_vote_list_congress_session = house_vote_list_congress_session_sync
house_vote_list_congress = house_vote_list_congress_sync
house_vote_list = house_vote_list_sync
house_vote_members = house_vote_members_sync

__all__ = [
    "house_vote_details_sync",
    "house_vote_list_congress_session_sync",
    "house_vote_list_congress_sync",
    "house_vote_list_sync",
    "house_vote_members_sync",
    "house_vote_details_async",
    "house_vote_list_congress_session_async",
    "house_vote_list_congress_async",
    "house_vote_list_async",
    "house_vote_members_async",
    "house_vote_details",
    "house_vote_list_congress_session",
    "house_vote_list_congress",
    "house_vote_list",
    "house_vote_members",
]

