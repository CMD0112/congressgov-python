from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov._client.api.bound_congressional_record import (
    bound_congressional_record_list_by_year_and_month_and_day_async,
    bound_congressional_record_list_by_year_and_month_async,
    bound_congressional_record_list_by_year_async,
)
from congressgov.models.base.model import ApiEnvelope

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient

ASYNC_BOUND_CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = ['AsyncBoundCongressionalRecord', 'ASYNC_BOUND_CONGRESSIONAL_RECORD_MAPPINGS']


class AsyncBoundCongressionalRecord(AsyncApiService):
    """BoundCongressionalRecord service provides API access for bound congressional record data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int = None,
        month: int = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ):
        """Search for bound congressional records using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'bound-congressional-record',
            self,
            client=client,
            year=year,
            month=month,
            format_=format_,
            offset=offset,
            limit=limit
        )

    async def get_by_year(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await bound_congressional_record_list_by_year_async(
            client=resolved_client, year=year, format_=format_, offset=offset, limit=limit
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data

    async def get_by_year_month(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int,
        month: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await bound_congressional_record_list_by_year_and_month_async(
            client=resolved_client,
            year=year,
            month=month,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data

    async def get_by_date(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int,
        month: int,
        day: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await bound_congressional_record_list_by_year_and_month_and_day_async(
            client=resolved_client,
            year=year,
            month=month,
            day=day,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data
