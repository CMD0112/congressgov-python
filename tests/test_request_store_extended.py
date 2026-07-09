"""Additional request store tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from congressgov.services.client_factory import create_offline_client
from congressgov.services.core.request_store import (
    ChangePolicy,
    PolicyConfig,
    RequestStore,
    current_congress,
    extract_congress_from_path,
    load_policy_config,
    purge_stale,
)
from congressgov.services.core.request_store.response_timestamps import extract_source_updated_at
from congressgov.services.core.request_store.models import StoredResponse


def test_extract_congress_from_path() -> None:
    assert extract_congress_from_path("/bill/118/hr/1") == 118
    assert extract_congress_from_path("/member") is None


def test_closed_congress_uses_permanent_policy() -> None:
    old_congress = current_congress() - 2
    config = PolicyConfig(closed_congress_permanent=True)
    assert config.resolve(f"/bill/{old_congress}/hr/1") == ChangePolicy.PERMANENT


def test_extract_source_updated_at_from_payload() -> None:
    body = json.dumps({"bill": {"updateDate": "2024-01-15T12:00:00Z"}}).encode()
    ts = extract_source_updated_at(body)
    assert ts is not None
    assert ts.year == 2024


def test_load_policy_config_default() -> None:
    config = load_policy_config()
    assert config.resolve("/bill") == ChangePolicy.DYNAMIC


def test_offline_client_raises_without_cached_response() -> None:
    # Import after other tests may have reloaded congressgov.services.* via sys.modules.
    from congressgov.services.exceptions import RequestStoreError as OfflineStoreError

    client = create_offline_client(request_store=":memory:")
    with pytest.raises(OfflineStoreError, match="offline"):
        client.get_httpx_client().get("https://api.congress.gov/v3/bill/118/hr/1")


def test_purge_stale_removes_expired_records() -> None:
    store = RequestStore(
        ":memory:",
    )
    backend = store.backend
    stale = StoredResponse(
        status_code=200,
        headers={},
        body=b"{}",
        fetched_at=datetime.now(timezone.utc) - timedelta(hours=2),
        policy=ChangePolicy.VOLATILE.value,
        request_key="GET:/bill/118/hr/1?format=json",
    )
    backend.put(stale.request_key, stale)
    removed = purge_stale(store)
    assert removed == 1
    assert backend.count() == 0


def test_cli_stats_command(capsys) -> None:
    from congressgov.services.core.request_store.__main__ import main

    assert main(["--store", ":memory:", "stats"]) == 0
    output = capsys.readouterr().out
    assert "Request store stats" in output
