"""Store inspection, listing, and maintenance helpers."""

from __future__ import annotations

from typing import Any

from .policy import PolicyConfig, estimate_staleness
from .store import RequestStore


def list_keys(
    store: RequestStore,
    *,
    url_prefix: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[str]:
    list_fn = getattr(store.backend, "list_keys", None)
    if list_fn is None:
        raise NotImplementedError(
            f"{type(store.backend).__name__} does not support list_keys()"
        )
    return list_fn(url_prefix=url_prefix, limit=limit, offset=offset)


def purge_stale(store: RequestStore, *, policy: PolicyConfig | None = None) -> int:
    purge_fn = getattr(store.backend, "purge_stale", None)
    if purge_fn is None:
        raise NotImplementedError(
            f"{type(store.backend).__name__} does not support purge_stale()"
        )
    return purge_fn(policy=policy or store.config.policy)


def summarize_store(store: RequestStore) -> dict[str, Any]:
    """Return combined runtime and backend statistics."""
    summary = store.get_stats()
    summary["keys_sample"] = list_keys(store, limit=5)
    stale_count = 0
    iter_fn = getattr(store.backend, "iter_records", None)
    if iter_fn is not None:
        for record in iter_fn():
            path = (record.request_key or "").split(":", 1)[-1].split("?", 1)[0]
            policy = store.config.policy.resolve(path)
            estimate = estimate_staleness(record, policy=policy)
            if estimate.is_stale:
                stale_count += 1
        summary["stale_records"] = stale_count
    return summary


def print_store_stats(store: RequestStore) -> None:
    """Print a human-readable summary of store activity."""
    summary = summarize_store(store)
    backend = summary.get("backend", {})
    print("Request store stats:")
    print(f"  hits: {summary.get('hits', 0)}  misses: {summary.get('misses', 0)}")
    print(f"  hit rate: {summary.get('hit_rate', 0.0):.1%}")
    print(f"  records: {backend.get('records', summary.get('records', '?'))}")
    if "stale_records" in summary:
        print(f"  stale records: {summary['stale_records']}")
    if backend.get("path"):
        print(f"  path: {backend['path']}")
    if summary.get("keys_sample"):
        print("  recent keys:")
        for key in summary["keys_sample"]:
            print(f"    - {key}")
