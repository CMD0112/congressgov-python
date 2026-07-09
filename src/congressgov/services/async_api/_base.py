"""Shared helpers for async congressgov.services API wrappers."""

from __future__ import annotations

import json
from typing import Any, TypeVar

from congressgov.models.base.model import ApiEnvelope

T = TypeVar("T")


def parse_api_envelope(content: bytes | str) -> ApiEnvelope:
    """Parse an httpx response body into an ApiEnvelope."""
    if isinstance(content, bytes):
        content = content.decode()
    return ApiEnvelope.model_validate(json.loads(content))


def parse_model_from_envelope(
    resp: Any,
    model_cls: type[T],
    *,
    data_key: str | None = None,
) -> T:
    """Parse a Pydantic model from an API response."""
    api_env = parse_api_envelope(resp.content)
    data = api_env.data
    if data_key is not None:
        data = data.get(data_key) if isinstance(data, dict) else data
    return model_cls.model_validate(data)
