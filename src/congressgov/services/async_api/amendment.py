from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_amendment_type, validate_congress

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.amendment import Amendment as AmendmentModel, Amendments as AmendmentsModel
    from congressgov._client import AuthenticatedClient
from congressgov._client.api.amendments import (
    amendment_actions_async,
    amendment_amendments_async,
    amendment_cosponsors_async,
    amendment_details_async,
    amendment_text_async
)

from congressgov.models.base.model import ApiEnvelope

# NOTE: Using ModelRegistry for loose coupling
AmendmentModel = ModelRegistry.get_model("Amendment")
AmendmentsModel = ModelRegistry.get_model("Amendments")
ActionsModel = ModelRegistry.get_model("Actions")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
TextVersionsModel = ModelRegistry.get_model("TextVersions")

# ✅ Expansion mappings - exported for use by extension methods
ASYNC_AMENDMENT_MAPPINGS = {
    "actions": {amendment_actions_async: ActionsModel},
    "amendments": {amendment_amendments_async: AmendmentsModel},
    "cosponsors": {amendment_cosponsors_async: CosponsorsModel},
    "textVersions": {amendment_text_async: TextVersionsModel}
}

ASYNC_AMENDMENT_PARAMETERS = {
    "congress": "congress",
    "amendment_type": ["amendment_type", "type"],
    "amendment_number": ["amendment_number", "number"]
}

__all__ = ['AsyncAmendment', 'ASYNC_AMENDMENT_MAPPINGS', 'ASYNC_AMENDMENT_PARAMETERS']


class AsyncAmendment(AsyncApiService):
    """
    Amendment service provides API access for fetching Congressional amendment data.
    
    This service class handles API interactions for fetching amendments from the
    Congress.gov API. Instance methods on the Amendment model (registered in
    congressgov.services.extensions.amendments) provide additional functionality.
    
    Separation of Concerns:
    - This service class: Fetches data from API (get, search)
    - Amendment model extensions: Operate on fetched data (expand, get_actions, etc.)
    - Amendments model extensions: Query and filter collections (filter, by_type, etc.)
    
    USAGE EXAMPLES:
        # Fetch an amendment
        amendment_service = Amendment(client=my_client)
        amendment = amendment_service.get(congress=118, amendment_type="hamdt", amendment_number="1")
        
        # Use extension methods
        expanded = amendment.expand(attributes=['actions', 'cosponsors'])
        actions = amendment.get_actions()
        
        # Search for amendments
        amendments = amendment_service.search(congress=118, limit=10)
        house_amdts = amendments.house_amendments()
    """
    
    def __init__(self, client: 'AuthenticatedClient | None' = None) -> None:
        """Initialize Amendment service."""
        self.client = client
        self._last_result: 'AmendmentModel | None' = None

    async def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        amendment_type: str,
        amendment_number: str,
        format_: str | None = None
    ) -> 'AmendmentModel':
        """
        Retrieve a single amendment's details from the API.

        Args:
            client: The API client instance.
            congress: Congress number.
            amendment_type: Amendment type (e.g., 'hamdt', 'samdt').
            amendment_number: Amendment number.
            format_: Response format.

        Returns:
            Amendment: Parsed Amendment model with client attached.
            
        Raises:
            ValidationError: If parameters are invalid (includes suggestions)
            APIError: If API request fails
            ClientNotFoundError: If no client is available
            
        Example:
            >>> amendment_service = Amendment(client=my_client)
            >>> amendment = amendment_service.get(congress=118, amendment_type="hamdt", amendment_number="1")
            >>> expanded = amendment.expand()
        """
        # --- <VALIDATE PARAMETERS> ---
        validate_congress(congress)
        validate_amendment_type(amendment_type)
        
        resolved_client = await AsyncApiService._resolve_client(self, client)
        
        resp = await amendment_details_async(
            client=resolved_client,
            congress=congress,
            amendment_type=amendment_type,
            amendment_number=amendment_number,
            format_=format_,
        )
        
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        result = AmendmentModel.model_validate(api_env.data)
        
        # Attach client for extension methods
        result.client = resolved_client
        self._last_result = result
        
        return result

    async def search(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        amendment_type: str | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None
    ) -> 'AmendmentsModel':
        """
        Search for amendments using the universal search system.

        Args:
            client: The API client instance.
            congress: Congress number (optional).
            amendment_type: Amendment type (optional).
            format_: Response format.
            offset: Offset for pagination.
            limit: Limit for pagination.
            from_date_time: Start date/time filter.
            to_date_time: End date/time filter.
            sort: Sort order.

        Returns:
            Amendments: Parsed Amendments collection model.
            
        Example:
            >>> amendment_service = Amendment(client=my_client)
            >>> amendments = amendment_service.search(congress=118, limit=50)
            >>> house_amdts = amendments.house_amendments()
        """
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'amendment',
            self,
            client=client,
            congress=congress,
            amendment_type=amendment_type,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )
