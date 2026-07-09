from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record import (
    asyncio_detailed as daily_congressional_record_list_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number import (
    asyncio_detailed as daily_congressional_record_volume_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number_issue_number import (
    asyncio_detailed as daily_congressional_record_issue_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number_issue_number_articles import (
    asyncio_detailed as daily_congressional_record_articles_detailed,
)

from congressgov.models.base.model import ApiEnvelope

DailyCongressionalRecordModel = ModelRegistry.get_model("DailyCongressionalRecord")
DailyCongressionalRecordIssueModel = ModelRegistry.get_model("DailyCongressionalRecordIssue")
DailyCongressionalRecordArticlesModel = ModelRegistry.get_model("DailyCongressionalRecordArticles")

ASYNC_DAILY_CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = ["AsyncDailyCongressionalRecord", "ASYNC_DAILY_CONGRESSIONAL_RECORD_MAPPINGS"]


def _parse_api_payload(response, model_cls):
    response_json = json.loads(response.content)
    api_envelope = ApiEnvelope.model_validate(response_json)
    payload = api_envelope.data if api_envelope.data is not None else response_json
    return model_cls.model_validate(payload)


class AsyncDailyCongressionalRecord(AsyncApiService):
    """Async daily Congressional Record API."""

    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordModel:
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await daily_congressional_record_list_detailed(
            client=resolved_client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordModel)
        result.client = resolved_client
        self._last_result = result
        return result

    async def get_volume(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordModel:
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await daily_congressional_record_volume_detailed(
            client=resolved_client,
            volume_number=volume_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordModel)
        result.client = resolved_client
        self._last_result = result
        return result

    async def get_issue(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        issue_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordIssueModel:
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await daily_congressional_record_issue_detailed(
            client=resolved_client,
            volume_number=volume_number,
            issue_number=issue_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordIssueModel)
        result.client = resolved_client
        self._last_result = result
        return result

    async def get_articles(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        issue_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordArticlesModel:
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await daily_congressional_record_articles_detailed(
            client=resolved_client,
            volume_number=volume_number,
            issue_number=issue_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordArticlesModel)
        result.client = resolved_client
        return result
