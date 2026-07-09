"""Workspace storage introspection helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from congressgov.services.core.storage_lanes.protocols import StorageLane

if TYPE_CHECKING:
    from congressgov.services.core.workspace import Workspace


def summarize_workspace(workspace: Workspace) -> dict[str, Any]:
    """Summarize workspace layout and registered stores."""
    paths = workspace.paths
    registry = workspace.registry()
    stores: list[dict[str, Any]] = []
    for name in registry.names():
        entry = registry.get_entry(name)
        item: dict[str, Any] = {
            "name": name,
            "lane": entry.lane.value,
            "backend": entry.backend,
        }
        if entry.schema:
            item["schema"] = entry.schema
        if entry.lane == StorageLane.BLOB:
            try:
                blob = registry.blob(name)
                item["stats"] = blob.get_stats()
            except Exception as exc:  # noqa: BLE001 — introspection only
                item["error"] = str(exc)
        elif entry.lane == StorageLane.RECORD:
            try:
                record = registry.record(name)
                item["stats"] = record.stats()
            except Exception as exc:  # noqa: BLE001
                item["error"] = str(exc)
        stores.append(item)

    return {
        "workspace": str(paths.root),
        "paths": {
            "api_db": str(paths.api_db),
            "graphs_dir": str(paths.graphs_dir),
            "exports_dir": str(paths.exports_dir),
            "config_file": str(paths.config_file),
        },
        "legacy_api_db": str(paths.legacy_api_db()),
        "stores": stores,
    }


def record_info(path: Path) -> dict[str, Any]:
    """Return metadata for a record-lane JSON file without fully opening it."""
    import json

    if not path.exists():
        return {"path": str(path), "exists": False}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "exists": True,
        "schema_version": payload.get("schema_version"),
        "congress": payload.get("congress"),
        "memberCount": len(payload.get("members") or {}),
        "eventCount": len(payload.get("events") or []),
        "billCount": len(payload.get("bill_ids") or []),
        "provenance": payload.get("provenance"),
    }
