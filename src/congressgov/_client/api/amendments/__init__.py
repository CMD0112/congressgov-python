"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_amendment_congress_amendment_type_amendment_number_actions import sync_detailed as amendment_actions_sync
from .get_amendment_congress_amendment_type_amendment_number_amendments import sync_detailed as amendment_amendments_sync
from .get_amendment_congress import sync_detailed as amendment_congress_sync
from .get_amendment_congress_amendment_type_amendment_number_cosponsors import sync_detailed as amendment_cosponsors_sync
from .get_amendment_congress_amendment_type_amendment_number import sync_detailed as amendment_details_sync
from .get_amendment_congress_amendment_type import sync_detailed as amendment_list_sync
from .get_amendment import sync_detailed as amendment_sync
from .get_amendment_congress_amendment_type_amendment_number_text import sync_detailed as amendment_text_sync

from .get_amendment_congress_amendment_type_amendment_number_actions import asyncio_detailed as amendment_actions_async
from .get_amendment_congress_amendment_type_amendment_number_amendments import asyncio_detailed as amendment_amendments_async
from .get_amendment_congress import asyncio_detailed as amendment_congress_async
from .get_amendment_congress_amendment_type_amendment_number_cosponsors import asyncio_detailed as amendment_cosponsors_async
from .get_amendment_congress_amendment_type_amendment_number import asyncio_detailed as amendment_details_async
from .get_amendment_congress_amendment_type import asyncio_detailed as amendment_list_async
from .get_amendment import asyncio_detailed as amendment_async
from .get_amendment_congress_amendment_type_amendment_number_text import asyncio_detailed as amendment_text_async

# Backward compatibility aliases (without _sync suffix)
amendment_actions = amendment_actions_sync
amendment_amendments = amendment_amendments_sync
amendment_congress = amendment_congress_sync
amendment_cosponsors = amendment_cosponsors_sync
amendment_details = amendment_details_sync
amendment_list = amendment_list_sync
amendment = amendment_sync
amendment_text = amendment_text_sync

__all__ = [
    "amendment_actions_sync",
    "amendment_amendments_sync",
    "amendment_congress_sync",
    "amendment_cosponsors_sync",
    "amendment_details_sync",
    "amendment_list_sync",
    "amendment_sync",
    "amendment_text_sync",
    "amendment_actions_async",
    "amendment_amendments_async",
    "amendment_congress_async",
    "amendment_cosponsors_async",
    "amendment_details_async",
    "amendment_list_async",
    "amendment_async",
    "amendment_text_async",
    "amendment_actions",
    "amendment_amendments",
    "amendment_congress",
    "amendment_cosponsors",
    "amendment_details",
    "amendment_list",
    "amendment",
    "amendment_text",
]

