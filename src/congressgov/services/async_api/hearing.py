from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.hearing import hearing_detail_async

from congressgov.models.base.model import ApiEnvelope

HearingModel = ModelRegistry.get_model("Hearing")
HearingsModel = ModelRegistry.get_model("Hearings")

# No expansion mappings needed (hearing endpoints return complete data)
ASYNC_HEARING_MAPPINGS = {}

__all__ = ['AsyncHearing', 'ASYNC_HEARING_MAPPINGS']


class AsyncHearing(AsyncApiService):
    """Hearing service provides API access for Congressional hearing data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        jacket_number: int,
        format_: str = None
    ) -> HearingModel:
        """Get detailed information about a specific hearing."""
        resolved_client = await AsyncApiService._resolve_client(self, client)

        response = await hearing_detail_async(
            client=resolved_client,
            congress=congress,
            chamber=chamber,
            jacket_number=jacket_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HearingModel.model_validate(api_envelope.data)
        
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
    ) -> HearingsModel:
        """Search for hearings using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'hearing',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
