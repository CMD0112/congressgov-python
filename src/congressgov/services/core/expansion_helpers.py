"""Shared helpers for sync/async attribute expansion and related-attribute fetch."""

from __future__ import annotations

import json
from typing import Any, Callable, Optional, Union

from congressgov.models.base.model import ApiEnvelope

PARENT_COLLECTION_ATTR = "_parent_collection"
PARENT_ENTITY_ATTR = "_parent_entity"
PARENT_FIELD_ATTR = "_parent_field"

# Bill detail fields that may be CountRef stubs with sub-resource URLs.
BILL_COUNT_REF_FIELDS = frozenset({
    "committees",
    "committeeReports",
    "relatedBills",
    "actions",
    "sponsors",
    "cosponsors",
    "cboCostEstimates",
    "laws",
    "notes",
    "subjects",
    "summaries",
    "titles",
    "amendments",
    "textVersions",
})

# Fetched wrapper model class name -> attribute on Bill.
FETCH_RESULT_BILL_ATTR: dict[str, str] = {
    "Actions": "actions",
    "Cosponsors": "cosponsors",
    "Summaries": "summaries",
    "Amendments": "amendments",
    "Committees": "committees",
    "Titles": "titles",
    "Subjects": "subjects",
    "TextVersions": "textVersions",
    "Bills": "relatedBills",
}


def attach_count_ref_parents(
    entity: Any,
    *,
    fields: frozenset[str] | None = None,
) -> None:
    """Link ``CountRef`` stubs on *entity* to their parent for ``.fetch()`` binding."""
    from congressgov.models.base.types import CountRef

    for name in fields or BILL_COUNT_REF_FIELDS:
        value = getattr(entity, name, None)
        if isinstance(value, CountRef):
            setattr(value, PARENT_ENTITY_ATTR, entity)
            setattr(value, PARENT_FIELD_ATTR, name)


def bind_fetch_result_to_parent(parent: Any, result: Any) -> Any:
    """Store a sub-resource fetch result on *parent* when the type is known."""
    attr = FETCH_RESULT_BILL_ATTR.get(type(result).__name__)
    if attr is not None and hasattr(parent, attr):
        setattr(parent, attr, result)
        if getattr(parent, "client", None) is not None and getattr(result, "client", None) is None:
            result.client = parent.client
    return result


def normalize_param_value(value: Any) -> Any:
    """Lowercase strings and enum-like values for API path/query parameters."""
    if value is None:
        return value
    if isinstance(value, str):
        return value.lower()
    if hasattr(value, "value"):
        return str(value.value).lower()
    return value


def extract_parameters_from_target(
    target: Any,
    parameters: Union[list[str], dict[str, Union[str, list[str]]], None],
    *,
    normalize_params: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Extract required parameters from a model instance with alias support.

    Raises ValueError if any required parameter is missing or empty.
    """
    if parameters is None:
        return {}

    if isinstance(parameters, dict):
        param_items = list(parameters.items())
    else:
        param_items = [(param, param) for param in parameters]

    extracted: dict[str, Any] = {}
    for api_param, attr_names in param_items:
        value = None
        if isinstance(attr_names, (list, tuple)):
            for alias in attr_names:
                value = getattr(target, alias, None)
                if value is not None:
                    break
        else:
            value = getattr(target, attr_names, None)
        extracted[api_param] = value

    missing = {k: v for k, v in extracted.items() if v is None}
    if missing:
        raise ValueError(
            f"Target must have all required parameters. "
            f"Found: {extracted}. "
            f"Missing or empty: {missing}"
        )

    if normalize_params:
        for param in normalize_params:
            if param in extracted:
                extracted[param] = normalize_param_value(extracted[param])

    return extracted


# Sponsorship item `type` codes that identify an amendment (vs. a bill).
AMENDMENT_LEGISLATION_TYPES = frozenset({"HAMDT", "SAMDT", "SUAMDT"})


def is_amendment_legislation_item(item: Any) -> bool:
    """True when a Sponsored/CosponsoredLegislationItem refers to an amendment.

    Shared by the sync and async ``url_follow`` extensions, which previously
    each defined their own copy of this check.
    """
    item_type = getattr(item, "type", None)
    if item_type is not None and str(item_type).upper() in AMENDMENT_LEGISLATION_TYPES:
        return True
    return getattr(item, "amendmentNumber", None) is not None


def bill_api_params(bill: Any) -> dict[str, Any]:
    """Extract normalized congress/bill_type/bill_number params from a Bill."""
    congress = getattr(bill, "congress", None)
    bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
    bill_number = getattr(bill, "bill_number", getattr(bill, "number", None))
    if isinstance(bill_type, str):
        bill_type = bill_type.lower()
    elif hasattr(bill_type, "value"):
        bill_type = str(bill_type.value).lower()
    return {
        "congress": congress,
        "bill_type": bill_type,
        "bill_number": bill_number,
    }


def bind_bill_subresource(
    bill: Any,
    *,
    attribute_name: str,
    model_class: type,
    api_function: Callable[..., Any],
    client: Any = None,
    refresh: bool = False,
    **kwargs: Any,
) -> Any:
    """Fetch a bill sub-resource via :func:`bind_related_attribute`."""
    return bind_related_attribute(
        bill,
        attribute_name=attribute_name,
        model_class=model_class,
        api_function=api_function,
        client=client,
        api_params=bill_api_params(bill),
        refresh=refresh,
        **kwargs,
    )


def is_loaded_related_attribute(value: Any, model_class: type) -> bool:
    """True when *value* is a fully fetched related model (not a CountRef stub)."""
    return isinstance(value, model_class)


def propagate_client_to_items(
    collection: Any,
    items_attr: str,
    client: Any,
) -> None:
    """Attach *client* to each item in a collection and link parent for client fallback."""
    items = getattr(collection, items_attr, None) or []
    for item in items:
        if getattr(item, "client", None) is None:
            item.client = client
        setattr(item, PARENT_COLLECTION_ATTR, collection)


def bind_related_attribute(
    entity: Any,
    *,
    attribute_name: str,
    model_class: type,
    api_function: Callable[..., Any],
    client: Any = None,
    api_params: dict[str, Any],
    force_fetch: bool = False,
    refresh: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Fetch a related sub-resource and store it on *entity* under *attribute_name*.

    Reuses an already-loaded model on the attribute unless *force_fetch* is True.
    Propagates the resolved client to both the entity and the fetched model.
    """
    from congressgov.services.core.api_service import ApiService
    from congressgov.services.core.request_store import fetch_options

    resolved_client = ApiService._resolve_client(entity, client)
    should_fetch = force_fetch or refresh

    current = getattr(entity, attribute_name, None)
    if not should_fetch and is_loaded_related_attribute(current, model_class):
        if getattr(current, "client", None) is None:
            current.client = resolved_client
        if getattr(entity, "client", None) is None:
            entity.client = resolved_client
        return current

    with fetch_options(force_fetch=should_fetch):
        response = api_function(client=resolved_client, **api_params, **kwargs)
    api_envelope = ApiEnvelope.model_validate(json.loads(response.content))
    instance = model_class.model_validate(api_envelope.data)
    instance.client = resolved_client
    setattr(entity, attribute_name, instance)
    if getattr(entity, "client", None) is None:
        entity.client = resolved_client
    return instance


async def bind_related_attribute_async(
    entity: Any,
    *,
    attribute_name: str,
    model_class: type,
    api_function: Callable[..., Any],
    client: Any = None,
    api_params: dict[str, Any],
    force_fetch: bool = False,
    refresh: bool = False,
    **kwargs: Any,
) -> Any:
    """Async variant of :func:`bind_related_attribute`."""
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.services.core.request_store import fetch_options

    resolved_client = await AsyncApiService._resolve_client(entity, client)
    should_fetch = force_fetch or refresh

    current = getattr(entity, attribute_name, None)
    if not should_fetch and is_loaded_related_attribute(current, model_class):
        if getattr(current, "client", None) is None:
            current.client = resolved_client
        if getattr(entity, "client", None) is None:
            entity.client = resolved_client
        return current

    with fetch_options(force_fetch=should_fetch):
        response = await api_function(client=resolved_client, **api_params, **kwargs)
    api_envelope = ApiEnvelope.model_validate(json.loads(response.content))
    instance = model_class.model_validate(api_envelope.data)
    instance.client = resolved_client
    setattr(entity, attribute_name, instance)
    if getattr(entity, "client", None) is None:
        entity.client = resolved_client
    return instance


def expand_sync_instance(
    target: Any,
    *,
    mapping: dict[str, dict[Any, Any]],
    parameters: Union[list[str], dict[str, Union[str, list[str]]], None],
    client: Any = None,
    attributes: Optional[list[str]] = None,
    normalize_params: Optional[list[str]] = None,
    entity_name: str = "instance",
    post_expand: Optional[Callable[[Any, Any], None]] = None,
    **kwargs: Any,
) -> Any:
    """Expand attributes on a model instance via ApiService.expand."""
    from congressgov.services.core.api_service import ApiService

    expanded = ApiService().expand(
        target=target,
        client=client,
        mapping=mapping,
        parameters=parameters,
        attributes=attributes,
        normalize_params=normalize_params,
        entity_name=entity_name,
        **kwargs,
    )
    if post_expand is not None:
        post_expand(expanded, client)
    return expanded


def assign_collection_items_to_attribute(
    entity: Any,
    *,
    attribute_name: str,
    wrapper: Any,
    items_field: str,
    client: Any = None,
) -> list[Any]:
    """Unwrap a collection model and store its item list on *entity*."""
    items = getattr(wrapper, items_field, None) or []
    if client is not None:
        for item in items:
            if getattr(item, "client", None) is None:
                item.client = client
    setattr(entity, attribute_name, items)
    return items
