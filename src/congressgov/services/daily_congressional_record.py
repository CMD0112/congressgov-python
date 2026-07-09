from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record import (
    sync_detailed as daily_congressional_record_list_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number import (
    sync_detailed as daily_congressional_record_volume_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number_issue_number import (
    sync_detailed as daily_congressional_record_issue_detailed,
)
from congressgov._client.api.daily_congressional_record.get_daily_congressional_record_volume_number_issue_number_articles import (
    sync_detailed as daily_congressional_record_articles_detailed,
)

from congressgov.models.base.model import ApiEnvelope

DailyCongressionalRecordModel = ModelRegistry.get_model("DailyCongressionalRecord")
DailyCongressionalRecordIssueModel = ModelRegistry.get_model("DailyCongressionalRecordIssue")
DailyCongressionalRecordArticlesModel = ModelRegistry.get_model("DailyCongressionalRecordArticles")

DAILY_CONGRESSIONAL_RECORD_MAPPINGS = {}

__all__ = [
    "DailyCongressionalRecord",
    "DAILY_CONGRESSIONAL_RECORD_MAPPINGS",
]


def _parse_api_payload(response, model_cls):
    response_json = json.loads(response.content)
    api_envelope = ApiEnvelope.model_validate(response_json)
    payload = api_envelope.data if api_envelope.data is not None else response_json
    result = model_cls.model_validate(payload)
    return result


class DailyCongressionalRecord(ApiService):
    """Daily Congressional Record API (volume / issue / articles), distinct from bound record search."""

    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordModel:
        """List daily Congressional Record issues (most recent first)."""
        # CUSTOM: direct list via ApiEnvelope
        client = ApiService._resolve_client(self, client)
        response = daily_congressional_record_list_detailed(
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordModel)
        result.client = client
        self._last_result = result
        return result

    def get_volume(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordModel:
        """List daily Congressional Record issues for a volume."""
        # CUSTOM: volume sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = daily_congressional_record_volume_detailed(
            client=client,
            volume_number=volume_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordModel)
        result.client = client
        self._last_result = result
        return result

    def get_issue(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        issue_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordIssueModel:
        """Get a daily Congressional Record issue by volume and issue number."""
        # CUSTOM: issue sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = daily_congressional_record_issue_detailed(
            client=client,
            volume_number=volume_number,
            issue_number=issue_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordIssueModel)
        result.client = client
        self._last_result = result
        return result

    def get_articles(
        self,
        *,
        client: AuthenticatedClient | None = None,
        volume_number: int,
        issue_number: int,
        format_: str = None,
        offset: int = None,
        limit: int = None,
    ) -> DailyCongressionalRecordArticlesModel:
        """List articles for a daily Congressional Record issue."""
        # CUSTOM: articles sub-endpoint
        client = ApiService._resolve_client(self, client)
        response = daily_congressional_record_articles_detailed(
            client=client,
            volume_number=volume_number,
            issue_number=issue_number,
            format_=format_,
            offset=offset,
            limit=limit,
        )
        result = _parse_api_payload(response, DailyCongressionalRecordArticlesModel)
        result.client = client
        return result
