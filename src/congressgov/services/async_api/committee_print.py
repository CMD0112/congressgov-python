from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.committee_print import (
    committee_print_detail_async,
    committee_print_text_async,
)
from congressgov.services.core.validation import validate_chamber, validate_congress

from congressgov.models.base.model import ApiEnvelope
from congressgov.models.documents.committee_print import CommitteePrintTexts

CommitteePrintModel = ModelRegistry.get_model("CommitteePrint")
CommitteePrintsModel = ModelRegistry.get_model("CommitteePrints")
CommitteePrintTextModel = ModelRegistry.get_model("CommitteePrintText")

ASYNC_COMMITTEE_PRINT_MAPPINGS = {
    "text": {committee_print_text_async: CommitteePrintTexts},
}

ASYNC_COMMITTEE_PRINT_PARAMETERS = {
    "congress": "congress",
    "chamber": "chamber",
    "jacket_number": ["jacket_number", "jacketNumber"],
}

__all__ = [
    "AsyncCommitteePrint",
    "ASYNC_COMMITTEE_PRINT_MAPPINGS",
    "ASYNC_COMMITTEE_PRINT_PARAMETERS",
]


class AsyncCommitteePrint(AsyncApiService):
    """CommitteePrint service provides API access for committee print data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        jacket_number: int,
        chamber: str,
        format_: str = None
    ) -> CommitteePrintModel:
        """Get detailed information about a specific committee print."""
        validate_congress(congress)
        validate_chamber(chamber)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await committee_print_detail_async(
            client=resolved_client,
            congress=congress,
            jacket_number=jacket_number,
            chamber=chamber,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteePrintModel.model_validate(api_envelope.data)
        result.client = resolved_client
        self._last_result = result
        return result

    async def get_text(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        jacket_number: int,
        format_: str = None,
    ):
        """Return text versions for a committee print."""
        validate_congress(congress)
        validate_chamber(chamber)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await committee_print_text_async(
            client=resolved_client,
            congress=congress,
            chamber=chamber,
            jacket_number=jacket_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        payload = response_json.get("data", api_envelope.data)
        if isinstance(payload, list):
            return [CommitteePrintTextModel.model_validate(item) for item in payload]
        return CommitteePrintTextModel.model_validate(payload)

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> CommitteePrintsModel:
        """Search for committee prints using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'committee-print',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
