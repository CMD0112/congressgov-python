"""
Unified storage facade for the Congress.gov SDK.

Re-exports workspace, registry, lanes, and request-store helpers.
"""

from __future__ import annotations

from congressgov.services.core.storage_lanes import (
    FileArtifactLane,
    StorageLane,
    lane_for_object,
)
from congressgov.services.core.store_registry import (
    StoreEntry,
    StoreRegistry,
    graph_store_name,
    load_store_config,
    record_info,
    summarize_workspace,
)
from congressgov.services.core.workspace import (
    CONGRESS_REQUEST_STORE_ENV,
    CONGRESS_WORKSPACE_ENV,
    Workspace,
    WorkspacePaths,
    default_workspace_root,
    resolve_blob_connection,
    resolve_workspace,
)
from congressgov.services.core.request_store import (
    RequestStore,
    StoreConfig,
    attach_offline_store,
    attach_request_store,
    fetch_options,
    get_attached_store,
    load_policy_config,
    print_store_stats,
)

__all__ = [
    "CONGRESS_REQUEST_STORE_ENV",
    "CONGRESS_WORKSPACE_ENV",
    "FileArtifactLane",
    "RequestStore",
    "StorageLane",
    "StoreConfig",
    "StoreEntry",
    "StoreRegistry",
    "Workspace",
    "WorkspacePaths",
    "attach_offline_store",
    "attach_request_store",
    "default_workspace_root",
    "fetch_options",
    "get_attached_store",
    "graph_store_name",
    "lane_for_object",
    "load_policy_config",
    "load_store_config",
    "print_store_stats",
    "record_info",
    "resolve_blob_connection",
    "resolve_workspace",
    "summarize_workspace",
]
