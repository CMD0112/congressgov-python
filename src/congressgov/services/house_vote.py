from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.house_vote import (
    house_vote_details_sync,
    house_vote_list_congress_session_sync,
)
from congressgov._client.models.get_house_vote_congress_session_session import (
    GetHouseVoteCongressSessionSession,
)
from congressgov._client.api.house_vote.get_house_vote_congress_session_vote_number_members import (
    sync_detailed as house_vote_members_detailed,
)
from congressgov._client.models.get_house_vote_congress_session_vote_number_members_session import (
    GetHouseVoteCongressSessionVoteNumberMembersSession,
)

from congressgov.models.base.model import ApiEnvelope

HouseVoteModel = ModelRegistry.get_model("HouseVote")
HouseVotesModel = ModelRegistry.get_model("HouseVotes")
MemberVotesModel = ModelRegistry.get_model("MemberVotes")

HOUSE_VOTE_MAPPINGS = {}

__all__ = ['HouseVote', 'HOUSE_VOTE_MAPPINGS']


class HouseVote(ApiService):
    """HouseVote service provides API access for House vote data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        session: int,
        vote_number: int,
        format_: str = None
    ) -> HouseVoteModel:
        """Get detailed information about a specific House vote."""
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = house_vote_details_sync(
            client=client,
            congress=congress,
            session=session,
            vote_number=vote_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HouseVoteModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> HouseVotesModel:
        """Search for House votes using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'house-vote',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )

    def list_by_congress_session(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        session: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> HouseVotesModel:
        """List House votes for a Congress and session."""
        # CUSTOM: congress/session vote list
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        session_param = GetHouseVoteCongressSessionSession(session)
        response = house_vote_list_congress_session_sync(
            client=client,
            congress=congress,
            session=session_param,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HouseVotesModel.model_validate(api_envelope.data)
        result.client = client
        return result

    def members(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        session: int,
        vote_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> MemberVotesModel:
        """Return per-member vote positions for a House roll call vote (beta endpoint)."""
        # CUSTOM: members sub-endpoint
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        session_param = GetHouseVoteCongressSessionVoteNumberMembersSession(session)
        response = house_vote_members_detailed(
            client=client,
            congress=congress,
            session=session_param,
            vote_number=vote_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        payload = api_envelope.data if api_envelope.data is not None else response_json
        result = MemberVotesModel.model_validate(payload)
        result.client = client
        return result
