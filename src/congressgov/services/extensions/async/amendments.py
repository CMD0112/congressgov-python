"""Async extension methods for Amendment model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.extensions._async_helpers import resolve_client, call_api_async
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.models.entities.amendment import Amendment

ActionsModel = ModelRegistry.get_model("Actions")
AmendmentsModel = ModelRegistry.get_model("Amendments")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
TextVersionsModel = ModelRegistry.get_model("TextVersions")


def _amendment_ids(self: Amendment) -> tuple[Any, Any, Any]:
    congress = getattr(self, "congress", None)
    amendment_type = getattr(self, "amendment_type", getattr(self, "type", None))
    amendment_number = getattr(self, "amendment_number", getattr(self, "number", None))
    if isinstance(amendment_type, str):
        amendment_type = amendment_type.lower()
    elif hasattr(amendment_type, "value"):
        amendment_type = str(amendment_type.value).lower()
    return congress, amendment_type, amendment_number


def _get_async_amendment_config():
    from congressgov.services.async_api.amendment import ASYNC_AMENDMENT_MAPPINGS, ASYNC_AMENDMENT_PARAMETERS
    return ASYNC_AMENDMENT_MAPPINGS, ASYNC_AMENDMENT_PARAMETERS


@register_async_method(Amendment)
async def expand_async(
    self: Amendment,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Amendment:
    mappings, param_spec = _get_async_amendment_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
        normalize_params=["amendment_type"],
        **kwargs,
    )
    return result.expanded_target


@register_async_method(Amendment)
async def get_actions_async(self: Amendment, client: Any = None, **kwargs: Any):
    from congressgov._client.api.amendments import amendment_actions_async
    resolved = await resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)
    return await call_api_async(
        amendment_actions_async,
        ActionsModel,
        client=resolved,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs,
    )


@register_async_method(Amendment)
async def get_amendments_async(self: Amendment, client: Any = None, **kwargs: Any):
    from congressgov._client.api.amendments import amendment_amendments_async
    resolved = await resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)
    return await call_api_async(
        amendment_amendments_async,
        AmendmentsModel,
        client=resolved,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs,
    )


@register_async_method(Amendment)
async def get_cosponsors_async(self: Amendment, client: Any = None, **kwargs: Any):
    from congressgov._client.api.amendments import amendment_cosponsors_async
    resolved = await resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)
    return await call_api_async(
        amendment_cosponsors_async,
        CosponsorsModel,
        client=resolved,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs,
    )


@register_async_method(Amendment)
async def get_text_versions_async(self: Amendment, client: Any = None, **kwargs: Any):
    from congressgov._client.api.amendments import amendment_text_async
    resolved = await resolve_client(self, client)
    congress, amendment_type, amendment_number = _amendment_ids(self)
    return await call_api_async(
        amendment_text_async,
        TextVersionsModel,
        client=resolved,
        congress=congress,
        amendment_type=amendment_type,
        amendment_number=amendment_number,
        **kwargs,
    )
