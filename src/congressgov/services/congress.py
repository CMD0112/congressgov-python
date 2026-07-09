from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import propagate_client_to_items
from congressgov.services.core.validation import validate_congress
from congressgov._client.models.get_congress_congress_format import GetCongressCongressFormat
from congressgov._client.models.get_congress_current_format import GetCongressCurrentFormat
from congressgov._client.models.get_congress_format import GetCongressFormat

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.congress import (
    congress_current_list_sync,
    congress_list_sync,
    congress_details_sync,
)

from congressgov.models.base.model import ApiEnvelope

CongressModel = ModelRegistry.get_model("Congress")
CongressesModel = ModelRegistry.get_model("Congresses")

CONGRESS_MAPPINGS = {}


def _ensure_congress_number(result: CongressModel, congress: int | None = None) -> None:
    """Preserve the requested session number when the API omits ``number``."""
    if result.number is None and congress is not None:
        result.number = congress


__all__ = ['Congress', 'CONGRESS_MAPPINGS']


class Congress(ApiService):
    """Congress service provides API access for Congressional session data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def current(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None
    ) -> CongressModel:
        """Get the current Congress session information."""
        # CUSTOM: current session method
        client = ApiService._resolve_client(self, client)
        response = congress_current_list_sync(
            client=client,
            format_=resolve_response_format(format_, GetCongressCurrentFormat),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressModel.model_validate(api_envelope.data)
        result.client = client
        return result

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        format_: str = None
    ) -> CongressModel:
        """Get detailed information about a specific Congress session."""
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = congress_details_sync(
            client=client,
            congress=congress,
            format_=resolve_response_format(format_, GetCongressCongressFormat),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressModel.model_validate(api_envelope.data)
        _ensure_congress_number(result, congress)
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
    ) -> CongressesModel:
        """List all Congress sessions."""
        # CUSTOM: direct list search
        client = ApiService._resolve_client(self, client)
        response = congress_list_sync(
            client=client,
            format_=resolve_response_format(format_, GetCongressFormat),
            offset=offset,
            limit=limit,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CongressesModel.model_validate(api_envelope.data)
        result.client = client
        propagate_client_to_items(result, "congresses", client)
        return result
