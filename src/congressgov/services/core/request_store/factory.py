"""Factory for constructing request-store backends from connection strings."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from congressgov.services.core.backends import create_request_store_backend as _create_backend

from .backends.base import RequestStoreBackend


def create_backend(
    connection: Union[str, Path, None] = None,
    *,
    workspace_root: Path | None = None,
) -> RequestStoreBackend:
    """
    Create a request-store backend from a connection string.

    Supported forms:
    - ``None`` with a *workspace_root* → the workspace's persistent SQLite blob
      store (``<workspace_root>/api/request_store.db``), matching
      :meth:`RequestStore.open`
    - ``None`` with no *workspace_root* or ``":memory:"`` → in-memory backend
    - ``sqlite:///path/to/store.db`` → SQLite file
    - filesystem path ending in ``.db`` → SQLite file
    - ``file:///path/to/dir`` or directory path → JSON file per entry
    - ``redis://host:port/db`` → Redis (requires ``redis`` package)
    """
    if connection is None:
        if workspace_root is not None:
            from congressgov.services.core.workspace import WorkspacePaths, resolve_blob_connection

            connection = resolve_blob_connection(workspace=WorkspacePaths(root=workspace_root))
        else:
            connection = ":memory:"
    return _create_backend(str(connection), workspace_root=workspace_root)
