"""Async extension methods for Bill model instances."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.expansion_helpers import (
    assign_collection_items_to_attribute,
    bill_api_params,
    bind_related_attribute_async,
)
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.extensions._async_helpers import resolve_client
from congressgov.models.base.types import CountRef
from congressgov.models.entities.bill import Bill

from congressgov.services.core.model_registry import ModelRegistry

ActionsModel = ModelRegistry.get_model("Actions")
AmendmentsModel = ModelRegistry.get_model("Amendments")
CommitteesModel = ModelRegistry.get_model("Committees")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
BillsModel = ModelRegistry.get_model("Bills")
SubjectModel = ModelRegistry.get_model("Subject")
SummariesModel = ModelRegistry.get_model("Summaries")
TextVersionsModel = ModelRegistry.get_model("TextVersions")
TitlesModel = ModelRegistry.get_model("Titles")


def _get_async_bill_config():
    from congressgov.services.async_api.bill import ASYNC_BILL_MAPPINGS, ASYNC_BILL_PARAMETERS
    return ASYNC_BILL_MAPPINGS, ASYNC_BILL_PARAMETERS


async def _normalize_bill_amendments_async(bill: Bill, client: Any = None) -> None:
    value = getattr(bill, "amendments", None)
    if value is None or isinstance(value, list):
        return
    resolved_client = await AsyncApiService._resolve_client(bill, client)
    assign_collection_items_to_attribute(
        bill,
        attribute_name="amendments",
        wrapper=value,
        items_field="amendments",
        client=resolved_client,
    )


async def _post_expand_bill_async(bill: Bill, client: Any = None) -> None:
    await _normalize_bill_amendments_async(bill, client)


async def _bind_bill_subresource_async(
    bill: Bill,
    *,
    attribute_name: str,
    model_class: type,
    api_function: Any,
    client: Any = None,
    refresh: bool = False,
    **kwargs: Any,
) -> Any:
    """Async counterpart of the sync ``bind_bill_subresource`` helper.

    Reuses an already-loaded sub-resource on ``bill`` unless ``refresh`` is set,
    and binds the fetched result back onto the bill instance -- parity gaps the
    async getters previously had against their sync counterparts.
    """
    return await bind_related_attribute_async(
        bill,
        attribute_name=attribute_name,
        model_class=model_class,
        api_function=api_function,
        client=client,
        api_params=bill_api_params(bill),
        refresh=refresh,
        **kwargs,
    )


@register_async_method(Bill)
async def expand_async(
    self: Bill,
    client: Any = None,
    attributes: Optional[list[str]] = None,
    **kwargs: Any,
) -> Bill:
    mappings, param_spec = _get_async_bill_config()
    result = await AsyncApiService.expand(
        target=deepcopy(self),
        client=client,
        mapping=mappings,
        parameters=param_spec,
        attributes=attributes,
        normalize_params=["bill_type"],
        **kwargs,
    )
    await _post_expand_bill_async(result.expanded_target, client)
    return result.expanded_target


@register_async_method(Bill)
async def expand_specific_attributes_async(
    self: Bill,
    *attributes: str,
    client: Any = None,
    **kwargs: Any,
) -> Bill:
    return await expand_async(self, client=client, attributes=list(attributes), **kwargs)


@register_async_method(Bill)
async def get_actions_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_actions_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="actions",
        model_class=ActionsModel,
        api_function=bill_actions_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_amendments_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_amendments_async

    # `bill.amendments` is stored as list[Amendment] (not the Amendments
    # wrapper), so reuse must check for an already-normalized list first,
    # matching sync `get_amendments`'s cache-reuse behavior.
    current = getattr(self, "amendments", None)
    if not refresh and current is not None and not isinstance(current, CountRef):
        if isinstance(current, list):
            return current
        resolved = await resolve_client(self, client)
        return assign_collection_items_to_attribute(
            self,
            attribute_name="amendments",
            wrapper=current,
            items_field="amendments",
            client=resolved,
        )

    wrapper = await _bind_bill_subresource_async(
        self,
        attribute_name="amendments",
        model_class=AmendmentsModel,
        api_function=bill_amendments_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )
    resolved = await resolve_client(self, client)
    return assign_collection_items_to_attribute(
        self,
        attribute_name="amendments",
        wrapper=wrapper,
        items_field="amendments",
        client=resolved,
    )


@register_async_method(Bill)
async def get_committees_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_committees_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="committees",
        model_class=CommitteesModel,
        api_function=bill_committees_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_cosponsors_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_cosponsors_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="cosponsors",
        model_class=CosponsorsModel,
        api_function=bill_cosponsors_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_related_bills_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_relatedbills_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="relatedBills",
        model_class=BillsModel,
        api_function=bill_relatedbills_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_subjects_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_subjects_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="subjects",
        model_class=SubjectModel,
        api_function=bill_subjects_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_summaries_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_summaries_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="summaries",
        model_class=SummariesModel,
        api_function=bill_summaries_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_text_versions_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_text_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="textVersions",
        model_class=TextVersionsModel,
        api_function=bill_text_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )


@register_async_method(Bill)
async def get_titles_async(
    self: Bill, client: Any = None, format_: str | None = None, refresh: bool = False, **kwargs: Any
):
    from congressgov._client.api.bill import bill_titles_async

    return await _bind_bill_subresource_async(
        self,
        attribute_name="titles",
        model_class=TitlesModel,
        api_function=bill_titles_async,
        client=client,
        refresh=refresh,
        format_=format_,
        **kwargs,
    )
