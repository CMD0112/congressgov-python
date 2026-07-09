"""Directory-based file backend for the request store."""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any, Iterator

from ..models import StoredResponse
from ..policy import PolicyConfig
from .base import purge_stale_records


class FileRequestStoreBackend:
    """Persist responses as JSON files under a directory (stdlib only)."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _path_for_key(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.directory / f"{digest}.json"

    def get(self, key: str) -> StoredResponse | None:
        path = self._path_for_key(key)
        with self._lock:
            if not path.exists():
                return None
            data = json.loads(path.read_text(encoding="utf-8"))
        body = data["body"]
        if isinstance(body, str):
            body = body.encode("utf-8")
        return StoredResponse.from_record({**data, "body": body, "request_key": key})

    def put(self, key: str, response: StoredResponse) -> None:
        record = response.to_record()
        record["request_key"] = key
        record["body"] = record["body"].decode("utf-8")
        path = self._path_for_key(key)
        tmp = path.with_suffix(".tmp")
        with self._lock:
            tmp.write_text(json.dumps(record), encoding="utf-8")
            tmp.replace(path)

    def delete(self, key: str) -> bool:
        path = self._path_for_key(key)
        with self._lock:
            if path.exists():
                path.unlink()
                return True
            return False

    def contains(self, key: str) -> bool:
        with self._lock:
            return self._path_for_key(key).exists()

    def count(self) -> int:
        with self._lock:
            return sum(1 for _ in self.directory.glob("*.json"))

    def list_keys(
        self,
        *,
        url_prefix: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        keys: list[str] = []
        with self._lock:
            paths = sorted(self.directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            key = str(data.get("request_key") or "")
            if not key:
                continue
            if url_prefix and url_prefix not in key:
                continue
            keys.append(key)
        return keys[offset : offset + limit]

    def iter_records(self) -> Iterator[StoredResponse]:
        with self._lock:
            paths = list(self.directory.glob("*.json"))
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            key = str(data.get("request_key") or "")
            body = data["body"]
            if isinstance(body, str):
                body = body.encode("utf-8")
            yield StoredResponse.from_record({**data, "body": body, "request_key": key})

    def purge_stale(self, *, policy: PolicyConfig | None = None) -> int:
        return purge_stale_records(self, list(self.iter_records()), policy=policy)

    def close(self) -> None:
        return None

    def get_stats(self) -> dict[str, Any]:
        return {"backend": "file", "path": str(self.directory), "records": self.count()}
