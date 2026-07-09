from __future__ import annotations
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry


SummariesModel = ModelRegistry.get_model("Summaries")

ASYNC_SUMMARIES_MAPPINGS = {}

__all__ = ['AsyncSummaries', 'ASYNC_SUMMARIES_MAPPINGS']


class AsyncSummaries(AsyncApiService):
    """Summaries service provides API access for bill summaries data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> SummariesModel:
        """Search for bill summaries using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'summary',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )
