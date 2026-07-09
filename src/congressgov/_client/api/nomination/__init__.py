"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_nomination_congress_nomination_number_actions import sync_detailed as nomination_actions_sync
from .get_nomination_congress_nomination_number_committees import sync_detailed as nomination_committees_sync
from .get_nomination_congress_nomination_number import sync_detailed as nomination_detail_sync
from .get_nomination_congress_nomination_number_hearings import sync_detailed as nomination_hearings_sync
from .get_nomination_congress import sync_detailed as nomination_list_by_congress_sync
from .get_nomination import sync_detailed as nomination_list_sync
from .get_nomination_congress_nomination_number_ordinal import sync_detailed as nominees_sync

from .get_nomination_congress_nomination_number_actions import asyncio_detailed as nomination_actions_async
from .get_nomination_congress_nomination_number_committees import asyncio_detailed as nomination_committees_async
from .get_nomination_congress_nomination_number import asyncio_detailed as nomination_detail_async
from .get_nomination_congress_nomination_number_hearings import asyncio_detailed as nomination_hearings_async
from .get_nomination_congress import asyncio_detailed as nomination_list_by_congress_async
from .get_nomination import asyncio_detailed as nomination_list_async
from .get_nomination_congress_nomination_number_ordinal import asyncio_detailed as nominees_async

# Backward compatibility aliases (without _sync suffix)
nomination_actions = nomination_actions_sync
nomination_committees = nomination_committees_sync
nomination_detail = nomination_detail_sync
nomination_hearings = nomination_hearings_sync
nomination_list_by_congress = nomination_list_by_congress_sync
nomination_list = nomination_list_sync
nominees = nominees_sync

__all__ = [
    "nomination_actions_sync",
    "nomination_committees_sync",
    "nomination_detail_sync",
    "nomination_hearings_sync",
    "nomination_list_by_congress_sync",
    "nomination_list_sync",
    "nominees_sync",
    "nomination_actions_async",
    "nomination_committees_async",
    "nomination_detail_async",
    "nomination_hearings_async",
    "nomination_list_by_congress_async",
    "nomination_list_async",
    "nominees_async",
    "nomination_actions",
    "nomination_committees",
    "nomination_detail",
    "nomination_hearings",
    "nomination_list_by_congress",
    "nomination_list",
    "nominees",
]

