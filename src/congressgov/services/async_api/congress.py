from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.expansion_helpers import propagate_client_to_items
from congressgov.services.core.validation import validate_congress
from congressgov._client.models.get_congress_congress_format import GetCongressCongressFormat
from congressgov._client.models.get_congress_current_format import GetCongressCurrentFormat
from congressgov._client.models.get_congress_format import GetCongressFormat

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.congress import (
    congress_current_list_async,
    congress_list_async,
    congress_details_async
)

from congressgov.models.base.model import ApiEnvelope

CongressModel = ModelRegistry.get_model("Congress")
CongressesModel = ModelRegistry.get_model("Congresses")

# No expansion mappings needed (congress endpoints return complete data)
ASYNC_CONGRESS_MAPPINGS = {}


def _ensure_congress_number(result: CongressModel, congress: int | None = None) -> None:
    """Preserve the requested session number when the API omits ``number``."""
    if result.number is None and congress is not None:
        result.number = congress


__all__ = ['AsyncCongress', 'ASYNC_CONGRESS_MAPPINGS']


class AsyncCongress(AsyncApiService):
    """Congress service provides API access for Congressional session data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def current(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None
    ) -> CongressModel:
        """Get the current Congress session information."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await congress_current_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCongressCurrentFormat),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressModel.model_validate(api_envelope.data)
        result.client = resolved_client
        return result

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        format_: str = None
    ) -> CongressModel:
        """Get detailed information about a specific Congress session."""
        validate_congress(congress)
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await congress_details_async(
            client=resolved_client,
            congress=congress,
            format_=resolve_response_format(format_, GetCongressCongressFormat),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressModel.model_validate(api_envelope.data)
        _ensure_congress_number(result, congress)
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
    ) -> CongressesModel:
        """List all Congress sessions."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await congress_list_async(
            client=resolved_client,
            format_=resolve_response_format(format_, GetCongressFormat),
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressesModel.model_validate(api_envelope.data)
        result.client = resolved_client
        propagate_client_to_items(result, "congresses", resolved_client)
        return result
