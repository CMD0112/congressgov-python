"""
Persistent request store for Congress.gov API deduplication.

Every distinct API request is stored on first fetch. Repeat calls with the
same canonical key are served from storage unless ``force_fetch=True``.

Quick start::

    from congressgov._client import AuthenticatedClient
    from congressgov.services.core.request_store import RequestStore, attach_request_store

    client = AuthenticatedClient(base_url="https://api.congress.gov/v3", token=API_KEY)
    store = RequestStore.open("sqlite:///.congressgov/request_store.db")
    attach_request_store(client, store)

Backends:
- ``:memory:`` — in-memory (tests)
- ``sqlite:///path/to/store.db`` — persistent SQLite (default)
"""

from .backends import (
    FileRequestStoreBackend,
    MemoryRequestStoreBackend,
    RequestStoreBackend,
    SQLiteRequestStoreBackend,
)
from .client import (
    attach_offline_store,
    attach_request_store,
    build_stored_client,
    get_attached_store,
)
from .context import CONGRESSGOV_EXT, fetch_options, get_force_fetch, get_store_fail
from .factory import create_backend
from .introspection import list_keys, print_store_stats, purge_stale, summarize_store
from .keys import normalize_query, request_key_digest, request_key_from_httpx
from .models import RequestKey, StoredResponse
from .policy import (
    POLICY_TTLS,
    ChangePolicy,
    PolicyConfig,
    PolicyRule,
    StalenessEstimate,
    DEFAULT_POLICY_RULES,
    current_congress,
    estimate_refresh_after,
    estimate_staleness,
    extract_congress_from_path,
    is_stale,
)
from .policy_loader import load_policy_config
from .store import RequestStore, StoreConfig
from .transport import (
    AsyncOfflineTransport,
    AsyncStoringTransport,
    OfflineTransport,
    StoringTransport,
)

try:
    from .backends.redis import RedisRequestStoreBackend
except ImportError:
    RedisRequestStoreBackend = None  # type: ignore[misc, assignment]

__all__ = [
    "CONGRESSGOV_EXT",
    "DEFAULT_POLICY_RULES",
    "POLICY_TTLS",
    "AsyncOfflineTransport",
    "AsyncStoringTransport",
    "ChangePolicy",
    "FileRequestStoreBackend",
    "MemoryRequestStoreBackend",
    "OfflineTransport",
    "PolicyConfig",
    "PolicyRule",
    "RequestKey",
    "RequestStore",
    "RequestStoreBackend",
    "SQLiteRequestStoreBackend",
    "StalenessEstimate",
    "StoredResponse",
    "StoreConfig",
    "StoringTransport",
    "attach_offline_store",
    "attach_request_store",
    "build_stored_client",
    "create_backend",
    "current_congress",
    "estimate_refresh_after",
    "estimate_staleness",
    "extract_congress_from_path",
    "fetch_options",
    "get_attached_store",
    "get_force_fetch",
    "get_store_fail",
    "is_stale",
    "list_keys",
    "load_policy_config",
    "normalize_query",
    "print_store_stats",
    "purge_stale",
    "request_key_digest",
    "request_key_from_httpx",
    "summarize_store",
]

if RedisRequestStoreBackend is not None:
    __all__.append("RedisRequestStoreBackend")
