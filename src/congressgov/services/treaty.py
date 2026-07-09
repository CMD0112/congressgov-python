from __future__ import annotations

import json
from typing import TYPE_CHECKING

from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.treaty import (
    treaty_actions_sync,
    treaty_committee_sync,
    treaty_detail_sync,
    treaty_details_sync,
)

from congressgov.models.base.model import ApiEnvelope

TreatyModel = ModelRegistry.get_model("Treaty")
TreatiesModel = ModelRegistry.get_model("Treaties")
ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")

TREATY_MAPPINGS = {
    "actions": {treaty_actions_sync: ActionsModel},
    "committee": {treaty_committee_sync: CommitteesModel}
}

TREATY_PARAMETERS = {
    "congress": "congress",
    "treaty_number": ["treaty_number", "number"]
}

__all__ = ['Treaty', 'TREATY_MAPPINGS', 'TREATY_PARAMETERS']


class Treaty(ApiService):
    """Treaty service provides API access for treaty data."""
    
    def __init__(self, client: "AuthenticatedClient | None" = None) -> None:
        self.client = client
        self._last_result: TreatyModel | None = None

    def get(
        self,
        *,
        client: "AuthenticatedClient | None" = None,
        congress: int,
        treaty_number: int,
        treaty_suffix: str | None = None,
        format_: str | None = None,
    ) -> TreatyModel:
        """Get detailed information about a specific treaty.

        Raises:
            ClientNotFoundError: If no API client is available.
        """
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)

        if treaty_suffix:
            response = treaty_details_sync(
                client=client,
                congress=congress,
                treaty_number=treaty_number,
                treaty_suffix=treaty_suffix,
                format_=format_,
            )
        else:
            response = treaty_detail_sync(
                client=client,
                congress=congress,
                treaty_number=treaty_number,
                format_=format_,
            )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = TreatyModel.model_validate(api_envelope.data)
        
        result.client = client
        self._last_result = result
        
        return result

    def search(
        self,
        *,
        client: "AuthenticatedClient | None" = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> TreatiesModel:
        """Search for treaties using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'treaty',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )

    def get_actions(
        self,
        *,
        client: "AuthenticatedClient | None" = None,
        congress: int,
        treaty_number: int,
        format_: str | None = None,
    ) -> ActionsModel:
        """Return actions for a treaty."""
        # CUSTOM: treaty actions sub-endpoint
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = treaty_actions_sync(
            client=client,
            congress=congress,
            treaty_number=treaty_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = ActionsModel.model_validate(api_envelope.data)
        result.client = client
        return result
