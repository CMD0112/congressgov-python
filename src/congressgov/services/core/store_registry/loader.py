"""Load workspace store registry configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from congressgov.services.core.storage_lanes.protocols import StorageLane

from .config import StoreEntry, default_store_entries


def _parse_lane(value: str) -> StorageLane:
    try:
        return StorageLane(str(value).lower())
    except ValueError as exc:
        raise ValueError(f"Unknown storage lane {value!r}") from exc


def store_entry_from_dict(name: str, data: dict[str, Any]) -> StoreEntry:
    return StoreEntry(
        name=name,
        lane=_parse_lane(data["lane"]),
        backend=str(data["backend"]),
        schema=data.get("schema"),
        policy=data.get("policy"),
        options=dict(data.get("options") or {}),
    )


def config_from_dict(data: dict[str, Any]) -> dict[str, StoreEntry]:
    stores_raw = data.get("stores") or {}
    return {
        str(name): store_entry_from_dict(str(name), entry)
        for name, entry in stores_raw.items()
    }


def _load_raw(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "YAML workspace config requires PyYAML. Install with: pip install pyyaml"
            ) from exc
        loaded = yaml.safe_load(text)
    else:
        loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Workspace config must be a mapping, got {type(loaded).__name__}")
    return loaded


def load_store_config(path: Path | None) -> dict[str, StoreEntry]:
    """Load named stores from *path*, or return defaults when missing."""
    if path is None or not path.exists():
        return default_store_entries()
    return config_from_dict(_load_raw(path))
