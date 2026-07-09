"""Redis-backed request store (optional ``redis`` extra)."""

from __future__ import annotations

import json
import threading
from typing import Any

from ..models import StoredResponse

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisRequestStoreBackend:
    """Persist responses in Redis."""

    def __init__(
        self,
        connection: str = "redis://localhost:6379/0",
        *,
        key_prefix: str = "congressgov:request_store:",
        **redis_kwargs: Any,
    ) -> None:
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis request store requires the redis package. "
                "Install with: pip install congressgov[cache]"
            )
        self._client = redis.from_url(connection, decode_responses=False, **redis_kwargs)
        self.key_prefix = key_prefix
        self._lock = threading.RLock()

    def _redis_key(self, key: str) -> str:
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> StoredResponse | None:
        with self._lock:
            raw = self._client.get(self._redis_key(key))
        if raw is None:
            return None
        data = json.loads(raw)
        return StoredResponse.from_record({**data, "request_key": key})

    def put(self, key: str, response: StoredResponse) -> None:
        record = response.to_record()
        record["request_key"] = key
        record["body"] = record["body"].decode("utf-8")
        with self._lock:
            self._client.set(self._redis_key(key), json.dumps(record).encode("utf-8"))

    def delete(self, key: str) -> bool:
        with self._lock:
            return bool(self._client.delete(self._redis_key(key)))

    def contains(self, key: str) -> bool:
        with self._lock:
            return bool(self._client.exists(self._redis_key(key)))

    def count(self) -> int:
        with self._lock:
            return sum(1 for _ in self._client.scan_iter(f"{self.key_prefix}*"))

    def close(self) -> None:
        with self._lock:
            self._client.close()

    def get_stats(self) -> dict[str, Any]:
        return {"backend": "redis", "prefix": self.key_prefix, "records": self.count()}
