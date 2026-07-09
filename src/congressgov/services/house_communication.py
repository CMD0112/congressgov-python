from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.house_communication import house_communication_detail_sync

from congressgov.models.base.model import ApiEnvelope

HouseCommunicationModel = ModelRegistry.get_model("HouseCommunication")
HouseCommunicationsModel = ModelRegistry.get_model("HouseCommunications")

HOUSE_COMMUNICATION_MAPPINGS = {}

__all__ = ['HouseCommunication', 'HOUSE_COMMUNICATION_MAPPINGS']


class HouseCommunication(ApiService):
    """HouseCommunication service provides API access for House communication data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        communication_type: str,
        communication_number: int,
        format_: str = None
    ) -> HouseCommunicationModel:
        """Get detailed information about a specific House communication."""
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = house_communication_detail_sync(
            client=client,
            congress=congress,
            communication_type=communication_type,
            communication_number=communication_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HouseCommunicationModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        communication_type: str = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> HouseCommunicationsModel:
        """Search for House communications using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'house-communication',
            self,
            client=client,
            congress=congress,
            communication_type=communication_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
