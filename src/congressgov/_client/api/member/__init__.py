"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_member_congress_congress import sync_detailed as member_congress_list_sync
from .get_member_bioguide_id_cosponsored_legislation import sync_detailed as member_cosponsorship_list_sync
from .get_member_bioguide_id import sync_detailed as member_details_sync
from .get_member_congress_congress_state_code_district import sync_detailed as member_list_by_congress_state_district_sync
from .get_member_state_code_district import sync_detailed as member_list_by_state_and_district_sync
from .get_member_state_code import sync_detailed as member_list_by_state_sync
from .get_member import sync_detailed as member_list_sync
from .get_member_bioguide_id_sponsored_legislation import sync_detailed as member_sponsorship_list_sync

from .get_member_congress_congress import asyncio_detailed as member_congress_list_async
from .get_member_bioguide_id_cosponsored_legislation import asyncio_detailed as member_cosponsorship_list_async
from .get_member_bioguide_id import asyncio_detailed as member_details_async
from .get_member_congress_congress_state_code_district import asyncio_detailed as member_list_by_congress_state_district_async
from .get_member_state_code_district import asyncio_detailed as member_list_by_state_and_district_async
from .get_member_state_code import asyncio_detailed as member_list_by_state_async
from .get_member import asyncio_detailed as member_list_async
from .get_member_bioguide_id_sponsored_legislation import asyncio_detailed as member_sponsorship_list_async

# Backward compatibility aliases (without _sync suffix)
member_congress_list = member_congress_list_sync
member_cosponsorship_list = member_cosponsorship_list_sync
member_details = member_details_sync
member_list_by_congress_state_district = member_list_by_congress_state_district_sync
member_list_by_state_and_district = member_list_by_state_and_district_sync
member_list_by_state = member_list_by_state_sync
member_list = member_list_sync
member_sponsorship_list = member_sponsorship_list_sync

__all__ = [
    "member_congress_list_sync",
    "member_cosponsorship_list_sync",
    "member_details_sync",
    "member_list_by_congress_state_district_sync",
    "member_list_by_state_and_district_sync",
    "member_list_by_state_sync",
    "member_list_sync",
    "member_sponsorship_list_sync",
    "member_congress_list_async",
    "member_cosponsorship_list_async",
    "member_details_async",
    "member_list_by_congress_state_district_async",
    "member_list_by_state_and_district_async",
    "member_list_by_state_async",
    "member_list_async",
    "member_sponsorship_list_async",
    "member_congress_list",
    "member_cosponsorship_list",
    "member_details",
    "member_list_by_congress_state_district",
    "member_list_by_state_and_district",
    "member_list_by_state",
    "member_list",
    "member_sponsorship_list",
]

