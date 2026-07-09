from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_chamber, validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.hearing import hearing_detail_sync

from congressgov.models.base.model import ApiEnvelope

HearingModel = ModelRegistry.get_model("Hearing")
HearingsModel = ModelRegistry.get_model("Hearings")

# No expansion mappings needed (hearing endpoints return complete data)
HEARING_MAPPINGS = {}

__all__ = ['Hearing', 'HEARING_MAPPINGS']


class Hearing(ApiService):
    """Hearing service provides API access for Congressional hearing data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        chamber: str,
        jacket_number: int,
        format_: str = None
    ) -> HearingModel:
        """Get detailed information about a specific hearing."""
        # CUSTOM: validation
        validate_congress(congress)
        validate_chamber(chamber)

        client = ApiService._resolve_client(self, client)

        response = hearing_detail_sync(
            client=client,
            congress=congress,
            chamber=chamber,
            jacket_number=jacket_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = HearingModel.model_validate(api_envelope.data)
        
        result.client = client
        self._last_result = result
        
        return result

    def search(
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
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'hearing',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
