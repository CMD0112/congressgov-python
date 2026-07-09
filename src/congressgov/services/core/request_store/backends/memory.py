"""In-memory request store backend (tests and ephemeral sessions)."""

from __future__ import annotations

import threading
from typing import Any, Iterator

from ..models import StoredResponse
from ..policy import PolicyConfig
from .base import purge_stale_records


class MemoryRequestStoreBackend:
    """Thread-safe in-memory backend implementing :class:`RequestStoreBackend`."""

    def __init__(self) -> None:
        self._data: dict[str, StoredResponse] = {}
        self._lock = threading.RLock()
        self._stats = {"gets": 0, "puts": 0, "hits": 0, "misses": 0}

    def get(self, key: str) -> StoredResponse | None:
        with self._lock:
            self._stats["gets"] += 1
            value = self._data.get(key)
            if value is None:
                self._stats["misses"] += 1
                return None
            self._stats["hits"] += 1
            return value

    def put(self, key: str, response: StoredResponse) -> None:
        with self._lock:
            self._data[key] = response
            self._stats["puts"] += 1

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._data.pop(key, None) is not None

    def contains(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def count(self) -> int:
        with self._lock:
            return len(self._data)

    def list_keys(
        self,
        *,
        url_prefix: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        with self._lock:
            keys = list(self._data.keys())
        if url_prefix:
            keys = [k for k in keys if url_prefix in k]
        return keys[offset : offset + limit]

    def iter_records(self) -> Iterator[StoredResponse]:
        with self._lock:
            values = list(self._data.values())
        yield from values

    def purge_stale(self, *, policy: PolicyConfig | None = None) -> int:
        with self._lock:
            records = list(self._data.values())
        return purge_stale_records(self, records, policy=policy)

    def close(self) -> None:
        with self._lock:
            self._data.clear()

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            return {**self._stats, "records": len(self._data)}
