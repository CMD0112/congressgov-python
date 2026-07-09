"""Async extension methods for CommitteePrint instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.models.documents.prints import CommitteePrint
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.expansion_helpers import assign_collection_items_to_attribute
from congressgov.services.extensions._async_helpers import resolve_client


def _get_async_committee_print_config():
    from congressgov.services.async_api.committee_print import (
        ASYNC_COMMITTEE_PRINT_MAPPINGS,
        ASYNC_COMMITTEE_PRINT_PARAMETERS,
    )
    return ASYNC_COMMITTEE_PRINT_MAPPINGS, ASYNC_COMMITTEE_PRINT_PARAMETERS


async def _normalize_committee_print_text_async(
    committee_print: CommitteePrint, client: Any = None
) -> None:
    value = getattr(committee_print, "text", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = await AsyncApiService._resolve_client(committee_print, client)
    assign_collection_items_to_attribute(
        committee_print,
        attribute_name="text",
        wrapper=value,
        items_field="text",
        client=resolved_client,
    )


@register_async_method(CommitteePrint)
async def expand_async(
    self: CommitteePrint,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> CommitteePrint:
    mappings, param_spec = _get_async_committee_print_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
        normalize_params=["chamber"],
        **kwargs,
    )
    await _normalize_committee_print_text_async(result.expanded_target, client)
    return result.expanded_target


@register_async_method(CommitteePrint)
async def get_text_async(self: CommitteePrint, client: Any = None, **kwargs: Any) -> Any:
    from congressgov.services.async_api.committee_print import AsyncCommitteePrint

    resolved = await resolve_client(self, client)
    service = AsyncCommitteePrint(client=resolved)
    items = await service.get_text(
        client=client,
        congress=self.congress,
        chamber=self.chamber,
        jacket_number=self.jacketNumber,
        **kwargs,
    )
    text_list = items if isinstance(items, list) else [items]
    if resolved is not None:
        for item in text_list:
            if getattr(item, "client", None) is None:
                item.client = resolved
    self.text = text_list
    return self.text
