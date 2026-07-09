from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.senate_communication import senate_communication_detail_async

from congressgov.models.base.model import ApiEnvelope

SenateCommunicationModel = ModelRegistry.get_model("SenateCommunication")
SenateCommunicationsModel = ModelRegistry.get_model("SenateCommunications")

ASYNC_SENATE_COMMUNICATION_MAPPINGS = {}

__all__ = ['AsyncSenateCommunication', 'ASYNC_SENATE_COMMUNICATION_MAPPINGS']


class AsyncSenateCommunication(AsyncApiService):
    """SenateCommunication service provides API access for Senate communication data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        communication_type: str,
        communication_number: int,
        format_: str = None
    ) -> SenateCommunicationModel:
        """Get detailed information about a specific Senate communication."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await senate_communication_detail_async(
            client=resolved_client,
            congress=congress,
            communication_type=communication_type,
            communication_number=communication_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = SenateCommunicationModel.model_validate(api_envelope.data)
        result.client = resolved_client
        self._last_result = result
        return result

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        communication_type: str = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> SenateCommunicationsModel:
        """Search for Senate communications using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'senate-communication',
            self,
            client=client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
