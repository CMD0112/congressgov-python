"""Async extension methods for CommitteeReport instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.models.documents.reports import CommitteeReport
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.expansion_helpers import assign_collection_items_to_attribute
from congressgov.services.extensions._async_helpers import resolve_client


def _get_async_committee_report_config():
    from congressgov.services.async_api.committee_report import (
        ASYNC_COMMITTEE_REPORT_MAPPINGS,
        ASYNC_COMMITTEE_REPORT_PARAMETERS,
    )
    return ASYNC_COMMITTEE_REPORT_MAPPINGS, ASYNC_COMMITTEE_REPORT_PARAMETERS


async def _normalize_committee_report_text_async(
    report: CommitteeReport, client: Any = None
) -> None:
    value = getattr(report, "text", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = await AsyncApiService._resolve_client(report, client)
    assign_collection_items_to_attribute(
        report,
        attribute_name="text",
        wrapper=value,
        items_field="text",
        client=resolved_client,
    )


@register_async_method(CommitteeReport)
async def expand_async(
    self: CommitteeReport,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> CommitteeReport:
    mappings, param_spec = _get_async_committee_report_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
        normalize_params=["report_type"],
        **kwargs,
    )
    await _normalize_committee_report_text_async(result.expanded_target, client)
    return result.expanded_target


@register_async_method(CommitteeReport)
async def get_text_async(self: CommitteeReport, client: Any = None, **kwargs: Any) -> Any:
    from congressgov.services.async_api.committee_report import AsyncCommitteeReport

    resolved = await resolve_client(self, client)
    service = AsyncCommitteeReport(client=resolved)
    items = await service.get_text(
        client=client,
        congress=self.congress,
        report_type=getattr(self, "type", None),
        report_number=self.number,
        **kwargs,
    )
    text_list = items if isinstance(items, list) else [items]
    if resolved is not None:
        for item in text_list:
            if getattr(item, "client", None) is None:
                item.client = resolved
    self.text = text_list
    return self.text
