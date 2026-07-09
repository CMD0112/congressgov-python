"""Storage lane taxonomy and adapters."""

from __future__ import annotations

from congressgov.services.core.storage_lanes.adapters import FileArtifactLane, lane_for_object
from congressgov.services.core.storage_lanes.protocols import (
    ArtifactLane,
    BlobLane,
    CacheLane,
    RecordLane,
    StorageLane,
    TableLane,
)

__all__ = [
    "ArtifactLane",
    "BlobLane",
    "CacheLane",
    "FileArtifactLane",
    "RecordLane",
    "StorageLane",
    "TableLane",
    "lane_for_object",
]
