"""httpx transports that deduplicate API requests via :class:`RequestStore`."""

from __future__ import annotations

import httpx

from congressgov.services.exceptions import RequestStoreError

from .context import resolve_request_options
from .keys import request_key_from_httpx
from .models import StoredResponse, normalize_stored_response_headers
from .store import RequestStore


def _response_from_stored(stored: StoredResponse, request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        status_code=stored.status_code,
        headers=normalize_stored_response_headers(stored.headers),
        content=stored.body,
        request=request,
    )


class StoringTransport(httpx.BaseTransport):
    """Sync transport wrapper that reads/writes through a :class:`RequestStore`."""

    def __init__(
        self,
        transport: httpx.BaseTransport,
        store: RequestStore,
    ) -> None:
        self._transport = transport
        self._store = store

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        force_fetch, store_fail = resolve_request_options(
            request.extensions,
            default_store_fail=self._store.config.store_fail,
        )
        stored, is_leader = self._store.get_sync(
            request,
            force_fetch=force_fetch,
            store_fail=store_fail,
        )
        if stored is not None:
            if is_leader:
                self._store.release_sync(request)
            return _response_from_stored(stored, request)

        if not is_leader:
            # The original leader finished (miss, failure, or a non-200 response
            # it didn't persist) without producing a cached entry. Re-entering the
            # gate here may make *this* caller the new leader, so its leadership
            # status must be tracked (not discarded) -- otherwise a redundant
            # fetch below would never be persisted, and the freshly acquired gate
            # entry would never be released, permanently wedging every future
            # request for this key behind an event nobody will ever set.
            stored, is_leader = self._store.get_sync(
                request,
                force_fetch=False,
                store_fail=store_fail,
            )
            if stored is not None:
                if is_leader:
                    self._store.release_sync(request)
                return _response_from_stored(stored, request)

        try:
            response = self._transport.handle_request(request)
            if is_leader:
                self._store.store(request, response, store_fail=store_fail)
            return response
        finally:
            if is_leader:
                self._store.release_sync(request)


class AsyncStoringTransport(httpx.AsyncBaseTransport):
    """Async transport wrapper that reads/writes through a :class:`RequestStore`."""

    def __init__(
        self,
        transport: httpx.AsyncBaseTransport,
        store: RequestStore,
    ) -> None:
        self._transport = transport
        self._store = store

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        force_fetch, store_fail = resolve_request_options(
            request.extensions,
            default_store_fail=self._store.config.store_fail,
        )
        stored, is_leader = await self._store.get_async(
            request,
            force_fetch=force_fetch,
            store_fail=store_fail,
        )
        if stored is not None:
            if is_leader:
                await self._store.release_async(request)
            return _response_from_stored(stored, request)

        if not is_leader:
            # See the matching comment in StoringTransport.handle_request: track
            # the re-entrant leadership status instead of discarding it, so a
            # redundant fetch is persisted and its gate entry is released.
            stored, is_leader = await self._store.get_async(
                request,
                force_fetch=False,
                store_fail=store_fail,
            )
            if stored is not None:
                if is_leader:
                    await self._store.release_async(request)
                return _response_from_stored(stored, request)

        try:
            response = await self._transport.handle_async_request(request)
            if is_leader:
                self._store.store(request, response, store_fail=store_fail)
            return response
        finally:
            if is_leader:
                await self._store.release_async(request)


class OfflineTransport(httpx.BaseTransport):
    """Serve API responses from the request store without network access."""

    def __init__(self, store: RequestStore) -> None:
        self._store = store

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        stored, is_leader = self._store.get_sync(request, force_fetch=False)
        try:
            if stored is None:
                raise RequestStoreError(
                    "No cached response available in offline mode",
                    request_key=request_key_from_httpx(request).digest(),
                    operation="get",
                )
            return _response_from_stored(stored, request)
        finally:
            if is_leader:
                self._store.release_sync(request)


class AsyncOfflineTransport(httpx.AsyncBaseTransport):
    """Async offline-only transport backed by the request store."""

    def __init__(self, store: RequestStore) -> None:
        self._store = store

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        stored, is_leader = await self._store.get_async(request, force_fetch=False)
        try:
            if stored is None:
                raise RequestStoreError(
                    "No cached response available in offline mode",
                    request_key=request_key_from_httpx(request).digest(),
                    operation="get",
                )
            return _response_from_stored(stored, request)
        finally:
            if is_leader:
                await self._store.release_async(request)
