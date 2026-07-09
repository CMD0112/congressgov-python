"""Async extension methods for Committee model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.extensions._async_helpers import resolve_client, call_api_async
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.models.committees.committee import Committee

BillsModel = ModelRegistry.get_model("Bills")
CommitteeReportsModel = ModelRegistry.get_model("CommitteeReports")
HouseCommunicationsModel = ModelRegistry.get_model("HouseCommunications")
SenateCommunicationsModel = ModelRegistry.get_model("SenateCommunications")
NominationsModel = ModelRegistry.get_model("Nominations")


def _committee_ids(self: Committee) -> tuple[Any, Any]:
    chamber = getattr(self, "chamber", None)
    committee_code = getattr(self, "committee_code", getattr(self, "committeeCode", None))
    return chamber, committee_code


def _get_async_committee_config():
    from congressgov.services.async_api.committee import ASYNC_COMMITTEE_MAPPINGS, ASYNC_COMMITTEE_PARAMETERS
    return ASYNC_COMMITTEE_MAPPINGS, ASYNC_COMMITTEE_PARAMETERS


@register_async_method(Committee)
async def expand_async(
    self: Committee,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Committee:
    mappings, param_spec = _get_async_committee_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
    )
    return result.expanded_target


@register_async_method(Committee)
async def get_bills_async(self: Committee, client: Any = None, **kwargs: Any):
    from congressgov._client.api.committee import committee_bills_list_async
    resolved = await resolve_client(self, client)
    chamber, committee_code = _committee_ids(self)
    return await call_api_async(
        committee_bills_list_async,
        BillsModel,
        client=resolved,
        chamber=chamber,
        committee_code=committee_code,
        **kwargs,
    )


@register_async_method(Committee)
async def get_reports_async(self: Committee, client: Any = None, **kwargs: Any):
    from congressgov._client.api.committee import committee_reports_by_committee_async
    resolved = await resolve_client(self, client)
    chamber, committee_code = _committee_ids(self)
    return await call_api_async(
        committee_reports_by_committee_async,
        CommitteeReportsModel,
        client=resolved,
        chamber=chamber,
        committee_code=committee_code,
        **kwargs,
    )


@register_async_method(Committee)
async def get_house_communications_async(self: Committee, client: Any = None, **kwargs: Any):
    from congressgov._client.api.committee import house_communications_by_committee_async
    resolved = await resolve_client(self, client)
    chamber, committee_code = _committee_ids(self)
    return await call_api_async(
        house_communications_by_committee_async,
        HouseCommunicationsModel,
        client=resolved,
        chamber=chamber,
        committee_code=committee_code,
        **kwargs,
    )


@register_async_method(Committee)
async def get_senate_communications_async(self: Committee, client: Any = None, **kwargs: Any):
    from congressgov._client.api.committee import senate_communications_by_committee_async
    resolved = await resolve_client(self, client)
    chamber, committee_code = _committee_ids(self)
    return await call_api_async(
        senate_communications_by_committee_async,
        SenateCommunicationsModel,
        client=resolved,
        chamber=chamber,
        committee_code=committee_code,
        **kwargs,
    )


@register_async_method(Committee)
async def get_nominations_async(self: Committee, client: Any = None, **kwargs: Any):
    from congressgov._client.api.committee import nomination_by_committee_async
    resolved = await resolve_client(self, client)
    chamber, committee_code = _committee_ids(self)
    return await call_api_async(
        nomination_by_committee_async,
        NominationsModel,
        client=resolved,
        chamber=chamber,
        committee_code=committee_code,
        **kwargs,
    )
