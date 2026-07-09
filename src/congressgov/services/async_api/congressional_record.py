from __future__ import annotations
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient

ASYNC_CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = ['AsyncCongressionalRecord', 'ASYNC_CONGRESSIONAL_RECORD_MAPPINGS']


class AsyncCongressionalRecord(AsyncApiService):
    """CongressionalRecord service provides API access for congressional record data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int = None,
        month: int = None,
        day: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ):
        """Search for congressional records using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'congressional-record',
            self,
            client=client,
            year=year,
            month=month,
            day=day,
            format_=format_,
            offset=offset,
            limit=limit
        )
