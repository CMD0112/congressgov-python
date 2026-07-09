from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov._client.api.bound_congressional_record import (
    bound_congressional_record_list_by_year_and_month_and_day_sync,
    bound_congressional_record_list_by_year_and_month_sync,
    bound_congressional_record_list_by_year_sync,
)
from congressgov.models.base.model import ApiEnvelope

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient

BOUND_CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = ['BoundCongressionalRecord', 'BOUND_CONGRESSIONAL_RECORD_MAPPINGS']


class BoundCongressionalRecord(ApiService):
    """BoundCongressionalRecord service provides API access for bound congressional record data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client

    def search(
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
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'bound-congressional-record',
            self,
            client=client,
            year=year,
            month=month,
            format_=format_,
            offset=offset,
            limit=limit
        )

    def get_by_year(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        """List bound congressional records for a year."""
        # CUSTOM: year sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = bound_congressional_record_list_by_year_sync(
            client=client, year=year, format_=format_, offset=offset, limit=limit
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data

    def get_by_year_month(
        self,
        *,
        client: AuthenticatedClient | None = None,
        year: int,
        month: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ):
        """List bound congressional records for a year and month."""
        # CUSTOM: year/month sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = bound_congressional_record_list_by_year_and_month_sync(
            client=client,
            year=year,
            month=month,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data

    def get_by_date(
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
        """List bound congressional records for a specific date."""
        # CUSTOM: year/month/day sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = bound_congressional_record_list_by_year_and_month_and_day_sync(
            client=client,
            year=year,
            month=month,
            day=day,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        return ApiEnvelope.model_validate(json.loads(response.content)).data
