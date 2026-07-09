"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_committee_meeting_congress_chamber import sync_detailed as committee_meeting_congress_chamber_sync
from .get_committee_meeting_congress import sync_detailed as committee_meeting_congress_sync
from .get_committee_meeting_congress_chamber_event_id import sync_detailed as committee_meeting_detail_sync
from .get_committee_meeting import sync_detailed as committee_meeting_list_sync

from .get_committee_meeting_congress_chamber import asyncio_detailed as committee_meeting_congress_chamber_async
from .get_committee_meeting_congress import asyncio_detailed as committee_meeting_congress_async
from .get_committee_meeting_congress_chamber_event_id import asyncio_detailed as committee_meeting_detail_async
from .get_committee_meeting import asyncio_detailed as committee_meeting_list_async

# Backward compatibility aliases (without _sync suffix)
committee_meeting_congress_chamber = committee_meeting_congress_chamber_sync
committee_meeting_congress = committee_meeting_congress_sync
committee_meeting_detail = committee_meeting_detail_sync
committee_meeting_list = committee_meeting_list_sync

__all__ = [
    "committee_meeting_congress_chamber_sync",
    "committee_meeting_congress_sync",
    "committee_meeting_detail_sync",
    "committee_meeting_list_sync",
    "committee_meeting_congress_chamber_async",
    "committee_meeting_congress_async",
    "committee_meeting_detail_async",
    "committee_meeting_list_async",
    "committee_meeting_congress_chamber",
    "committee_meeting_congress",
    "committee_meeting_detail",
    "committee_meeting_list",
]

