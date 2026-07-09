"""Data models for persisted API request/response pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestKey:
    """Canonical identity for an API request."""

    method: str
    url: str
    query: tuple[tuple[str, str], ...] = ()

    def digest(self) -> str:
        """Stable string used as the storage backend key."""
        query_part = "&".join(f"{k}={v}" for k, v in self.query)
        return f"{self.method.upper()}:{self.url}?{query_part}"


@dataclass(slots=True)
class StoredResponse:
    """Raw HTTP response persisted for a :class:`RequestKey`."""

    status_code: int
    headers: dict[str, str]
    body: bytes
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    policy: str = "moderate"
    request_key: str | None = None
    source_updated_at: datetime | None = None

    @property
    def effective_updated_at(self) -> datetime:
        """Best available timestamp for change-detection/display purposes.

        Note: TTL/staleness math (:func:`request_store.policy.estimate_staleness`)
        deliberately uses ``fetched_at`` instead, since ``source_updated_at`` reflects
        the API's own (often old) ``updateDate`` and would make freshly cached
        responses look immediately stale.
        """
        if self.source_updated_at is not None:
            return self.source_updated_at
        return self.fetched_at

    def to_record(self) -> dict[str, Any]:
        source_ts = (
            self.source_updated_at.timestamp()
            if self.source_updated_at is not None
            else None
        )
        return {
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body,
            "fetched_at": self.fetched_at.timestamp(),
            "policy": self.policy,
            "request_key": self.request_key,
            "source_updated_at": source_ts,
        }

    @classmethod
    def from_record(cls, data: dict[str, Any]) -> StoredResponse:
        fetched_at = _coerce_datetime(data.get("fetched_at"))
        source_updated_at = _coerce_datetime(data.get("source_updated_at"))
        body = data["body"]
        if isinstance(body, str):
            body = body.encode("utf-8")
        return cls(
            status_code=int(data["status_code"]),
            headers=dict(data.get("headers") or {}),
            body=body,
            fetched_at=fetched_at or datetime.now(timezone.utc),
            policy=str(data.get("policy") or "moderate"),
            request_key=data.get("request_key"),
            source_updated_at=source_updated_at,
        )


_DECODED_BODY_HEADER_SKIP = frozenset({"content-encoding", "content-length", "transfer-encoding"})


def normalize_stored_response_headers(headers: dict[str, str]) -> dict[str, str]:
    """Drop transport headers that do not match decoded cached bodies."""
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in _DECODED_BODY_HEADER_SKIP
    }


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    return None
