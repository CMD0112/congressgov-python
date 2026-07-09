"""SQLite-backed request store (default persistent backend)."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterator

from ..models import StoredResponse
from ..policy import PolicyConfig
from ..schema import apply_migrations
from .base import purge_stale_records


class SQLiteRequestStoreBackend:
    """Persistent SQLite backend implementing :class:`RequestStoreBackend`."""

    def __init__(self, connection: str | Path) -> None:
        path = str(connection)
        if path.startswith("sqlite:///"):
            path = path[len("sqlite:///") :]
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            apply_migrations(self._conn)

    def _row_to_stored(self, row: sqlite3.Row) -> StoredResponse:
        source_updated_at = row["source_updated_at"]
        return StoredResponse.from_record(
            {
                "status_code": row["status_code"],
                "headers": json.loads(row["headers"]),
                "body": row["body"],
                "fetched_at": row["fetched_at"],
                "policy": row["policy"],
                "request_key": row["request_key"],
                "source_updated_at": source_updated_at,
            }
        )

    def get(self, key: str) -> StoredResponse | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM api_responses WHERE request_key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_stored(row)

    def put(self, key: str, response: StoredResponse) -> None:
        record = response.to_record()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO api_responses (
                    request_key, method, url, status_code, headers, body,
                    fetched_at, policy, source_updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_key) DO UPDATE SET
                    status_code = excluded.status_code,
                    headers = excluded.headers,
                    body = excluded.body,
                    fetched_at = excluded.fetched_at,
                    policy = excluded.policy,
                    source_updated_at = excluded.source_updated_at
                """,
                (
                    key,
                    key.split(":", 1)[0],
                    key.split(":", 1)[1].split("?", 1)[0],
                    record["status_code"],
                    json.dumps(record["headers"]),
                    record["body"],
                    record["fetched_at"],
                    record["policy"],
                    record["source_updated_at"],
                ),
            )
            self._conn.commit()

    def delete(self, key: str) -> bool:
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM api_responses WHERE request_key = ?",
                (key,),
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def contains(self, key: str) -> bool:
        with self._lock:
            row = self._conn.execute(
                "SELECT 1 FROM api_responses WHERE request_key = ? LIMIT 1",
                (key,),
            ).fetchone()
        return row is not None

    def count(self) -> int:
        with self._lock:
            row = self._conn.execute("SELECT COUNT(*) AS c FROM api_responses").fetchone()
        return int(row["c"]) if row else 0

    def list_keys(
        self,
        *,
        url_prefix: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        query = "SELECT request_key FROM api_responses"
        params: list[Any] = []
        if url_prefix:
            query += " WHERE url LIKE ?"
            params.append(f"{url_prefix}%")
        query += " ORDER BY fetched_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [str(row["request_key"]) for row in rows]

    def iter_records(self) -> Iterator[StoredResponse]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM api_responses ORDER BY fetched_at DESC"
            ).fetchall()
        for row in rows:
            yield self._row_to_stored(row)

    def purge_stale(
        self,
        *,
        policy: PolicyConfig | None = None,
    ) -> int:
        return purge_stale_records(self, list(self.iter_records()), policy=policy)

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            schema_row = self._conn.execute(
                "SELECT version FROM schema_version LIMIT 1"
            ).fetchone()
        return {
            "backend": "sqlite",
            "path": str(self._path),
            "records": self.count(),
            "schema_version": int(schema_row["version"]) if schema_row else None,
        }
