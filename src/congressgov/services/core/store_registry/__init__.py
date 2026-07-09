"""Named store registry for the Congress.gov workspace."""

from __future__ import annotations

from congressgov.services.core.store_registry.config import (
    StoreEntry,
    default_graph_entry,
    default_store_entries,
    graph_store_name,
)
from congressgov.services.core.store_registry.introspection import record_info, summarize_workspace
from congressgov.services.core.store_registry.loader import load_store_config
from congressgov.services.core.store_registry.registry import StoreRegistry

__all__ = [
    "StoreEntry",
    "StoreRegistry",
    "default_graph_entry",
    "default_store_entries",
    "graph_store_name",
    "load_store_config",
    "record_info",
    "summarize_workspace",
]
