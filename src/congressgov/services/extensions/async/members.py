"""Async extension methods for Member model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.config import MAX_PAGINATION_LIMIT
from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.expansion_helpers import (
    bind_related_attribute_async,
    extract_parameters_from_target,
)
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.models.entities.member import Member

SponsoredLegislationModel = ModelRegistry.get_model("SponsoredLegislation")
CosponsoredLegislationModel = ModelRegistry.get_model("CosponsoredLegislation")


def _get_async_member_config():
    from congressgov.services.async_api.member import (
        ASYNC_MEMBER_MAPPINGS,
        ASYNC_MEMBER_PARAMETERS,
    )
    return ASYNC_MEMBER_MAPPINGS, ASYNC_MEMBER_PARAMETERS


def _member_sponsorship_params_async(member: Member) -> dict[str, Any]:
    _, param_spec = _get_async_member_config()
    return extract_parameters_from_target(member, param_spec)


def _coerce_sponsorship_limit(limit: int | str | None) -> int | None:
    """Map ``limit='max'`` to the API maximum page size (250) -- async parity with sync."""
    if limit is None:
        return None
    if isinstance(limit, str) and limit.lower() == "max":
        return MAX_PAGINATION_LIMIT
    return limit


@register_async_method(Member)
async def expand_async(
    self: Member,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Member:
    """Expand member attributes via AsyncApiService.expand."""
    mappings, param_spec = _get_async_member_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
        **kwargs,
    )
    return result.expanded_target


@register_async_method(Member)
async def expand_specific_attributes_async(
    self: Member,
    *attributes: str,
    client: Any = None,
    **kwargs: Any,
) -> Member:
    """Expand only the given attributes (varargs)."""
    return await expand_async(self, client=client, attributes=list(attributes), **kwargs)


@register_async_method(Member)
async def get_available_attributes_async(self: Member) -> list[str]:
    """List attribute names that ``expand_async()`` can populate."""
    mappings, _ = _get_async_member_config()
    return list(mappings.keys())


@register_async_method(Member)
async def get_sponsored_legislation_async(
    self: Member,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int | str = None,
    *,
    refresh: bool = False,
):
    from congressgov._client.api.member import member_sponsorship_list_async

    return await bind_related_attribute_async(
        self,
        attribute_name="sponsoredLegislation",
        model_class=SponsoredLegislationModel,
        api_function=member_sponsorship_list_async,
        client=client,
        api_params=_member_sponsorship_params_async(self),
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=_coerce_sponsorship_limit(limit),
    )


@register_async_method(Member)
async def get_cosponsored_legislation_async(
    self: Member,
    client: Any = None,
    format_: str = None,
    offset: int = None,
    limit: int | str = None,
    *,
    refresh: bool = False,
):
    from congressgov._client.api.member import member_cosponsorship_list_async

    return await bind_related_attribute_async(
        self,
        attribute_name="cosponsoredLegislation",
        model_class=CosponsoredLegislationModel,
        api_function=member_cosponsorship_list_async,
        client=client,
        api_params=_member_sponsorship_params_async(self),
        refresh=refresh,
        format_=format_,
        offset=offset,
        limit=_coerce_sponsorship_limit(limit),
    )
