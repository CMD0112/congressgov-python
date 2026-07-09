"""Tests for the persistent request store."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from congressgov.services.core.request_store import (
    ChangePolicy,
    PolicyConfig,
    RequestStore,
    StoreConfig,
    attach_request_store,
    create_backend,
    estimate_staleness,
    fetch_options,
    get_attached_store,
    is_stale,
    request_key_from_httpx,
)
from congressgov.services.core.request_store.backends.memory import MemoryRequestStoreBackend
from congressgov.services.core.request_store.models import StoredResponse
from congressgov.services.core.request_store.transport import StoringTransport, _response_from_stored
from congressgov.services.exceptions import RequestStoreError


def _json_response(payload: dict, request: httpx.Request) -> httpx.Response:
    body = json.dumps(payload).encode("utf-8")
    return httpx.Response(200, content=body, request=request)


def test_request_key_strips_api_key() -> None:
    request = httpx.Request(
        "GET",
        "https://api.congress.gov/v3/bill/118/hr/1?format=json&api_key=secret",
    )
    key = request_key_from_httpx(request)
    assert key.query == (("format", "json"),)
    assert "api_key" not in key.digest()


def test_request_key_is_stable_for_param_order() -> None:
    req_a = httpx.Request("GET", "https://api.congress.gov/v3/bill?limit=10&offset=0")
    req_b = httpx.Request("GET", "https://api.congress.gov/v3/bill?offset=0&limit=10")
    assert request_key_from_httpx(req_a).digest() == request_key_from_httpx(req_b).digest()


def test_policy_permanent_never_stale() -> None:
    stored = StoredResponse(
        status_code=200,
        headers={},
        body=b"{}",
        fetched_at=datetime.now(timezone.utc) - timedelta(days=365),
        policy=ChangePolicy.PERMANENT.value,
    )
    assert is_stale(stored, policy=ChangePolicy.PERMANENT) is False


def test_policy_dynamic_becomes_stale() -> None:
    stored = StoredResponse(
        status_code=200,
        headers={},
        body=b"{}",
        fetched_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        policy=ChangePolicy.DYNAMIC.value,
    )
    assert is_stale(stored, policy=ChangePolicy.DYNAMIC) is True


def test_sqlite_backend_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "store.db"
    backend = create_backend(f"sqlite:///{db_path}")
    stored = StoredResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        body=b'{"ok": true}',
        policy="moderate",
        request_key="GET:/bill/118/hr/1?format=json",
    )
    backend.put(stored.request_key, stored)
    loaded = backend.get(stored.request_key)
    assert loaded is not None
    assert loaded.body == stored.body
    assert loaded.headers == stored.headers
    backend.close()


def test_file_backend_roundtrip(tmp_path) -> None:
    backend = create_backend(f"file:///{tmp_path / 'store'}")
    stored = StoredResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        body=b'{"ok": true}',
        policy="moderate",
        request_key="GET:/bill/118/hr/1?format=json",
    )
    backend.put(stored.request_key, stored)
    loaded = backend.get(stored.request_key)
    assert loaded is not None
    assert loaded.body == stored.body
    backend.close()


def test_estimate_staleness_ramps_with_age() -> None:
    from datetime import timedelta

    fresh = StoredResponse(
        status_code=200,
        headers={},
        body=b"{}",
        fetched_at=datetime.now(timezone.utc),
        policy=ChangePolicy.MODERATE.value,
    )
    old = StoredResponse(
        status_code=200,
        headers={},
        body=b"{}",
        fetched_at=datetime.now(timezone.utc) - timedelta(hours=2),
        policy=ChangePolicy.MODERATE.value,
    )
    fresh_est = estimate_staleness(fresh, policy=ChangePolicy.MODERATE)
    old_est = estimate_staleness(old, policy=ChangePolicy.MODERATE)
    assert fresh_est.change_likelihood < old_est.change_likelihood
    assert old_est.is_stale is True
    assert old_est.likely_changed is True


def test_store_fail_closed_on_read_error() -> None:
    class BrokenBackend(MemoryRequestStoreBackend):
        def get(self, key: str):
            raise OSError("disk unavailable")

    store = RequestStore(BrokenBackend(), config=StoreConfig(store_fail=False))
    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1")
    with pytest.raises(RequestStoreError, match="read failed"):
        store.get_sync(request)


def test_store_fail_open_on_read_error() -> None:
    class BrokenBackend(MemoryRequestStoreBackend):
        def get(self, key: str):
            raise OSError("disk unavailable")

    store = RequestStore(BrokenBackend(), config=StoreConfig(store_fail=True))
    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1")
    stored, is_leader = store.get_sync(request)
    assert stored is None
    assert is_leader is True
    store.release_sync(request)


def test_storing_transport_deduplicates_requests() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return _json_response({"requestNumber": calls["count"]}, request)

    transport = httpx.MockTransport(handler)
    store = RequestStore(
        MemoryRequestStoreBackend(),
        config=StoreConfig(policy=PolicyConfig(default_policy=ChangePolicy.PERMANENT)),
    )
    storing = StoringTransport(transport, store)

    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1?format=json")
    first = storing.handle_request(request)
    second = storing.handle_request(request)

    assert calls["count"] == 1
    assert json.loads(first.content) == json.loads(second.content) == {"requestNumber": 1}


def test_force_fetch_bypasses_store() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return _json_response({"n": calls["count"]}, request)

    transport = httpx.MockTransport(handler)
    store = RequestStore(
        MemoryRequestStoreBackend(),
        config=StoreConfig(policy=PolicyConfig(default_policy=ChangePolicy.PERMANENT)),
    )
    storing = StoringTransport(transport, store)

    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1")
    storing.handle_request(request)

    forced = httpx.Request(
        "GET",
        "https://api.congress.gov/v3/bill/118/hr/1",
        extensions={"congressgov": {"force_fetch": True}},
    )
    with fetch_options(force_fetch=True):
        storing.handle_request(forced)

    assert calls["count"] == 2


def test_inflight_dedup_single_network_call() -> None:
    calls = {"count": 0}
    start = threading.Barrier(3)

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        time.sleep(0.05)
        return _json_response({"n": calls["count"]}, request)

    transport = httpx.MockTransport(handler)
    store = RequestStore(
        MemoryRequestStoreBackend(),
        config=StoreConfig(policy=PolicyConfig(default_policy=ChangePolicy.PERMANENT)),
    )
    storing = StoringTransport(transport, store)
    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1")
    results: list[bytes] = []

    def worker() -> None:
        start.wait()
        response = storing.handle_request(request)
        results.append(response.content)

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert calls["count"] == 1
    assert len(results) == 3
    assert len(set(results)) == 1


def test_attach_request_store_wraps_client() -> None:
    from congressgov._client import Client

    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return _json_response({"n": calls["count"]}, request)

    raw = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.congress.gov/v3")
    client = Client(base_url="https://api.congress.gov/v3")
    client.set_httpx_client(raw)

    store = RequestStore(":memory:", config=StoreConfig(policy=PolicyConfig(default_policy=ChangePolicy.PERMANENT)))
    attach_request_store(client, store)

    httpx_client = client.get_httpx_client()
    url = "/bill/118/hr/1"
    httpx_client.get(url)
    httpx_client.get(url)

    assert calls["count"] == 1
    assert get_attached_store(client) is store


def test_store_reads_streaming_response_before_persisting() -> None:
    payload = b'{"requestNumber": 1}'
    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1?format=json")

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=req, stream=httpx.ByteStream(payload))

    transport = httpx.MockTransport(handler)
    store = RequestStore(
        MemoryRequestStoreBackend(),
        config=StoreConfig(policy=PolicyConfig(default_policy=ChangePolicy.PERMANENT)),
    )
    storing = StoringTransport(transport, store)

    response = storing.handle_request(request)

    assert json.loads(response.content) == {"requestNumber": 1}
    stored, _ = store.get_sync(request)
    assert stored is not None
    assert stored.body == payload


def test_response_from_stored_ignores_content_encoding_for_decoded_body() -> None:
    request = httpx.Request("GET", "https://api.congress.gov/v3/bill/118/hr/1")
    stored = StoredResponse(
        status_code=200,
        headers={"content-type": "application/json", "content-encoding": "gzip"},
        body=b'{"ok": true}',
        policy="permanent",
        request_key="GET:/bill/118/hr/1?format=json",
    )

    response = _response_from_stored(stored, request)

    assert json.loads(response.content) == {"ok": True}
