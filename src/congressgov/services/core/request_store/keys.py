"""Canonical request-key generation for API deduplication."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlparse

import httpx

from .models import RequestKey

# Query params that do not affect response identity.
_STRIP_PARAMS = frozenset({"api_key", "apiKey", "X-Api-Key"})


def normalize_query(params: dict[str, Any] | list[tuple[str, Any]]) -> tuple[tuple[str, str], ...]:
    """Return sorted, normalized query pairs for key generation."""
    if isinstance(params, dict):
        items = params.items()
    else:
        items = params
    normalized: list[tuple[str, str]] = []
    for key, value in items:
        if key in _STRIP_PARAMS or value is None:
            continue
        normalized.append((str(key), str(value)))
    return tuple(sorted(normalized))


def request_key_from_httpx(request: httpx.Request) -> RequestKey:
    """Build a :class:`RequestKey` from an outgoing httpx request."""
    parsed = urlparse(str(request.url))
    path = parsed.path or "/"
    query = normalize_query(parse_qsl(parsed.query, keep_blank_values=True))
    return RequestKey(method=request.method, url=path, query=query)


def request_key_digest(request: httpx.Request) -> str:
    """Digest string for storage lookup."""
    return request_key_from_httpx(request).digest()
