"""Tests for workspace path resolution and blob connection."""

from __future__ import annotations

from pathlib import Path

import pytest

from congressgov.services.core.workspace import (
    Workspace,
    resolve_blob_connection,
    resolve_workspace,
)


def test_resolve_workspace_default_name() -> None:
    paths = resolve_workspace()
    assert paths.root.name == ".congressgov"
    assert paths.api_db == paths.root / "api" / "request_store.db"
    assert paths.graph_path(118) == paths.root / "datasets" / "graphs" / "118.json"


def test_workspace_open_creates_directories(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    workspace = Workspace.open(root)
    assert workspace.paths.api_dir.is_dir()
    assert workspace.paths.graphs_dir.is_dir()
    assert workspace.paths.exports_dir.is_dir()


def test_resolve_blob_connection_explicit_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CONGRESS_REQUEST_STORE", raising=False)
    override = f"sqlite:///{tmp_path / 'custom.db'}"
    assert resolve_blob_connection(override=override) == override


def test_resolve_blob_connection_prefers_workspace_api_db(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CONGRESS_REQUEST_STORE", raising=False)
    paths = resolve_workspace(tmp_path / "ws")
    paths.ensure_dirs()
    paths.api_db.touch()
    connection = resolve_blob_connection(workspace=paths)
    assert connection == paths.api_db_url


def test_resolve_blob_connection_legacy_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CONGRESS_REQUEST_STORE", raising=False)
    paths = resolve_workspace(tmp_path / "ws")
    paths.root.mkdir(parents=True)
    legacy = paths.legacy_api_db()
    legacy.touch()
    connection = resolve_blob_connection(workspace=paths)
    assert connection == f"sqlite:///{legacy.as_posix()}"


def test_workspace_registry_default_api_blob(tmp_path: Path) -> None:
    workspace = Workspace.open(tmp_path / "ws")
    registry = workspace.registry()
    assert "api" in registry.names()
    blob = registry.blob("api")
    assert blob.get_stats()["backend"]["records"] == 0
    blob.close()
