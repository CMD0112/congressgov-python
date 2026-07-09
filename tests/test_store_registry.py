"""Tests for named store registry and unified backend resolution."""

from __future__ import annotations

import json
from pathlib import Path


from congressgov.services.core.backends import BackendKind, resolve_connection
from congressgov.services.core.store_registry import (
    StoreEntry,
    StoreRegistry,
    graph_store_name,
    load_store_config,
    record_info,
)
from congressgov.services.core.storage_lanes import StorageLane
from congressgov.services.core.workspace import Workspace


def test_resolve_connection_memory() -> None:
    resolved = resolve_connection(":memory:")
    assert resolved.kind == BackendKind.MEMORY


def test_resolve_connection_relative_sqlite(tmp_path: Path) -> None:
    resolved = resolve_connection(
        "sqlite:///api/request_store.db",
        workspace_root=tmp_path,
    )
    assert resolved.kind == BackendKind.SQLITE
    assert resolved.path == tmp_path / "api" / "request_store.db"


def test_load_store_config_defaults_when_missing(tmp_path: Path) -> None:
    entries = load_store_config(tmp_path / "missing.yaml")
    assert "api" in entries
    assert entries["api"].lane == StorageLane.BLOB
    assert "exports" in entries
    assert entries["exports"].lane == StorageLane.ARTIFACT


def test_registry_graph_lazy_entry(tmp_path: Path) -> None:
    workspace = Workspace.open(tmp_path / "ws")
    registry = workspace.registry()
    name = graph_store_name(118)
    entry = registry.get_entry(name)
    assert entry.lane == StorageLane.RECORD
    assert entry.options["congress"] == 118


def test_registry_open_graph_store(tmp_path: Path) -> None:
    from congressgov.services.export.graph.store import CongressGraphStore as GraphStore

    workspace = Workspace.open(tmp_path / "ws")
    store = workspace.open_graph(119)
    assert isinstance(store, GraphStore)
    assert store.congress == 119
    store.save()
    assert store.path.exists()


def test_record_info(tmp_path: Path) -> None:
    path = tmp_path / "118.json"
    payload = {
        "schema_version": 1,
        "congress": 118,
        "members": {"A000001": {"id": "A000001", "label": "Test"}},
        "events": [],
        "bill_ids": ["118hr1"],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    info = record_info(path)
    assert info["exists"] is True
    assert info["congress"] == 118
    assert info["billCount"] == 1


def test_registry_custom_config(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    root.mkdir()
    config = {
        "version": 1,
        "stores": {
            "api": {
                "lane": "blob",
                "backend": "sqlite:///api/custom.db",
            }
        },
    }
    (root / "config.yaml").write_text(json.dumps(config), encoding="utf-8")
    registry = StoreRegistry.from_workspace(Workspace.open(root, ensure_dirs=False))
    resolved = registry.resolve_backend_connection(registry.get_entry("api"))
    assert resolved.endswith("api/custom.db")


def test_artifact_lane_write(tmp_path: Path) -> None:
    registry = StoreRegistry.from_entries(
        {
            "exports": StoreEntry(
                name="exports",
                lane=StorageLane.ARTIFACT,
                backend=f"file:///{tmp_path / 'exports'}",
            )
        },
        workspace_root=tmp_path,
    )
    lane = registry.artifact("exports")
    out = lane.write("report.json", '{"ok": true}')
    assert Path(out).exists()
    assert Path(out + ".manifest.json").exists()
