"""Resolve Congress.gov API URLs to typed models via generated route table."""

from __future__ import annotations

import importlib
import json
import re
from dataclasses import dataclass
from typing import Any, Union, get_args, get_origin
from urllib.parse import parse_qs, urlparse

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.expansion_helpers import normalize_param_value
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.url_routes_generated import URL_ROUTES
from congressgov.services.exceptions import UnsupportedApiUrlError

API_HOST_SUFFIX = "api.congress.gov"
V3_PREFIX = "/v3"

INT_PARAMS = frozenset({
    "congress",
    "bill_number",
    "amendment_number",
    "district",
    "vote_number",
    "session",
    "nomination_number",
    "law_number",
    "report_number",
    "jacket_number",
    "requirement_number",
    "communication_number",
    "volume_number",
    "issue_number",
    "year",
    "month",
    "day",
    "ordinal",
    "event_id",
})


@dataclass(frozen=True)
class ParsedApiUrl:
    """Normalized API URL path and query parameters."""

    path: str
    query: dict[str, list[str]]


@dataclass(frozen=True)
class RouteMatch:
    """Matched route with extracted path parameters."""

    route: dict[str, Any]
    params: dict[str, Any]


def _coerce_param_value(name: str, value: str) -> Any:
    if name in INT_PARAMS:
        try:
            return int(value)
        except ValueError:
            return value
    return value


def parse_api_url(url: str) -> ParsedApiUrl:
    """
    Parse a Congress.gov API URL into a normalized ``/v3``-relative path.

    Raises:
        ValueError: If the URL is not a supported API URL.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    raw = url.strip()
    if raw.startswith("/"):
        path = raw.split("?", 1)[0]
        query_str = raw.split("?", 1)[1] if "?" in raw else ""
        query = parse_qs(query_str, keep_blank_values=False)
        path = re.sub(r"/+", "/", path)
        if not path.startswith(V3_PREFIX):
            path = f"{V3_PREFIX}{path}" if path.startswith("/") else f"{V3_PREFIX}/{path}"
        api_path = path[len(V3_PREFIX):] or "/"
        return ParsedApiUrl(path=api_path.rstrip("/") or "/", query=query)

    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower()
    if host and not host.endswith(API_HOST_SUFFIX):
        raise ValueError(
            f"Unsupported URL host {host!r}; expected {API_HOST_SUFFIX} API URLs"
        )
    path = re.sub(r"/+", "/", parsed.path or "")
    if path.startswith(V3_PREFIX):
        api_path = path[len(V3_PREFIX):]
    else:
        raise ValueError(f"URL path must include {V3_PREFIX} prefix: {url!r}")
    return ParsedApiUrl(
        path=api_path.rstrip("/") or "/",
        query=parse_qs(parsed.query or "", keep_blank_values=False),
    )


def _match_template(api_path: str, template: str) -> dict[str, Any] | None:
    path_parts = [p for p in api_path.strip("/").split("/") if p]
    template_parts = [p for p in template.strip("/").split("/") if p]
    if len(path_parts) != len(template_parts):
        return None
    params: dict[str, Any] = {}
    for segment, pattern in zip(path_parts, template_parts):
        if pattern.startswith("{") and pattern.endswith("}"):
            name = pattern[1:-1]
            params[name] = _coerce_param_value(name, segment)
        elif segment != pattern:
            return None
    return params


def match_url(url: str) -> RouteMatch:
    """
    Match a URL to the most specific registered API route.

    Raises:
        UnsupportedApiUrlError: If no route matches.
    """
    parsed = parse_api_url(url)
    for route in URL_ROUTES:
        params = _match_template(parsed.path, route["path"])
        if params is not None:
            return RouteMatch(route=route, params=params)
    raise UnsupportedApiUrlError(
        f"No API route registered for path {parsed.path!r}",
        url=url,
    )


_QUERY_KWARG_OVERRIDES = {
    # "format" shadows a builtin, so generated API functions use "format_".
    "format": "format_",
}
_INT_QUERY_PARAMS = frozenset({"offset", "limit"})
_CAMEL_CASE_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake(name: str) -> str:
    return _CAMEL_CASE_BOUNDARY.sub("_", name).lower()


def _query_to_kwargs(query: dict[str, list[str]]) -> dict[str, Any]:
    """Convert parsed query params into API-callable kwargs.

    Unrecognized keys are converted from camelCase to snake_case and forwarded
    rather than silently dropped, so any current or future query param reaches
    the generated API function (which will raise a clear TypeError if it truly
    doesn't accept it). Malformed ``offset``/``limit`` values are passed through
    as strings instead of crashing here; downstream validation reports a clearer
    error than an uncaught ``ValueError`` from URL parsing would.
    """
    kwargs: dict[str, Any] = {}
    for key, values in query.items():
        if not values:
            continue
        kwarg_name = _QUERY_KWARG_OVERRIDES.get(key, _camel_to_snake(key))
        value: Any = values[0]
        if kwarg_name in _INT_QUERY_PARAMS:
            try:
                value = int(value)
            except ValueError:
                pass
        kwargs[kwarg_name] = value
    return kwargs


def _apply_normalize_params(params: dict[str, Any], normalize: tuple[str, ...]) -> dict[str, Any]:
    out = dict(params)
    for name in normalize:
        if name in out and out[name] is not None:
            out[name] = normalize_param_value(out[name])
    return out


def _import_api_callable(package: str, name: str) -> Any:
    module = importlib.import_module(f"congressgov._client.api.{package}")
    return getattr(module, name)


def _is_list_annotation(annotation: Any) -> bool:
    if get_origin(annotation) is list:
        return True
    if get_origin(annotation) is Union:
        return any(_is_list_annotation(arg) for arg in get_args(annotation))
    return False


def _coerce_list_payload(model_class: type, data: Any) -> Any:
    """Wrap a bare-list ``data`` payload into the model's single list field.

    A few endpoints (e.g. committee print/report ``/text``) return a raw
    JSON array as ``data`` even though the resolved model is a wrapper
    object with one list field (e.g. ``CommitteePrintTexts.text``). Without
    this, ``model_class.model_validate(data)`` fails because a bare list
    can't populate a dict-shaped model.
    """
    if not isinstance(data, list):
        return data
    model_fields = getattr(model_class, "model_fields", None) or {}
    for name, field in model_fields.items():
        if _is_list_annotation(getattr(field, "annotation", None)):
            return {name: data}
    return data


def _attach_client(instance: Any, client: Any) -> Any:
    if instance is not None and client is not None:
        instance.client = client
    return instance


def _resolve_fetch_options(kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Pop store-bypass flags before forwarding kwargs to generated API callables."""
    force_fetch = bool(kwargs.pop("force_fetch", False))
    refresh = bool(kwargs.pop("refresh", False))
    return force_fetch or refresh, kwargs


def fetch_from_url(
    url: str,
    *,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """
    Fetch and parse the API resource described by a Congress.gov API URL.

    Args:
        url: Full or path-only ``api.congress.gov/v3/...`` URL.
        client: Optional API client override.
        parent: Object used to resolve ``client`` (and ``_parent_collection``).
        **kwargs: Extra parameters forwarded to the underlying API function.
            ``force_fetch`` and ``refresh`` bypass the request store for this call.

    Returns:
        Validated model instance with ``client`` attached.
    """
    from congressgov.services.core.api_service import ApiService
    from congressgov.services.core.request_store import fetch_options

    match = match_url(url)
    parsed = parse_api_url(url)
    resolved_client = ApiService._resolve_client(parent, client)

    api_fn = _import_api_callable(match.route["package"], match.route["sync"])
    params = _apply_normalize_params(match.params, tuple(match.route.get("normalize") or ()))
    should_fetch, call_kwargs = _resolve_fetch_options({**_query_to_kwargs(parsed.query), **kwargs})

    with fetch_options(force_fetch=should_fetch):
        response = api_fn(client=resolved_client, **params, **call_kwargs)
    api_envelope = ApiEnvelope.model_validate(json.loads(response.content))
    model_class = ModelRegistry.get_model(match.route["model"])
    instance = model_class.model_validate(_coerce_list_payload(model_class, api_envelope.data))
    if match.route["model"] == "Congress" and getattr(instance, "number", None) is None:
        path_congress = match.params.get("congress")
        if path_congress is not None:
            instance.number = path_congress
    return _attach_client(instance, resolved_client)


async def fetch_from_url_async(
    url: str,
    *,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Async variant of :func:`fetch_from_url`."""
    from congressgov.services.core.async_api_service import AsyncApiService
    from congressgov.services.core.request_store import fetch_options

    match = match_url(url)
    parsed = parse_api_url(url)
    resolved_client = await AsyncApiService._resolve_client(parent, client)

    api_fn = _import_api_callable(match.route["package"], match.route["async"])
    params = _apply_normalize_params(match.params, tuple(match.route.get("normalize") or ()))
    should_fetch, call_kwargs = _resolve_fetch_options({**_query_to_kwargs(parsed.query), **kwargs})

    with fetch_options(force_fetch=should_fetch):
        response = await api_fn(client=resolved_client, **params, **call_kwargs)
    api_envelope = ApiEnvelope.model_validate(json.loads(response.content))
    model_class = ModelRegistry.get_model(match.route["model"])
    instance = model_class.model_validate(_coerce_list_payload(model_class, api_envelope.data))
    if match.route["model"] == "Congress" and getattr(instance, "number", None) is None:
        path_congress = match.params.get("congress")
        if path_congress is not None:
            instance.number = path_congress
    return _attach_client(instance, resolved_client)


def extract_api_url(value: Any) -> str | None:
    """Return URL string from ``URL``, ``CountRef``, or plain string."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    url = getattr(value, "url", None)
    if url is None:
        return None
    if isinstance(url, str):
        return url
    nested = getattr(url, "url", None)
    return nested if isinstance(nested, str) else str(nested) if nested is not None else None
