"""Attach a :class:`RequestStore` to generated API clients."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from .store import RequestStore, StoreConfig
from .transport import (
    AsyncOfflineTransport,
    AsyncStoringTransport,
    OfflineTransport,
    StoringTransport,
)

_CLIENT_STORES: dict[int, RequestStore] = {}


def get_attached_store(client: Any) -> RequestStore | None:
    return _CLIENT_STORES.get(id(client))


def attach_request_store(
    client: Any,
    store: RequestStore | str | None = None,
    *,
    config: StoreConfig | None = None,
    enabled: bool = True,
    store_fail: bool = False,
) -> Any:
    """
    Wrap *client*'s httpx transport so all API calls pass through *store*.

    Works with ``AuthenticatedClient`` and ``Client`` from ``congressgov._client``.
    Call before any API traffic, or after ``set_httpx_client`` / ``set_async_httpx_client``.

    Args:
        client: API client instance.
        store: :class:`RequestStore`, connection string, or ``None`` for default SQLite.
        config: Optional store configuration merged with *store* when provided.
        enabled: When False, register store metadata without wrapping transport.
        store_fail: Fall through to network when store read/write fails.

    Returns:
        The same *client* instance (mutated in place).
    """
    if isinstance(store, str) or store is None:
        merged_config = config or StoreConfig(enabled=enabled, store_fail=store_fail)
        request_store = RequestStore(store, config=merged_config)
    elif config is not None:
        request_store = store
        request_store.config = config
        request_store.config.enabled = enabled
        request_store.config.store_fail = store_fail
    else:
        request_store = store
        request_store.config.enabled = enabled
        request_store.config.store_fail = store_fail

    _CLIENT_STORES[id(client)] = request_store

    if not enabled:
        return client

    if client._client is not None:
        _install_sync_transport(client._client, request_store)
    else:
        client.set_httpx_client(_build_sync_httpx_client(client, request_store))

    if client._async_client is not None:
        _install_async_transport(client._async_client, request_store)
    else:
        client.set_async_httpx_client(_build_async_httpx_client(client, request_store))

    return client


def _client_headers(client: Any) -> dict[str, str]:
    headers = dict(client._headers)
    token = getattr(client, "token", None)
    if token is not None:
        prefix = getattr(client, "prefix", "Bearer")
        auth_header_name = getattr(client, "auth_header_name", "Authorization")
        headers[auth_header_name] = f"{prefix} {token}" if prefix else token
    return headers


def _build_sync_httpx_client(client: Any, store: RequestStore) -> httpx.Client:
    transport = StoringTransport(httpx.HTTPTransport(), store)
    return httpx.Client(
        base_url=client._base_url,
        cookies=client._cookies,
        headers=_client_headers(client),
        timeout=client._timeout,
        verify=client._verify_ssl,
        follow_redirects=client._follow_redirects,
        transport=transport,
        **client._httpx_args,
    )


def _build_async_httpx_client(client: Any, store: RequestStore) -> httpx.AsyncClient:
    transport = AsyncStoringTransport(httpx.AsyncHTTPTransport(), store)
    return httpx.AsyncClient(
        base_url=client._base_url,
        cookies=client._cookies,
        headers=_client_headers(client),
        timeout=client._timeout,
        verify=client._verify_ssl,
        follow_redirects=client._follow_redirects,
        transport=transport,
        **client._httpx_args,
    )


def _install_sync_transport(httpx_client: httpx.Client, store: RequestStore) -> None:
    transport = httpx_client._transport
    if isinstance(transport, StoringTransport):
        # Re-attaching a (possibly different) store must not silently keep the
        # old one wired into the live transport -- swap it in place so callers
        # of attach_request_store() and get_attached_store() stay consistent.
        transport._store = store
        return
    httpx_client._transport = StoringTransport(transport, store)


def _install_async_transport(httpx_client: httpx.AsyncClient, store: RequestStore) -> None:
    transport = httpx_client._transport
    if isinstance(transport, AsyncStoringTransport):
        transport._store = store
        return
    httpx_client._transport = AsyncStoringTransport(transport, store)


def build_stored_client(
    client_factory: Callable[[], Any],
    store: RequestStore | str | None = None,
    **attach_kwargs: Any,
) -> Any:
    """Create a client via *client_factory* and attach a request store."""
    client = client_factory()
    return attach_request_store(client, store, **attach_kwargs)


def attach_offline_store(
    client: Any,
    store: RequestStore | str | None = None,
    *,
    config: StoreConfig | None = None,
) -> Any:
    """Attach *store* in offline-only mode (no network requests)."""
    if isinstance(store, str) or store is None:
        request_store = RequestStore(store, config=config or StoreConfig())
    else:
        request_store = store
        if config is not None:
            request_store.config = config

    _CLIENT_STORES[id(client)] = request_store
    client.set_httpx_client(_build_offline_sync_client(client, request_store))
    client.set_async_httpx_client(_build_offline_async_client(client, request_store))
    return client


def _build_offline_sync_client(client: Any, store: RequestStore) -> httpx.Client:
    return httpx.Client(
        base_url=client._base_url,
        cookies=client._cookies,
        headers=_client_headers(client),
        timeout=client._timeout,
        verify=client._verify_ssl,
        follow_redirects=client._follow_redirects,
        transport=OfflineTransport(store),
        **client._httpx_args,
    )


def _build_offline_async_client(client: Any, store: RequestStore) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=client._base_url,
        cookies=client._cookies,
        headers=_client_headers(client),
        timeout=client._timeout,
        verify=client._verify_ssl,
        follow_redirects=client._follow_redirects,
        transport=AsyncOfflineTransport(store),
        **client._httpx_args,
    )
