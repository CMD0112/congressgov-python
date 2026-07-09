"""Backend protocol for request-store persistence."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from ..models import StoredResponse

if TYPE_CHECKING:
    from ..policy import PolicyConfig


class RequestStoreBackend(Protocol):
    """
    Canonical persistence interface for raw API responses.

    Implementations may use SQLite, files, Redis, or other engines while
    exposing the same lookup/store contract.
    """

    def get(self, key: str) -> StoredResponse | None:
        """Load a stored response by canonical request key."""
        ...

    def put(self, key: str, response: StoredResponse) -> None:
        """Persist a response under *key*."""
        ...

    def delete(self, key: str) -> bool:
        """Remove a stored response. Returns True when a record existed."""
        ...

    def contains(self, key: str) -> bool:
        """Return True when *key* exists in the backend."""
        ...

    def count(self) -> int:
        """Return total stored records."""
        ...

    def close(self) -> None:
        """Release backend resources."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Return backend-specific statistics."""
        ...


def purge_stale_records(
    backend: RequestStoreBackend,
    records: Iterable[StoredResponse],
    *,
    policy: "PolicyConfig | None" = None,
) -> int:
    """
    Delete stale records from *backend*, shared across all backend implementations.

    *records* is typically ``backend.iter_records()``; kept as an explicit
    argument so backends can control snapshotting (e.g. materializing to a
    list before deleting while iterating).
    """
    from ..policy import PolicyConfig, is_stale

    config = policy or PolicyConfig()
    removed = 0
    for stored in records:
        path = (stored.request_key or "").split(":", 1)[-1].split("?", 1)[0]
        resolved = config.resolve(path)
        if is_stale(stored, policy=resolved) and backend.delete(stored.request_key or ""):
            removed += 1
    return removed
