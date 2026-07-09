from __future__ import annotations
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient

CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = ['CongressionalRecord', 'CONGRESSIONAL_RECORD_MAPPINGS']


class CongressionalRecord(ApiService):
    """CongressionalRecord service provides API access for congressional record data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    def search(
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
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
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
