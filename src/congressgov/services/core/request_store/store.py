"""Request store orchestrating policy, persistence, and in-flight deduplication."""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from congressgov.services.exceptions import RequestStoreError

from .backends.base import RequestStoreBackend
from .factory import create_backend
from .keys import request_key_digest, request_key_from_httpx
from .models import StoredResponse, normalize_stored_response_headers
from .policy import ChangePolicy, PolicyConfig, is_stale
from .policy_loader import load_policy_config
from .response_timestamps import extract_source_updated_at


def _default_store_config() -> StoreConfig:
    return StoreConfig(policy=load_policy_config())


@dataclass
class StoreConfig:
    """Runtime configuration for :class:`RequestStore`."""

    enabled: bool = True
    store_fail: bool = False
    policy: PolicyConfig = field(default_factory=load_policy_config)


class _SyncInFlightGate:
    """Coalesce concurrent sync requests for the same canonical key."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[str, threading.Event] = {}

    def leader_or_wait(self, key: str) -> bool:
        """
        Return True for the leader (performs fetch), False for followers (wait).

        Followers block until the leader completes and signals the gate.
        """
        with self._lock:
            event = self._events.get(key)
            if event is None:
                self._events[key] = threading.Event()
                return True
        event.wait()
        return False

    def release(self, key: str) -> None:
        with self._lock:
            event = self._events.pop(key, None)
        if event is not None:
            event.set()


class _AsyncInFlightGate:
    """Coalesce concurrent async requests for the same canonical key."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._events: dict[str, asyncio.Event] = {}

    async def leader_or_wait(self, key: str) -> bool:
        async with self._lock:
            event = self._events.get(key)
            if event is None:
                self._events[key] = asyncio.Event()
                return True
        await event.wait()
        return False

    async def release(self, key: str) -> None:
        async with self._lock:
            event = self._events.pop(key, None)
        if event is not None:
            event.set()


class RequestStore:
    """
    Persistent deduplicating store for raw API responses.

    Network calls for the same canonical request are blocked when a fresh stored
    response exists. Use ``force_fetch=True`` to bypass the store.
    """

    def __init__(
        self,
        backend: RequestStoreBackend | str | None = None,
        *,
        config: StoreConfig | None = None,
        workspace_root: Path | None = None,
    ) -> None:
        from pathlib import Path as _Path

        if backend is None or isinstance(backend, str):
            root = workspace_root
            if root is None:
                from congressgov.services.core.workspace import resolve_workspace

                root = resolve_workspace().root
            self.backend = create_backend(backend, workspace_root=_Path(root))
        else:
            self.backend = backend
        self.config = config or _default_store_config()
        self._sync_gate = _SyncInFlightGate()
        self._async_gate = _AsyncInFlightGate()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0,
            "store_errors": 0,
            "inflight_waits": 0,
        }
        self._stats_lock = threading.Lock()

    def resolve_policy(self, path: str) -> ChangePolicy:
        return self.config.policy.resolve(path)

    def _record(self, name: str, amount: int = 1) -> None:
        with self._stats_lock:
            self._stats[name] = self._stats.get(name, 0) + amount

    def _lookup(
        self,
        key: str,
        *,
        path: str,
        force_fetch: bool,
        store_fail: bool,
    ) -> StoredResponse | None:
        if not self.config.enabled or force_fetch:
            return None
        try:
            stored = self.backend.get(key)
        except Exception as exc:
            if store_fail:
                return None
            raise RequestStoreError(
                "Request store read failed",
                request_key=key,
                operation="get",
            ) from exc
        if stored is None:
            self._record("misses")
            return None
        policy = self.resolve_policy(path)
        if is_stale(stored, policy=policy):
            self._record("misses")
            return None
        self._record("hits")
        return stored

    def get_sync(
        self,
        request,
        *,
        force_fetch: bool = False,
        store_fail: bool | None = None,
    ) -> tuple[StoredResponse | None, bool]:
        """
        Lookup a stored response for a sync httpx request.

        Returns ``(stored_response, is_leader)``. Followers should wait on the
        in-flight gate before calling again.
        """
        effective_store_fail = (
            self.config.store_fail if store_fail is None else store_fail
        )
        key_obj = request_key_from_httpx(request)
        key = key_obj.digest()
        is_leader = self._sync_gate.leader_or_wait(key)
        if not is_leader:
            self._record("inflight_waits")
            stored = self._lookup(
                key,
                path=key_obj.url,
                force_fetch=force_fetch,
                store_fail=effective_store_fail,
            )
            return stored, False
        stored = self._lookup(
            key,
            path=key_obj.url,
            force_fetch=force_fetch,
            store_fail=effective_store_fail,
        )
        return stored, True

    async def get_async(
        self,
        request,
        *,
        force_fetch: bool = False,
        store_fail: bool | None = None,
    ) -> tuple[StoredResponse | None, bool]:
        effective_store_fail = (
            self.config.store_fail if store_fail is None else store_fail
        )
        key_obj = request_key_from_httpx(request)
        key = key_obj.digest()
        is_leader = await self._async_gate.leader_or_wait(key)
        if not is_leader:
            self._record("inflight_waits")
            stored = self._lookup(
                key,
                path=key_obj.url,
                force_fetch=force_fetch,
                store_fail=effective_store_fail,
            )
            return stored, False
        stored = self._lookup(
            key,
            path=key_obj.url,
            force_fetch=force_fetch,
            store_fail=effective_store_fail,
        )
        return stored, True

    def release_sync(self, request) -> None:
        self._sync_gate.release(request_key_digest(request))

    async def release_async(self, request) -> None:
        await self._async_gate.release(request_key_digest(request))

    @staticmethod
    def _response_body_bytes(response: httpx.Response) -> bytes:
        """Read streaming httpx responses before persisting their bodies."""
        try:
            return response.content
        except httpx.ResponseNotRead:
            return response.read()

    def store(
        self,
        request,
        response,
        *,
        store_fail: bool | None = None,
    ) -> None:
        """Persist a successful API response."""
        if not self.config.enabled:
            return
        if response.status_code != 200:
            return
        effective_store_fail = (
            self.config.store_fail if store_fail is None else store_fail
        )
        key_obj = request_key_from_httpx(request)
        key = key_obj.digest()
        policy = self.resolve_policy(key_obj.url)
        body = self._response_body_bytes(response)
        stored = StoredResponse(
            status_code=response.status_code,
            headers=normalize_stored_response_headers(
                {key: value for key, value in response.headers.items()}
            ),
            body=body,
            policy=policy.value,
            request_key=key,
            source_updated_at=extract_source_updated_at(body),
        )
        try:
            self.backend.put(key, stored)
            self._record("stores")
        except Exception as exc:
            self._record("store_errors")
            if effective_store_fail:
                return
            raise RequestStoreError(
                "Request store write failed",
                request_key=key,
                operation="put",
            ) from exc

    def get_stats(self) -> dict[str, Any]:
        with self._stats_lock:
            stats = dict(self._stats)
        stats["backend"] = self.backend.get_stats()
        total = stats["hits"] + stats["misses"]
        stats["hit_rate"] = stats["hits"] / total if total else 0.0
        return stats

    def close(self) -> None:
        self.backend.close()

    @classmethod
    def open(cls, connection: str | None = None, **kwargs) -> RequestStore:
        """Open the workspace default on-disk store when *connection* is omitted."""
        if connection is None:
            from congressgov.services.core.workspace import resolve_blob_connection

            connection = resolve_blob_connection()
        return cls(connection, **kwargs)
