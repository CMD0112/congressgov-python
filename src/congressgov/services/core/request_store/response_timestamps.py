"""Extract source update timestamps from Congress.gov API JSON payloads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from dateutil import parser as date_parser

_TIMESTAMP_KEYS = (
    "updateDate",
    "updateDateTime",
    "lastModified",
    "lastUpdated",
    "date",
)


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = date_parser.parse(value)
        except (ValueError, TypeError):
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def _walk_for_timestamp(node: Any, *, depth: int = 0) -> datetime | None:
    if depth > 6:
        return None
    if isinstance(node, dict):
        for key in _TIMESTAMP_KEYS:
            if key in node:
                parsed = _parse_timestamp(node[key])
                if parsed is not None:
                    return parsed
        for value in node.values():
            found = _walk_for_timestamp(value, depth=depth + 1)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node[:20]:
            found = _walk_for_timestamp(item, depth=depth + 1)
            if found is not None:
                return found
    return None


def extract_source_updated_at(body: bytes) -> datetime | None:
    """Return the best available source update time from an API JSON body."""
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return _walk_for_timestamp(payload)
