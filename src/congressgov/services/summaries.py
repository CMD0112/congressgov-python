from __future__ import annotations
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry


SummariesModel = ModelRegistry.get_model("Summaries")

SUMMARIES_MAPPINGS = {}

__all__ = ['Summaries', 'SUMMARIES_MAPPINGS']


class Summaries(ApiService):
    """Summaries service provides API access for bill summaries data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> SummariesModel:
        """Search for bill summaries using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'summary',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )
