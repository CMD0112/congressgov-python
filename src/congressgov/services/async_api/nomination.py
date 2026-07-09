from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.nomination import (
    nomination_actions_async,
    nomination_committees_async,
    nomination_detail_async,
    nomination_hearings_async,
    nominees_async,
)
from congressgov.services.core.validation import validate_congress

from congressgov.models.base.model import ApiEnvelope

NominationModel = ModelRegistry.get_model("Nomination")
NominationsModel = ModelRegistry.get_model("Nominations")
NomineesModel = ModelRegistry.get_model("Nominees")
ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")
HearingsModel = ModelRegistry.get_model("Hearings")

ASYNC_NOMINATION_MAPPINGS = {
    "actions": {nomination_actions_async: ActionsModel},
    "committees": {nomination_committees_async: CommitteesModel},
    "hearings": {nomination_hearings_async: HearingsModel}
}

ASYNC_NOMINATION_PARAMETERS = {
    "congress": "congress",
    "nomination_number": ["nomination_number", "number"]
}

__all__ = ['AsyncNomination', 'ASYNC_NOMINATION_MAPPINGS', 'ASYNC_NOMINATION_PARAMETERS']


class AsyncNomination(AsyncApiService):
    """Nomination service provides API access for Congressional nomination data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        nomination_number: int,
        format_: str = None
    ) -> NominationModel:
        """Get detailed information about a specific nomination."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        
        response = await nomination_detail_async(
            client=resolved_client, 
            congress=congress, 
            nomination_number=nomination_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = NominationModel.model_validate(api_envelope.data)
        
        result.client = resolved_client
        self._last_result = result
        
        return result

    async def get_nominees(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        nomination_number: int,
        ordinal: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> NomineesModel:
        """Get nominees for a nomination at a specific ordinal."""
        validate_congress(congress)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await nominees_async(
            client=resolved_client,
            congress=congress,
            nomination_number=nomination_number,
            ordinal=ordinal,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        payload = api_envelope.data if api_envelope.data is not None else response_json
        result = NomineesModel.model_validate(payload)
        result.client = resolved_client
        return result

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> NominationsModel:
        """Search for nominations using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'nomination',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
