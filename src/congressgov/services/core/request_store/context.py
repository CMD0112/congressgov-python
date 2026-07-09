"""Per-request and context-scoped store options."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

_force_fetch: ContextVar[bool] = ContextVar("congressgov_force_fetch", default=False)
_store_fail: ContextVar[bool | None] = ContextVar("congressgov_store_fail", default=None)

CONGRESSGOV_EXT = "congressgov"


def get_force_fetch() -> bool:
    return _force_fetch.get()


def get_store_fail(default: bool = False) -> bool:
    value = _store_fail.get()
    return default if value is None else value


@contextmanager
def fetch_options(
    *,
    force_fetch: bool = False,
    store_fail: bool | None = None,
) -> Iterator[None]:
    """
    Temporarily override fetch behavior for nested API calls.

    Example:
        with fetch_options(force_fetch=True):
            bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
    """
    force_token = _force_fetch.set(force_fetch)
    fail_token = _store_fail.set(store_fail)
    try:
        yield
    finally:
        _force_fetch.reset(force_token)
        _store_fail.reset(fail_token)


def resolve_request_options(
    request_extensions: dict,
    *,
    default_store_fail: bool,
) -> tuple[bool, bool]:
    """Merge httpx request extensions with context-scoped options."""
    ext = request_extensions.get(CONGRESSGOV_EXT, {})
    force_fetch = bool(ext.get("force_fetch", get_force_fetch()))
    if "store_fail" in ext:
        store_fail = bool(ext["store_fail"])
    else:
        store_fail = get_store_fail(default_store_fail)
    return force_fetch, store_fail
