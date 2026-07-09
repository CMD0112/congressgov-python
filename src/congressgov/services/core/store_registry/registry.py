"""Named store registry for the Congress.gov workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from congressgov.services.core.backends import resolve_connection
from congressgov.services.core.storage_lanes.adapters import FileArtifactLane
from congressgov.services.core.storage_lanes.protocols import StorageLane

from .config import StoreEntry, default_graph_entry, default_store_entries, graph_store_name
from .loader import load_store_config

if TYPE_CHECKING:
    from congressgov.services.core.request_store import RequestStore
    from congressgov.services.core.workspace import Workspace
    from congressgov.services.export.graph.store import CongressGraphStore


@dataclass
class StoreRegistry:
    """Resolve named stores by lane from workspace configuration."""

    workspace_root: Path
    entries: dict[str, StoreEntry] = field(default_factory=dict)
    _instances: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_workspace(cls, workspace: Workspace) -> StoreRegistry:
        entries = load_store_config(workspace.paths.config_file)
        return cls(workspace_root=workspace.paths.root, entries=entries)

    @classmethod
    def from_entries(
        cls,
        entries: dict[str, StoreEntry],
        *,
        workspace_root: Path | None = None,
    ) -> StoreRegistry:
        root = workspace_root or Path(".congressgov").resolve()
        return cls(workspace_root=root, entries=entries)

    @classmethod
    def default(cls, workspace_root: Path | None = None) -> StoreRegistry:
        root = workspace_root or Path(".congressgov").resolve()
        return cls(workspace_root=root, entries=default_store_entries())

    def names(self) -> list[str]:
        return sorted(self.entries)

    def get_entry(self, name: str) -> StoreEntry:
        if name not in self.entries:
            if name.startswith("graphs/"):
                try:
                    congress = int(name.split("/", 1)[1])
                except (IndexError, ValueError) as exc:
                    raise KeyError(f"Unknown store {name!r}") from exc
                entry = default_graph_entry(congress)
                self.entries[name] = entry
                return entry
            raise KeyError(f"Unknown store {name!r}")
        return self.entries[name]

    def resolve_backend_connection(self, entry: StoreEntry) -> str:
        resolved = resolve_connection(entry.backend, workspace_root=self.workspace_root)
        return resolved.connection

    def resolve_path(self, entry: StoreEntry) -> Path:
        resolved = resolve_connection(entry.backend, workspace_root=self.workspace_root)
        if resolved.path is not None:
            return resolved.path
        raise ValueError(f"Store {entry.name!r} has no filesystem path")

    def get(self, name: str) -> Any:
        if name in self._instances:
            return self._instances[name]
        entry = self.get_entry(name)
        instance = self._open_entry(entry)
        self._instances[name] = instance
        return instance

    def _open_entry(self, entry: StoreEntry) -> Any:
        if entry.lane == StorageLane.BLOB:
            return self._open_blob(entry)
        if entry.lane == StorageLane.RECORD:
            return self._open_record(entry)
        if entry.lane == StorageLane.TABLE:
            return self._open_table(entry)
        if entry.lane == StorageLane.ARTIFACT:
            return self._open_artifact(entry)
        if entry.lane == StorageLane.CACHE:
            raise NotImplementedError("Cache lane registry entries are not implemented yet")
        raise ValueError(f"Unsupported lane {entry.lane!r}")

    def _open_blob(self, entry: StoreEntry) -> RequestStore:
        from congressgov.services.core.policies import load_policy_config
        from congressgov.services.core.request_store import RequestStore, StoreConfig

        connection = self.resolve_backend_connection(entry)
        config = StoreConfig()
        if entry.policy and entry.policy != "default":
            policy_path = Path(entry.policy)
            if not policy_path.is_absolute():
                # Policy paths in config.yaml are authored relative to the
                # workspace root, not the process's CWD.
                policy_path = self.workspace_root / policy_path
            config.policy = load_policy_config(policy_path)
        return RequestStore(connection, config=config, workspace_root=self.workspace_root)

    def _open_record(self, entry: StoreEntry) -> CongressGraphStore:
        from congressgov.services.export.graph.store import CongressGraphStore

        congress = int(entry.options.get("congress", 0))
        if congress <= 0 and entry.name.startswith("graphs/"):
            congress = int(entry.name.split("/", 1)[1])
        if congress <= 0:
            raise ValueError(f"Record store {entry.name!r} requires options.congress")
        path = self.resolve_path(entry)
        return CongressGraphStore.open(path, congress=congress)

    def _open_table(self, entry: StoreEntry) -> Any:
        from congressgov.services.core.storage import UnifiedStorage

        model_class = entry.options.get("model_class")
        return UnifiedStorage(self.resolve_backend_connection(entry), model_class=model_class)

    def _open_artifact(self, entry: StoreEntry) -> FileArtifactLane:
        return FileArtifactLane(self.resolve_path(entry))

    def blob(self, name: str = "api") -> RequestStore:
        store = self.get(name)
        entry = self.get_entry(name)
        if entry.lane != StorageLane.BLOB:
            raise TypeError(f"Store {name!r} is lane {entry.lane.value}, expected blob")
        return store

    def record(self, name: str) -> CongressGraphStore:
        store = self.get(name)
        entry = self.get_entry(name)
        if entry.lane != StorageLane.RECORD:
            raise TypeError(f"Store {name!r} is lane {entry.lane.value}, expected record")
        return store

    def graph(self, congress: int) -> CongressGraphStore:
        return self.record(graph_store_name(congress))

    def artifact(self, name: str) -> FileArtifactLane:
        store = self.get(name)
        entry = self.get_entry(name)
        if entry.lane != StorageLane.ARTIFACT:
            raise TypeError(f"Store {name!r} is lane {entry.lane.value}, expected artifact")
        return store

    def table(self, name: str) -> Any:
        store = self.get(name)
        entry = self.get_entry(name)
        if entry.lane != StorageLane.TABLE:
            raise TypeError(f"Store {name!r} is lane {entry.lane.value}, expected table")
        return store
