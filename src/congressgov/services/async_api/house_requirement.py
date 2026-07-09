from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.house_requirement import house_requirement_detail_async
from congressgov._client.api.house_requirement.get_house_requirement_requirement_number_matching_communications import (
    asyncio_detailed as house_requirement_matching_communications_detailed,
)

from congressgov.models.base.model import ApiEnvelope

HouseRequirementModel = ModelRegistry.get_model("HouseRequirement")
HouseRequirementsModel = ModelRegistry.get_model("HouseRequirements")

ASYNC_HOUSE_REQUIREMENT_MAPPINGS = {}

__all__ = ['AsyncHouseRequirement', 'ASYNC_HOUSE_REQUIREMENT_MAPPINGS']


class AsyncHouseRequirement(AsyncApiService):
    """HouseRequirement service provides API access for House requirement data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        requirement_number: int,
        format_: str = None
    ) -> HouseRequirementModel:
        """Get detailed information about a specific House requirement."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await house_requirement_detail_async(
            client=resolved_client,
            requirement_number=requirement_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HouseRequirementModel.model_validate(api_envelope.data)
        result.client = resolved_client
        self._last_result = result
        return result

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> HouseRequirementsModel:
        """Search for House requirements using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'house-requirement',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )

    async def matching_communications(
        self,
        *,
        client: AuthenticatedClient | None = None,
        requirement_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await house_requirement_matching_communications_detailed(
            client=resolved_client,
            requirement_number=requirement_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        return api_envelope.data
