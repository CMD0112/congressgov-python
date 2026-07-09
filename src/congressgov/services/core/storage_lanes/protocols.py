"""Storage lane taxonomy and protocols."""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable


class StorageLane(str, Enum):
    """Fixed storage lanes for the Congress.gov workspace."""

    BLOB = "blob"
    RECORD = "record"
    TABLE = "table"
    ARTIFACT = "artifact"
    CACHE = "cache"


@runtime_checkable
class BlobLane(Protocol):
    """Raw HTTP response persistence (request store)."""

    def close(self) -> None: ...

    def get_stats(self) -> dict[str, Any]: ...


@runtime_checkable
class RecordLane(Protocol):
    """Versioned JSON/Pydantic document stores."""

    def save(self) -> None: ...

    def stats(self) -> dict[str, Any]: ...


@runtime_checkable
class TableLane(Protocol):
    """Queryable model collections."""

    def save(self, data: Any, **options: Any) -> int: ...

    def load(self, **options: Any) -> list[Any]: ...


@runtime_checkable
class ArtifactLane(Protocol):
    """Immutable export outputs with optional manifest."""

    def write(self, name: str, content: bytes | str, *, metadata: dict[str, Any] | None = None) -> str: ...


@runtime_checkable
class CacheLane(Protocol):
    """Ephemeral TTL key-value overlay."""

    def get(self, key: str) -> Any: ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool: ...
