"""Contains endpoint functions for accessing the API (compat re-exports)."""
# isort: skip_file

from .get_bill_congress_bill_type_bill_number_actions import sync_detailed as bill_actions_sync
from .get_bill_congress_bill_type_bill_number_amendments import sync_detailed as bill_amendments_sync
from .get_bill_congress_bill_type_bill_number_committees import sync_detailed as bill_committees_sync
from .get_bill_congress_bill_type_bill_number_cosponsors import sync_detailed as bill_cosponsors_sync
from .get_bill_congress_bill_type_bill_number import sync_detailed as bill_details_sync
from .get_bill import sync_detailed as bill_list_all_sync
from .get_bill_congress import sync_detailed as bill_list_by_congress_sync
from .get_bill_congress_bill_type import sync_detailed as bill_list_by_type_sync
from .get_bill_congress_bill_type_bill_number_relatedbills import sync_detailed as bill_relatedbills_sync
from .get_bill_congress_bill_type_bill_number_subjects import sync_detailed as bill_subjects_sync
from .get_bill_congress_bill_type_bill_number_summaries import sync_detailed as bill_summaries_sync
from .get_bill_congress_bill_type_bill_number_text import sync_detailed as bill_text_sync
from .get_bill_congress_bill_type_bill_number_titles import sync_detailed as bill_titles_sync
from .get_law_congress_law_type import sync_detailed as law_list_by_congress_and_law_type_sync
from .get_law_congress_law_type_law_number import sync_detailed as law_list_by_congress_law_type_and_law_number_sync
from .get_law_congress import sync_detailed as law_list_by_congress_sync

from .get_bill_congress_bill_type_bill_number_actions import asyncio_detailed as bill_actions_async
from .get_bill_congress_bill_type_bill_number_amendments import asyncio_detailed as bill_amendments_async
from .get_bill_congress_bill_type_bill_number_committees import asyncio_detailed as bill_committees_async
from .get_bill_congress_bill_type_bill_number_cosponsors import asyncio_detailed as bill_cosponsors_async
from .get_bill_congress_bill_type_bill_number import asyncio_detailed as bill_details_async
from .get_bill import asyncio_detailed as bill_list_all_async
from .get_bill_congress import asyncio_detailed as bill_list_by_congress_async
from .get_bill_congress_bill_type import asyncio_detailed as bill_list_by_type_async
from .get_bill_congress_bill_type_bill_number_relatedbills import asyncio_detailed as bill_relatedbills_async
from .get_bill_congress_bill_type_bill_number_subjects import asyncio_detailed as bill_subjects_async
from .get_bill_congress_bill_type_bill_number_summaries import asyncio_detailed as bill_summaries_async
from .get_bill_congress_bill_type_bill_number_text import asyncio_detailed as bill_text_async
from .get_bill_congress_bill_type_bill_number_titles import asyncio_detailed as bill_titles_async
from .get_law_congress_law_type import asyncio_detailed as law_list_by_congress_and_law_type_async
from .get_law_congress_law_type_law_number import asyncio_detailed as law_list_by_congress_law_type_and_law_number_async
from .get_law_congress import asyncio_detailed as law_list_by_congress_async

# Backward compatibility aliases (without _sync suffix)
bill_actions = bill_actions_sync
bill_amendments = bill_amendments_sync
bill_committees = bill_committees_sync
bill_cosponsors = bill_cosponsors_sync
bill_details = bill_details_sync
bill_list_all = bill_list_all_sync
bill_list_by_congress = bill_list_by_congress_sync
bill_list_by_type = bill_list_by_type_sync
bill_relatedbills = bill_relatedbills_sync
bill_subjects = bill_subjects_sync
bill_summaries = bill_summaries_sync
bill_text = bill_text_sync
bill_titles = bill_titles_sync
law_list_by_congress_and_law_type = law_list_by_congress_and_law_type_sync
law_list_by_congress_law_type_and_law_number = law_list_by_congress_law_type_and_law_number_sync
law_list_by_congress = law_list_by_congress_sync

__all__ = [
    "bill_actions_sync",
    "bill_amendments_sync",
    "bill_committees_sync",
    "bill_cosponsors_sync",
    "bill_details_sync",
    "bill_list_all_sync",
    "bill_list_by_congress_sync",
    "bill_list_by_type_sync",
    "bill_relatedbills_sync",
    "bill_subjects_sync",
    "bill_summaries_sync",
    "bill_text_sync",
    "bill_titles_sync",
    "law_list_by_congress_and_law_type_sync",
    "law_list_by_congress_law_type_and_law_number_sync",
    "law_list_by_congress_sync",
    "bill_actions_async",
    "bill_amendments_async",
    "bill_committees_async",
    "bill_cosponsors_async",
    "bill_details_async",
    "bill_list_all_async",
    "bill_list_by_congress_async",
    "bill_list_by_type_async",
    "bill_relatedbills_async",
    "bill_subjects_async",
    "bill_summaries_async",
    "bill_text_async",
    "bill_titles_async",
    "law_list_by_congress_and_law_type_async",
    "law_list_by_congress_law_type_and_law_number_async",
    "law_list_by_congress_async",
    "bill_actions",
    "bill_amendments",
    "bill_committees",
    "bill_cosponsors",
    "bill_details",
    "bill_list_all",
    "bill_list_by_congress",
    "bill_list_by_type",
    "bill_relatedbills",
    "bill_subjects",
    "bill_summaries",
    "bill_text",
    "bill_titles",
    "law_list_by_congress_and_law_type",
    "law_list_by_congress_law_type_and_law_number",
    "law_list_by_congress",
]

