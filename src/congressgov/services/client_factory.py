"""Build API clients from environment configuration."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from congressgov._client import AuthenticatedClient

if TYPE_CHECKING:
    from congressgov.services.core.request_store import RequestStore

DEFAULT_API_BASE_URL = "https://api.congress.gov/v3"
CONGRESS_API_KEY_ENV = "CONGRESS_API_KEY"
OFFLINE_API_KEY = "offline"
CONGRESS_API_AUTH_HEADER = "X-API-Key"


def _resolve_request_store(
    request_store: RequestStore | str | bool | None,
) -> RequestStore | None:
    from congressgov.services.core.request_store import RequestStore
    from congressgov.services.core.workspace import Workspace

    if request_store is False:
        return None
    if isinstance(request_store, RequestStore):
        return request_store

    workspace = Workspace.open(ensure_dirs=False)
    workspace_root = workspace.paths.root

    if request_store is True or request_store is None:
        return workspace.blob_store("api")

    return RequestStore(request_store, workspace_root=workspace_root)


def _maybe_attach_store(
    client: AuthenticatedClient,
    request_store: RequestStore | str | bool | None,
    *,
    store_fail: bool,
) -> AuthenticatedClient:
    store = _resolve_request_store(request_store)
    if store is None:
        return client
    from congressgov.services.core.request_store import attach_request_store

    attach_request_store(client, store, store_fail=store_fail)
    return client


def create_api_client(
    *,
    api_key: str,
    base_url: str | None = None,
    request_store: RequestStore | str | bool | None = False,
    store_fail: bool = False,
) -> AuthenticatedClient:
    """
    Return an ``AuthenticatedClient`` configured for the Congress.gov API.

    Args:
        api_key: Congress.gov API key.
        base_url: API base URL (default: ``https://api.congress.gov/v3``).
        request_store: When ``True`` or a connection string, attach persistent
            request deduplication. ``False`` (default) leaves the client bare.
        store_fail: Fall through to the network when the store errors.
    """
    client = AuthenticatedClient(
        base_url=base_url or DEFAULT_API_BASE_URL,
        token=api_key,
        prefix="",
        auth_header_name=CONGRESS_API_AUTH_HEADER,
    )
    return _maybe_attach_store(client, request_store, store_fail=store_fail)


def create_stored_api_client(
    *,
    api_key: str,
    base_url: str | None = None,
    request_store: RequestStore | str | bool | None = True,
    store_fail: bool = False,
) -> AuthenticatedClient:
    """
    Return an authenticated client with request-store deduplication enabled.

    Equivalent to ``create_api_client(..., request_store=True)``.
    """
    return create_api_client(
        api_key=api_key,
        base_url=base_url,
        request_store=request_store,
        store_fail=store_fail,
    )


def create_offline_client(
    *,
    base_url: str | None = None,
    request_store: RequestStore | str | bool | None = True,
) -> AuthenticatedClient:
    """
    Return a client that serves API responses only from the request store.

    No network requests are made. Useful for demos and CI when the store was
    populated by a prior online run.
    """
    store = _resolve_request_store(request_store)
    if store is None:
        raise ValueError("Offline mode requires a request store connection")
    client = AuthenticatedClient(
        base_url=base_url or DEFAULT_API_BASE_URL,
        token=OFFLINE_API_KEY,
        prefix="",
        auth_header_name=CONGRESS_API_AUTH_HEADER,
    )
    from congressgov.services.core.request_store import attach_offline_store

    attach_offline_store(client, store)
    return client


def get_client_from_env(
    *,
    api_key_var: str = CONGRESS_API_KEY_ENV,
    base_url: str | None = None,
    token: str | None = None,
    load_dotenv: bool = True,
    request_store: RequestStore | str | bool | None = True,
    store_fail: bool = False,
    offline: bool = False,
) -> AuthenticatedClient:
    """
    Create an authenticated client using ``CONGRESS_API_KEY`` (or *api_key_var*).

    By default attaches a persistent request store (see ``CONGRESS_REQUEST_STORE``
    and ``CONGRESS_WORKSPACE``). Pass ``request_store=False`` to disable deduplication.
    Pass ``offline=True`` to serve responses only from the store (no API key required).

    If *load_dotenv* is true and ``python-dotenv`` is installed, loads a ``.env``
    file from the current working directory before reading the environment.

    Raises:
        ValueError: If no API key is available and *offline* is False.
    """
    if load_dotenv:
        try:
            from dotenv import load_dotenv as _load_dotenv
        except ImportError:
            pass
        else:
            _load_dotenv()

    if offline:
        return create_offline_client(base_url=base_url, request_store=request_store)

    key = token or os.environ.get(api_key_var)
    if not key:
        raise ValueError(
            f"No API key found. Set {api_key_var} or pass token= explicitly."
        )
    return create_api_client(
        api_key=key,
        base_url=base_url,
        request_store=request_store,
        store_fail=store_fail,
    )
