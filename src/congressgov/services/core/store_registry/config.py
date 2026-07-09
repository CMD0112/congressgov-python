"""Store registry configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from congressgov.services.core.storage_lanes.protocols import StorageLane


@dataclass(frozen=True, slots=True)
class StoreEntry:
    """One named store in the workspace registry."""

    name: str
    lane: StorageLane
    backend: str
    schema: str | None = None
    policy: str | None = None
    options: dict[str, Any] = field(default_factory=dict)


def default_store_entries() -> dict[str, StoreEntry]:
    """Built-in stores when no ``config.yaml`` is present."""
    return {
        "api": StoreEntry(
            name="api",
            lane=StorageLane.BLOB,
            backend="sqlite:///api/request_store.db",
            policy="default",
        ),
        "exports": StoreEntry(
            name="exports",
            lane=StorageLane.ARTIFACT,
            backend="file:///exports",
        ),
    }


def graph_store_name(congress: int) -> str:
    return f"graphs/{congress}"


def default_graph_entry(congress: int) -> StoreEntry:
    return StoreEntry(
        name=graph_store_name(congress),
        lane=StorageLane.RECORD,
        backend=f"file:///datasets/graphs/{congress}.json",
        schema="congress_graph/v1",
        options={"congress": congress},
    )
