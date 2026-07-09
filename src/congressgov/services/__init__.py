"""
Congress.gov API services (congressgov.services).

High-level services for the Congress.gov API. Core services load eagerly;
caching, export, batch, and rate-limiting symbols load on demand (optional extras).
"""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __version__ = version("congressgov")
except PackageNotFoundError:
    __version__ = "0.1.0"

# Register dynamic method extensions on model classes FIRST
from . import extensions  # noqa: F401

from .core.service import ApiService
from .bill import Bill
from .amendment import Amendment
from .congress import Congress
from .committee import Committee
from .committee_meeting import CommitteeMeeting
from .committee_print import CommitteePrint
from .committee_report import CommitteeReport
from .congressional_record import CongressionalRecord
from .daily_congressional_record import DailyCongressionalRecord
from .bound_congressional_record import BoundCongressionalRecord
from .crsreport import CRSReport
from .hearing import Hearing
from .house_communication import HouseCommunication
from .house_requirement import HouseRequirement
from .house_vote import HouseVote
from .member import Member
from .nomination import Nomination
from .senate_communication import SenateCommunication
from .summaries import Summaries
from .treaty import Treaty

from congressgov.models.entities.bill import Summary

from .exceptions import (
    MiddlewareError,
    ClientNotFoundError,
    ValidationError,
    APIError,
    RateLimitError,
    RequestStoreError,
    UnsupportedApiUrlError,
)
from .client_factory import (
    create_api_client,
    create_offline_client,
    create_stored_api_client,
    get_client_from_env,
    CONGRESS_API_KEY_ENV,
    CONGRESS_API_AUTH_HEADER,
    DEFAULT_API_BASE_URL,
    OFFLINE_API_KEY,
)
from .core.workspace import (
    CONGRESS_REQUEST_STORE_ENV,
    CONGRESS_WORKSPACE_ENV,
    Workspace,
)
from .core.store_registry import StoreRegistry
from .config import configure_logging
from .core.request_store import (
    RequestStore,
    StoreConfig,
    attach_offline_store,
    attach_request_store,
    fetch_options,
    get_attached_store,
    load_policy_config,
    print_store_stats,
)

# name -> (submodule to import, pip extra for error message)
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # batch
    "BatchProcessor": ("batch", "batch"),
    "BatchConfig": ("batch", "batch"),
    "BatchResult": ("batch", "batch"),
    # cache
    "CacheConfig": ("caching", "cache"),
    "MultiLevelCache": ("caching", "cache"),
    "MemoryCache": ("caching", "cache"),
    "RedisCache": ("caching", "cache"),
    "FileCache": ("caching", "cache"),
    # rate limiting (shipped with cache extra — uses same optional stack)
    "RateLimiter": ("rate_limiting", "cache"),
    "RateLimitConfig": ("rate_limiting", "cache"),
    # export
    "DataExporter": ("export", "export"),
    "PandasIntegration": ("export", "export"),
    "DatabaseExporter": ("export", "export"),
    "DataTransformer": ("export", "export"),
    "VisualizationExporter": ("export", "export"),
    "ExportConfig": ("export", "export"),
}

_LAZY_MODULES: dict[str, frozenset[str]] = {}


def _lazy_module_names() -> dict[str, frozenset[str]]:
    global _LAZY_MODULES
    if not _LAZY_MODULES:
        buckets: dict[str, set[str]] = {}
        for _name, (mod, _extra) in _LAZY_EXPORTS.items():
            buckets.setdefault(mod, set()).add(_name)
        _LAZY_MODULES = {k: frozenset(v) for k, v in buckets.items()}
    return _LAZY_MODULES


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    mod_name, extra = _LAZY_EXPORTS[name]
    try:
        module = import_module(f".{mod_name}", __name__)
    except ImportError as exc:
        raise ImportError(
            f"Optional feature requires congressgov[{extra}]. "
            f"Install with: pip install congressgov[{extra}]"
            f" or pip install congressgov[all]"
        ) from exc

    for export_name in _lazy_module_names()[mod_name]:
        globals()[export_name] = getattr(module, export_name)

    return globals()[name]


__all__ = [
    "__version__",
    "ApiService",
    "Bill",
    "Amendment",
    "Congress",
    "Committee",
    "CommitteeMeeting",
    "CommitteePrint",
    "CommitteeReport",
    "CongressionalRecord",
    "DailyCongressionalRecord",
    "BoundCongressionalRecord",
    "CRSReport",
    "Hearing",
    "HouseCommunication",
    "HouseRequirement",
    "HouseVote",
    "Member",
    "Nomination",
    "SenateCommunication",
    "Summaries",
    "Summary",
    "Treaty",
    "CacheConfig",
    "MultiLevelCache",
    "MemoryCache",
    "RedisCache",
    "FileCache",
    "RateLimiter",
    "RateLimitConfig",
    "DataExporter",
    "PandasIntegration",
    "DatabaseExporter",
    "DataTransformer",
    "VisualizationExporter",
    "ExportConfig",
    "BatchProcessor",
    "BatchConfig",
    "BatchResult",
    "MiddlewareError",
    "ClientNotFoundError",
    "ValidationError",
    "APIError",
    "RateLimitError",
    "RequestStoreError",
    "UnsupportedApiUrlError",
    "RequestStore",
    "StoreConfig",
    "attach_request_store",
    "attach_offline_store",
    "fetch_options",
    "get_attached_store",
    "load_policy_config",
    "print_store_stats",
    "create_api_client",
    "create_offline_client",
    "create_stored_api_client",
    "get_client_from_env",
    "CONGRESS_API_KEY_ENV",
    "CONGRESS_API_AUTH_HEADER",
    "CONGRESS_REQUEST_STORE_ENV",
    "CONGRESS_WORKSPACE_ENV",
    "Workspace",
    "StoreRegistry",
    "DEFAULT_API_BASE_URL",
    "OFFLINE_API_KEY",
    "configure_logging",
]


