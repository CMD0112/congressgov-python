from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_chamber, resolve_response_format
from congressgov.services.core.async_api_service import AsyncApiService
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
from congressgov._client.api.committee_meeting import committee_meeting_detail_async

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.api_response import raise_for_envelope_detail_response

CommitteeMeetingModel = ModelRegistry.get_model("CommitteeMeeting")
CommitteeMeetingsModel = ModelRegistry.get_model("CommitteeMeetings")

ASYNC_COMMITTEE_MEETING_MAPPINGS = {}

__all__ = ['AsyncCommitteeMeeting', 'ASYNC_COMMITTEE_MEETING_MAPPINGS']


class AsyncCommitteeMeeting(AsyncApiService):
    """CommitteeMeeting service provides API access for committee meeting data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        event_id: str,
        format_: str = None
    ) -> CommitteeMeetingModel:
        """Get detailed information about a specific committee meeting."""
        validate_congress(congress)
        validate_chamber(chamber)
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await committee_meeting_detail_async(
            client=resolved_client,
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
        result.client = resolved_client
        self._last_result = result
        return result

    async def search(
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
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'committee-meeting',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
