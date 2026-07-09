"""SQLite schema versioning and migrations for the request store."""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 2

_INITIAL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS api_responses (
    request_key TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    headers TEXT NOT NULL,
    body BLOB NOT NULL,
    fetched_at REAL NOT NULL,
    policy TEXT NOT NULL,
    source_updated_at REAL
);
CREATE INDEX IF NOT EXISTS idx_api_responses_fetched_at ON api_responses(fetched_at);
CREATE INDEX IF NOT EXISTS idx_api_responses_url ON api_responses(url);
"""

_MIGRATIONS: dict[int, str] = {
    2: "ALTER TABLE api_responses ADD COLUMN source_updated_at REAL;",
}


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def apply_migrations(conn: sqlite3.Connection) -> int:
    """Ensure the database schema is at :data:`SCHEMA_VERSION`. Returns final version."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
    )
    row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()

    if row is None:
        if _table_exists(conn, "api_responses"):
            current = 1
            conn.execute("INSERT INTO schema_version(version) VALUES (?)", (current,))
        else:
            conn.executescript(_INITIAL)
            conn.execute("DELETE FROM schema_version")
            conn.execute(
                "INSERT INTO schema_version(version) VALUES (?)",
                (SCHEMA_VERSION,),
            )
            conn.commit()
            return SCHEMA_VERSION
    else:
        current = int(row[0])

    while current < SCHEMA_VERSION:
        next_version = current + 1
        script = _MIGRATIONS.get(next_version)
        if script:
            try:
                conn.executescript(script)
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        if _table_exists(conn, "schema_version"):
            conn.execute("UPDATE schema_version SET version = ?", (next_version,))
        else:
            conn.execute(
                "INSERT INTO schema_version(version) VALUES (?)",
                (next_version,),
            )
        current = next_version
    conn.commit()
    return current
