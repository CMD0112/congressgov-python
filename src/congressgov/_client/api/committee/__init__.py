"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_committee_chamber_committee_code_bills import sync_detailed as committee_bills_list_sync
from .get_committee_chamber_committee_code import sync_detailed as committee_details_sync
from .get_committee_chamber import sync_detailed as committee_list_by_chamber_sync
from .get_committee_congress_chamber import sync_detailed as committee_list_by_congress_chamber_sync
from .get_committee_congress import sync_detailed as committee_list_by_congress_sync
from .get_committee import sync_detailed as committee_list_sync
from .get_committee_chamber_committee_code_reports import sync_detailed as committee_reports_by_committee_sync
from .get_committee_chamber_committee_code_house_communication import sync_detailed as house_communications_by_committee_sync
from .get_committee_chamber_committee_code_nominations import sync_detailed as nomination_by_committee_sync
from .get_committee_chamber_committee_code_senate_communication import sync_detailed as senate_communications_by_committee_sync

from .get_committee_chamber_committee_code_bills import asyncio_detailed as committee_bills_list_async
from .get_committee_chamber_committee_code import asyncio_detailed as committee_details_async
from .get_committee_chamber import asyncio_detailed as committee_list_by_chamber_async
from .get_committee_congress_chamber import asyncio_detailed as committee_list_by_congress_chamber_async
from .get_committee_congress import asyncio_detailed as committee_list_by_congress_async
from .get_committee import asyncio_detailed as committee_list_async
from .get_committee_chamber_committee_code_reports import asyncio_detailed as committee_reports_by_committee_async
from .get_committee_chamber_committee_code_house_communication import asyncio_detailed as house_communications_by_committee_async
from .get_committee_chamber_committee_code_nominations import asyncio_detailed as nomination_by_committee_async
from .get_committee_chamber_committee_code_senate_communication import asyncio_detailed as senate_communications_by_committee_async

# Backward compatibility aliases (without _sync suffix)
committee_bills_list = committee_bills_list_sync
committee_details = committee_details_sync
committee_list_by_chamber = committee_list_by_chamber_sync
committee_list_by_congress_chamber = committee_list_by_congress_chamber_sync
committee_list_by_congress = committee_list_by_congress_sync
committee_list = committee_list_sync
committee_reports_by_committee = committee_reports_by_committee_sync
house_communications_by_committee = house_communications_by_committee_sync
nomination_by_committee = nomination_by_committee_sync
senate_communications_by_committee = senate_communications_by_committee_sync

__all__ = [
    "committee_bills_list_sync",
    "committee_details_sync",
    "committee_list_by_chamber_sync",
    "committee_list_by_congress_chamber_sync",
    "committee_list_by_congress_sync",
    "committee_list_sync",
    "committee_reports_by_committee_sync",
    "house_communications_by_committee_sync",
    "nomination_by_committee_sync",
    "senate_communications_by_committee_sync",
    "committee_bills_list_async",
    "committee_details_async",
    "committee_list_by_chamber_async",
    "committee_list_by_congress_chamber_async",
    "committee_list_by_congress_async",
    "committee_list_async",
    "committee_reports_by_committee_async",
    "house_communications_by_committee_async",
    "nomination_by_committee_async",
    "senate_communications_by_committee_async",
    "committee_bills_list",
    "committee_details",
    "committee_list_by_chamber",
    "committee_list_by_congress_chamber",
    "committee_list_by_congress",
    "committee_list",
    "committee_reports_by_committee",
    "house_communications_by_committee",
    "nomination_by_committee",
    "senate_communications_by_committee",
]

