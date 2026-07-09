"""Async extension methods for Nomination model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.extensions._async_helpers import resolve_client, call_api_async
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.models.nominations.nomination import Nomination

ActionsModel = ModelRegistry.get_model("Actions")
CommitteesModel = ModelRegistry.get_model("Committees")
HearingsModel = ModelRegistry.get_model("Hearings")


def _nomination_ids(self: Nomination) -> tuple[Any, Any]:
    congress = getattr(self, "congress", None)
    nomination_number = getattr(self, "nomination_number", getattr(self, "number", None))
    return congress, nomination_number


def _get_async_nomination_config():
    from congressgov.services.async_api.nomination import ASYNC_NOMINATION_MAPPINGS, ASYNC_NOMINATION_PARAMETERS
    return ASYNC_NOMINATION_MAPPINGS, ASYNC_NOMINATION_PARAMETERS


@register_async_method(Nomination)
async def expand_async(
    self: Nomination,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Nomination:
    mappings, param_spec = _get_async_nomination_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
    )
    return result.expanded_target


@register_async_method(Nomination)
async def get_actions_async(self: Nomination, client: Any = None, **kwargs: Any):
    from congressgov._client.api.nomination import nomination_actions_async
    resolved = await resolve_client(self, client)
    congress, nomination_number = _nomination_ids(self)
    return await call_api_async(
        nomination_actions_async,
        ActionsModel,
        client=resolved,
        congress=congress,
        nomination_number=nomination_number,
        **kwargs,
    )


@register_async_method(Nomination)
async def get_committees_async(self: Nomination, client: Any = None, **kwargs: Any):
    from congressgov._client.api.nomination import nomination_committees_async
    resolved = await resolve_client(self, client)
    congress, nomination_number = _nomination_ids(self)
    return await call_api_async(
        nomination_committees_async,
        CommitteesModel,
        client=resolved,
        congress=congress,
        nomination_number=nomination_number,
        **kwargs,
    )


@register_async_method(Nomination)
async def get_hearings_async(self: Nomination, client: Any = None, **kwargs: Any):
    from congressgov._client.api.nomination import nomination_hearings_async
    resolved = await resolve_client(self, client)
    congress, nomination_number = _nomination_ids(self)
    return await call_api_async(
        nomination_hearings_async,
        HearingsModel,
        client=resolved,
        congress=congress,
        nomination_number=nomination_number,
        **kwargs,
    )
