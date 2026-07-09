"""Async extension methods for Treaty model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.extensions._async_helpers import resolve_client, call_api_async
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.models.entities.treaty import Treaty

ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")


def _treaty_ids(self: Treaty) -> tuple[Any, Any]:
    congress = getattr(self, "congress", None)
    treaty_number = getattr(self, "treaty_number", getattr(self, "number", None))
    return congress, treaty_number


def _get_async_treaty_config():
    from congressgov.services.async_api.treaty import ASYNC_TREATY_MAPPINGS, ASYNC_TREATY_PARAMETERS
    return ASYNC_TREATY_MAPPINGS, ASYNC_TREATY_PARAMETERS


@register_async_method(Treaty)
async def expand_async(
    self: Treaty,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Treaty:
    mappings, param_spec = _get_async_treaty_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
    )
    return result.expanded_target


@register_async_method(Treaty)
async def get_actions_async(self: Treaty, client: Any = None, **kwargs: Any):
    from congressgov._client.api.treaty import treaty_actions_async
    resolved = await resolve_client(self, client)
    congress, treaty_number = _treaty_ids(self)
    return await call_api_async(
        treaty_actions_async,
        ActionsModel,
        client=resolved,
        congress=congress,
        treaty_number=treaty_number,
        **kwargs,
    )


@register_async_method(Treaty)
async def get_committee_async(self: Treaty, client: Any = None, **kwargs: Any):
    from congressgov._client.api.treaty import treaty_committee_async
    resolved = await resolve_client(self, client)
    congress, treaty_number = _treaty_ids(self)
    return await call_api_async(
        treaty_committee_async,
        CommitteesModel,
        client=resolved,
        congress=congress,
        treaty_number=treaty_number,
        **kwargs,
    )
