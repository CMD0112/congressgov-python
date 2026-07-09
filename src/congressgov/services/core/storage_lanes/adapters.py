"""Lane adapters wrapping existing persistence implementations."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from congressgov.services.core.storage_lanes.protocols import StorageLane


class FileArtifactLane:
    """Write immutable artifacts under a workspace exports directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        name: str,
        content: bytes | str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_bytes(content)
        manifest = {
            "name": name,
            "path": str(path),
            "written_at": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }
        manifest_path = path.with_suffix(path.suffix + ".manifest.json")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return str(path)


def lane_for_object(obj: Any) -> StorageLane | None:
    """Best-effort lane classification for a stored object."""
    module = type(obj).__module__
    name = type(obj).__name__
    if name == "RequestStore" and "request_store" in module:
        return StorageLane.BLOB
    if name == "CongressGraphStore":
        return StorageLane.RECORD
    if name in ("UnifiedStorage", "StorageManager"):
        return StorageLane.TABLE
    if name == "FileArtifactLane":
        return StorageLane.ARTIFACT
    if name == "MultiLevelCache":
        return StorageLane.CACHE
    return None
