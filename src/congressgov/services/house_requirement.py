from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.house_requirement import (
    house_requirement_detail_sync,
)
from congressgov._client.api.house_requirement.get_house_requirement_requirement_number_matching_communications import (
    sync_detailed as house_requirement_matching_communications_detailed,
)

from congressgov.models.base.model import ApiEnvelope

HouseRequirementModel = ModelRegistry.get_model("HouseRequirement")
HouseRequirementsModel = ModelRegistry.get_model("HouseRequirements")

HOUSE_REQUIREMENT_MAPPINGS = {}

__all__ = ['HouseRequirement', 'HOUSE_REQUIREMENT_MAPPINGS']


class HouseRequirement(ApiService):
    """HouseRequirement service provides API access for House requirement data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        requirement_number: int,
        format_: str = None
    ) -> HouseRequirementModel:
        """Get detailed information about a specific House requirement."""
        client = ApiService._resolve_client(self, client)
        response = house_requirement_detail_sync(
            client=client,
            requirement_number=requirement_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HouseRequirementModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> HouseRequirementsModel:
        """Search for House requirements using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'house-requirement',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )

    def matching_communications(
        self,
        *,
        client: AuthenticatedClient | None = None,
        requirement_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        """List communications matching a House requirement."""
        # CUSTOM: matching communications sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = house_requirement_matching_communications_detailed(
            client=client,
            requirement_number=requirement_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        return api_envelope.data
