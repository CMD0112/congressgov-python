from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_chamber, resolve_response_format
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_chamber, validate_congress
from congressgov._client.models.get_committee_meeting_congress_chamber_event_id_chamber import (
    GetCommitteeMeetingCongressChamberEventIdChamber,
)
from congressgov._client.models.get_committee_meeting_congress_chamber_event_id_format import (
    GetCommitteeMeetingCongressChamberEventIdFormat,
)

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.committee_meeting import committee_meeting_detail_sync

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.api_response import raise_for_envelope_detail_response

CommitteeMeetingModel = ModelRegistry.get_model("CommitteeMeeting")
CommitteeMeetingsModel = ModelRegistry.get_model("CommitteeMeetings")

COMMITTEE_MEETING_MAPPINGS = {}

__all__ = ['CommitteeMeeting', 'COMMITTEE_MEETING_MAPPINGS']


class CommitteeMeeting(ApiService):
    """CommitteeMeeting service provides API access for committee meeting data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        event_id: str,
        format_: str = None
    ) -> CommitteeMeetingModel:
        """Get detailed information about a specific committee meeting."""
        # CUSTOM: validation
        validate_congress(congress)
        validate_chamber(chamber)

        client = ApiService._resolve_client(self, client)
        response = committee_meeting_detail_sync(
            client=client,
            congress=congress,
            chamber=resolve_chamber(chamber, GetCommitteeMeetingCongressChamberEventIdChamber),
            event_id=event_id,
            format_=resolve_response_format(
                format_, GetCommitteeMeetingCongressChamberEventIdFormat
            ),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        raise_for_envelope_detail_response(
            response,
            response_json,
            api_envelope,
            resource_label="Committee meeting",
            identifiers={
                "congress": congress,
                "chamber": chamber,
                "event_id": event_id,
            },
        )
        result = CommitteeMeetingModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        chamber: str = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> CommitteeMeetingsModel:
        """Search for committee meetings using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'committee-meeting',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
