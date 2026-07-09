from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_chamber, validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.committee_print import (
    committee_print_detail_sync,
    committee_print_text_sync,
)

from congressgov.models.base.model import ApiEnvelope
from congressgov.models.documents.committee_print import CommitteePrintTexts

CommitteePrintModel = ModelRegistry.get_model("CommitteePrint")
CommitteePrintsModel = ModelRegistry.get_model("CommitteePrints")
CommitteePrintTextModel = ModelRegistry.get_model("CommitteePrintText")

COMMITTEE_PRINT_MAPPINGS = {
    "text": {committee_print_text_sync: CommitteePrintTexts},
}

COMMITTEE_PRINT_PARAMETERS = {
    "congress": "congress",
    "chamber": "chamber",
    "jacket_number": ["jacket_number", "jacketNumber"],
}

__all__ = [
    "CommitteePrint",
    "COMMITTEE_PRINT_MAPPINGS",
    "COMMITTEE_PRINT_PARAMETERS",
]


class CommitteePrint(ApiService):
    """CommitteePrint service provides API access for committee print data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        jacket_number: int,
        chamber: str,
        format_: str = None
    ) -> CommitteePrintModel:
        """Get detailed information about a specific committee print."""
        # CUSTOM: validation
        validate_congress(congress)
        validate_chamber(chamber)

        client = ApiService._resolve_client(self, client)
        response = committee_print_detail_sync(
            client=client,
            congress=congress,
            jacket_number=jacket_number,
            chamber=chamber,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteePrintModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def get_text(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        jacket_number: int,
        format_: str = None,
    ):
        """Return text versions for a committee print."""
        # CUSTOM: committee print text sub-endpoint
        validate_congress(congress)
        validate_chamber(chamber)

        client = ApiService._resolve_client(self, client)
        response = committee_print_text_sync(
            client=client,
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

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> CommitteePrintsModel:
        """Search for committee prints using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'committee-print',
            self,
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit
        )
