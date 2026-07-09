"""Congress.gov project workspace — shared root for all storage lanes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .paths import (
    CONGRESS_REQUEST_STORE_ENV,
    CONGRESS_WORKSPACE_ENV,
    CONFIG_FILENAME,
    DEFAULT_WORKSPACE_NAME,
    LEGACY_API_DB_NAME,
    WorkspacePaths,
    default_workspace_root,
)
from .resolve import (
    maybe_log_legacy_migration,
    migrate_legacy_blob_if_needed,
    resolve_blob_connection,
    resolve_workspace,
)

if TYPE_CHECKING:
    from congressgov.services.core.request_store import RequestStore
    from congressgov.services.core.store_registry import StoreRegistry
    from congressgov.services.export.graph.store import CongressGraphStore


class Workspace:
    """
    Single project workspace for API blobs, datasets, exports, and cache.

    Example::

        workspace = Workspace.open()
        client = get_client_from_env(request_store=workspace.blob_connection())
        graph = workspace.open_graph(118)
    """

    def __init__(self, paths: WorkspacePaths) -> None:
        self.paths = paths

    @classmethod
    def open(
        cls,
        root: str | Path | None = None,
        *,
        ensure_dirs: bool = True,
    ) -> Workspace:
        paths = resolve_workspace(root)
        if ensure_dirs:
            paths.ensure_dirs()
        maybe_log_legacy_migration(paths)
        return cls(paths)

    def blob_connection(self, name: str = "api") -> str:
        """Resolve a blob-lane connection via the store registry (and env overrides)."""
        import os

        if name == "api" and os.environ.get(CONGRESS_REQUEST_STORE_ENV):
            return resolve_blob_connection(workspace=self.paths)
        if name == "api":
            legacy = self.paths.legacy_api_db()
            if legacy.exists() and not self.paths.api_db.exists():
                return f"sqlite:///{legacy.as_posix()}"
        registry = self.registry()
        entry = registry.get_entry(name)
        if entry.lane.value != "blob":
            raise ValueError(f"Store {name!r} is lane {entry.lane.value!r}, not blob")
        return registry.resolve_backend_connection(entry)

    def blob_store(self, name: str = "api") -> RequestStore:
        return self.registry().blob(name)

    def open_graph(self, congress: int, *, name: str | None = None) -> CongressGraphStore:
        if name is not None:
            store = self.registry().record(name)
            if store.congress != congress:
                raise ValueError(
                    f"Store {name!r} congress {store.congress} != requested {congress}"
                )
            return store
        return self.registry().graph(congress)

    def registry(self) -> StoreRegistry:
        from congressgov.services.core.store_registry import StoreRegistry

        return StoreRegistry.from_workspace(self)

    def summarize(self) -> dict[str, object]:
        from congressgov.services.core.store_registry.introspection import summarize_workspace

        return summarize_workspace(self)

    def write_export(
        self,
        name: str,
        content: bytes | str,
        *,
        metadata: dict[str, object] | None = None,
    ) -> str:
        """Write a generated artifact to the workspace exports lane."""
        return self.registry().artifact("exports").write(
            name,
            content,
            metadata=metadata,
        )


__all__ = [
    "CONGRESS_REQUEST_STORE_ENV",
    "CONGRESS_WORKSPACE_ENV",
    "CONFIG_FILENAME",
    "DEFAULT_WORKSPACE_NAME",
    "LEGACY_API_DB_NAME",
    "Workspace",
    "WorkspacePaths",
    "default_workspace_root",
    "maybe_log_legacy_migration",
    "migrate_legacy_blob_if_needed",
    "resolve_blob_connection",
    "resolve_workspace",
]
