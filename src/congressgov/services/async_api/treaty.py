from __future__ import annotations

import json
from typing import TYPE_CHECKING

from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.treaty import (
    treaty_actions_async,
    treaty_committee_async,
    treaty_detail_async,
    treaty_details_async,
)

from congressgov.models.base.model import ApiEnvelope

TreatyModel = ModelRegistry.get_model("Treaty")
TreatiesModel = ModelRegistry.get_model("Treaties")
ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")

ASYNC_TREATY_MAPPINGS = {
    "actions": {treaty_actions_async: ActionsModel},
    "committee": {treaty_committee_async: CommitteesModel}
}

ASYNC_TREATY_PARAMETERS = {
    "congress": "congress",
    "treaty_number": ["treaty_number", "number"]
}

__all__ = ['AsyncTreaty', 'ASYNC_TREATY_MAPPINGS', 'ASYNC_TREATY_PARAMETERS']


class AsyncTreaty(AsyncApiService):
    """Treaty service provides API access for treaty data."""
    
    def __init__(self, client: "AuthenticatedClient | None" = None) -> None:
        self.client = client
        self._last_result: TreatyModel | None = None

    async def get(
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
        resolved_client = await AsyncApiService._resolve_client(self, client)

        if treaty_suffix:
            response = await treaty_details_async(
                client=resolved_client,
                congress=congress,
                treaty_number=treaty_number,
                treaty_suffix=treaty_suffix,
                format_=format_,
            )
        else:
            response = await treaty_detail_async(
                client=resolved_client,
                congress=congress,
                treaty_number=treaty_number,
                format_=format_,
            )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = TreatyModel.model_validate(api_envelope.data)
        
        result.client = resolved_client
        self._last_result = result
        
        return result

    async def search(
        self,
        *,
        client: "AuthenticatedClient | None" = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> TreatiesModel:
        """Search for treaties using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'treaty',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )

    async def get_actions(
        self,
        *,
        client: "AuthenticatedClient | None" = None,
        congress: int,
        treaty_number: int,
        format_: str | None = None,
    ) -> ActionsModel:
        """Return actions for a treaty."""
        validate_congress(congress)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await treaty_actions_async(
            client=resolved_client,
            congress=congress,
            treaty_number=treaty_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = ActionsModel.model_validate(api_envelope.data)
        result.client = resolved_client
        return result
