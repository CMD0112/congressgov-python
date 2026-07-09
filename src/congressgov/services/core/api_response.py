"""Normalize Congress.gov API error payloads before Pydantic model validation."""

from __future__ import annotations

from typing import Any

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.exceptions import APIError


def extract_api_error_message(
    response_json: dict[str, Any],
    api_env: ApiEnvelope | None = None,
) -> str | None:
    """Return a human-readable API error string when the payload is not resource data."""
    err = response_json.get("error")
    if isinstance(err, str):
        return err

    if api_env is None:
        return None

    data = api_env.data
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        nested = data.get("error")
        if isinstance(nested, str):
            return nested
        if len(data) == 1:
            only = next(iter(data.values()))
            if isinstance(only, str):
                return only
    return None


def raise_for_envelope_detail_response(
    response: Any,
    response_json: dict[str, Any],
    api_env: ApiEnvelope,
    *,
    resource_label: str,
    identifiers: dict[str, Any] | None = None,
) -> None:
    """Raise APIError when a detail GET returned HTTP errors or a string error body."""
    status_code = getattr(response, "status_code", None)
    body_snippet: str | None = None
    content = getattr(response, "content", None)
    if content is not None:
        body_snippet = (
            content.decode(errors="replace")[:500]
            if isinstance(content, bytes)
            else str(content)[:500]
        )

    err_msg = extract_api_error_message(response_json, api_env)
    id_suffix = ""
    if identifiers:
        id_suffix = f" ({', '.join(f'{k}={v}' for k, v in identifiers.items())})"

    if status_code is not None and status_code != 200:
        message = err_msg or f"{resource_label} request failed with HTTP {status_code}"
        raise APIError(
            f"{message}{id_suffix}",
            status_code=status_code,
            response_body=body_snippet or err_msg,
        )

    if err_msg:
        raise APIError(
            f"{err_msg}{id_suffix}",
            status_code=status_code or 404,
            response_body=body_snippet or err_msg,
        )
