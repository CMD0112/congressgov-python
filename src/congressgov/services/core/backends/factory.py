"""Connection-string factory shared by request store and workspace registry."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from congressgov.services.core.request_store.backends.base import RequestStoreBackend


class BackendKind(str, Enum):
    """Supported storage engine kinds."""

    MEMORY = "memory"
    SQLITE = "sqlite"
    FILE = "file"
    REDIS = "redis"
    SQL = "sql"


@dataclass(frozen=True, slots=True)
class ResolvedBackend:
    """Normalized backend descriptor."""

    kind: BackendKind
    connection: str
    path: Path | None = None


def _normalize_sqlite_path(raw_path: str, workspace_root: Path | None) -> str:
    path = Path(raw_path)
    if not path.is_absolute() and workspace_root is not None:
        path = (workspace_root / path).resolve()
    return f"sqlite:///{path.as_posix()}"


def _normalize_file_path(raw_path: str, workspace_root: Path | None) -> str:
    path = Path(raw_path)
    if not path.is_absolute() and workspace_root is not None:
        path = (workspace_root / path).resolve()
    return path.as_posix()


def resolve_connection(
    connection: str,
    *,
    workspace_root: Path | None = None,
) -> ResolvedBackend:
    """
    Parse a connection string into a :class:`ResolvedBackend`.

    Relative ``sqlite://`` and ``file://`` paths resolve against *workspace_root*
    when provided.
    """
    text = str(connection).strip()
    lower = text.lower()

    if text in (":memory:", "memory://", "memory"):
        return ResolvedBackend(kind=BackendKind.MEMORY, connection=":memory:")

    if lower.startswith("redis://"):
        return ResolvedBackend(kind=BackendKind.REDIS, connection=text)

    if lower.startswith("sqlite:///"):
        raw = text[len("sqlite:///") :]
        normalized = _normalize_sqlite_path(raw, workspace_root)
        db_path = Path(normalized[len("sqlite:///") :])
        return ResolvedBackend(kind=BackendKind.SQLITE, connection=normalized, path=db_path)

    if lower.startswith("file:///"):
        raw = text[len("file:///") :]
        normalized = _normalize_file_path(raw, workspace_root)
        return ResolvedBackend(
            kind=BackendKind.FILE,
            connection=f"file:///{normalized}",
            path=Path(normalized),
        )

    sql_prefixes = ("postgresql://", "mysql://", "mariadb://", "oracle://")
    if any(lower.startswith(prefix) for prefix in sql_prefixes):
        return ResolvedBackend(kind=BackendKind.SQL, connection=text)

    path = Path(text)
    if workspace_root is not None and not path.is_absolute():
        path = (workspace_root / path).resolve()

    if path.suffix == ".db" or lower.endswith(".db"):
        normalized = f"sqlite:///{path.as_posix()}"
        return ResolvedBackend(kind=BackendKind.SQLITE, connection=normalized, path=path)

    if path.is_dir() or (not path.suffix and not path.exists()):
        return ResolvedBackend(
            kind=BackendKind.FILE,
            connection=f"file:///{path.as_posix()}",
            path=path,
        )

    parsed = urlparse(text)
    if parsed.scheme in ("", "file") and path.suffix.lower() in {
        ".json",
        ".csv",
        ".parquet",
        ".pkl",
        ".pickle",
    }:
        return ResolvedBackend(kind=BackendKind.FILE, connection=str(path), path=path)

    if path.is_dir():
        return ResolvedBackend(
            kind=BackendKind.FILE,
            connection=f"file:///{path.as_posix()}",
            path=path,
        )

    raise ValueError(
        f"Unsupported storage connection {connection!r}. "
        "Use :memory:, sqlite:///path, file:///dir, redis://host/db, or a file path."
    )


def create_request_store_backend(
    connection: str,
    *,
    workspace_root: Path | None = None,
) -> RequestStoreBackend:
    """Instantiate a request-store backend from a connection string."""
    resolved = resolve_connection(connection, workspace_root=workspace_root)

    if resolved.kind == BackendKind.MEMORY:
        from congressgov.services.core.request_store.backends.memory import MemoryRequestStoreBackend

        return MemoryRequestStoreBackend()

    if resolved.kind == BackendKind.REDIS:
        from congressgov.services.core.request_store.backends.redis import RedisRequestStoreBackend

        return RedisRequestStoreBackend(resolved.connection)

    if resolved.kind == BackendKind.FILE:
        from congressgov.services.core.request_store.backends.file import FileRequestStoreBackend

        conn = resolved.connection
        directory = conn[len("file:///") :] if conn.startswith("file:///") else conn
        return FileRequestStoreBackend(directory)

    if resolved.kind == BackendKind.SQLITE:
        from congressgov.services.core.request_store.backends.sqlite import SQLiteRequestStoreBackend

        return SQLiteRequestStoreBackend(resolved.connection)

    raise ValueError(
        f"Connection {connection!r} resolves to {resolved.kind.value}, "
        "which is not supported for the blob request store."
    )
