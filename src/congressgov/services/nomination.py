from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.nomination import (
    nomination_actions_sync,
    nomination_committees_sync,
    nomination_detail_sync,
    nomination_hearings_sync,
    nominees_sync,
)

from congressgov.models.base.model import ApiEnvelope

NominationModel = ModelRegistry.get_model("Nomination")
NominationsModel = ModelRegistry.get_model("Nominations")
NomineesModel = ModelRegistry.get_model("Nominees")
ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")
HearingsModel = ModelRegistry.get_model("Hearings")

NOMINATION_MAPPINGS = {
    "actions": {nomination_actions_sync: ActionsModel},
    "committees": {nomination_committees_sync: CommitteesModel},
    "hearings": {nomination_hearings_sync: HearingsModel}
}

NOMINATION_PARAMETERS = {
    "congress": "congress",
    "nomination_number": ["nomination_number", "number"]
}

__all__ = ['Nomination', 'NOMINATION_MAPPINGS', 'NOMINATION_PARAMETERS']


class Nomination(ApiService):
    """Nomination service provides API access for Congressional nomination data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        nomination_number: int,
        format_: str = None
    ) -> NominationModel:
        """Get detailed information about a specific nomination."""
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        
        response = nomination_detail_sync(
            client=client, 
            congress=congress, 
            nomination_number=nomination_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = NominationModel.model_validate(api_envelope.data)
        
        result.client = client
        self._last_result = result
        
        return result

    def get_nominees(
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
        # CUSTOM: nomination ordinal sub-endpoint
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = nominees_sync(
            client=client,
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
        result.client = client
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> NominationsModel:
        """Search for nominations using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'nomination',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
