"""Public API facade and packaging smoke tests."""

from __future__ import annotations

import importlib
import warnings

import pytest


def test_congressgov_exports_match_services() -> None:
    import congressgov
    import congressgov.services as services
    from congressgov.models.entities.bill import Summary as SummaryModel

    assert congressgov.Bill is services.Bill
    assert congressgov.Member is services.Member
    assert congressgov.Summary is SummaryModel
    assert congressgov.get_client_from_env is services.get_client_from_env
    assert congressgov.__version__ == services.__version__


def test_congressgov_async_api() -> None:
    from congressgov.async_api import AsyncBill
    from congressgov.services.async_api import AsyncBill as MiddlewareAsyncBill

    assert AsyncBill is MiddlewareAsyncBill


def test_congressgov_client() -> None:
    from congressgov.client import AuthenticatedClient, Client
    from congressgov._client import AuthenticatedClient as RawAuth, Client as RawClient

    assert AuthenticatedClient is RawAuth
    assert Client is RawClient


def test_congressgov_lazy_extra_requires_install(monkeypatch: pytest.MonkeyPatch) -> None:
    from importlib import import_module as real_import_module
    import sys

    def fail_caching_import(name: str, package: str | None = None):  # noqa: ANN001
        if name in (".caching", ".rate_limiting") or name.endswith(
            (".caching", ".rate_limiting")
        ):
            raise ImportError("simulated missing cache stack")
        return real_import_module(name, package)

    # Only reset the top-level "congressgov" and "congressgov.services" module
    # objects (not the whole congressgov.services.* submodule tree). Popping
    # deeper submodules like extensions/core/bill/member would force them to
    # re-run their top-level @register_method(...) side effects against the
    # (never-reloaded) model classes, permanently rebinding methods to a module
    # namespace that gets discarded when monkeypatch restores sys.modules at
    # teardown -- corrupting later tests. A fresh "congressgov.services" module
    # object is sufficient: its globals() start empty, so the lazy `__getattr__`
    # export cache (e.g. CacheConfig) can't already be populated from an earlier
    # test, while unpopped submodules like `extensions` are simply re-bound from
    # the existing sys.modules cache instead of re-executed.
    for name in ("congressgov", "middleware", "congressgov.services"):
        monkeypatch.delitem(sys.modules, name, raising=False)

    import congressgov

    monkeypatch.setattr(congressgov.services, "import_module", fail_caching_import)

    with pytest.raises(ImportError, match=r"congressgov\[cache\]"):
        _ = congressgov.CacheConfig


def test_import_congressgov_no_deprecation_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    for name in ("congressgov",):
        monkeypatch.delitem(sys.modules, name, raising=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        importlib.import_module("congressgov")
