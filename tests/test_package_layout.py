"""Package namespace layout (src/congressgov, 2.0)."""

from __future__ import annotations

import importlib
import sys
import warnings

import pytest


def _package_path_fragment(module_file: str, fragment: str) -> bool:
    normalized = module_file.replace("\\", "/")
    return fragment in normalized or f"src/{fragment}" in normalized


def test_src_layout_services_and_models() -> None:
    import congressgov
    import congressgov.services as services
    import congressgov.models as cg_models

    assert congressgov.__file__ is not None
    assert _package_path_fragment(congressgov.__file__, "congressgov/__init__.py")
    assert services.__file__ is not None
    assert _package_path_fragment(services.__file__, "congressgov/services")
    assert cg_models.__file__ is not None
    assert _package_path_fragment(cg_models.__file__, "congressgov/models")


def test_congressgov_services_namespace() -> None:
    import congressgov.services as services
    from congressgov.services.bill import Bill as BillService

    assert services.Bill is BillService


def test_congressgov_models_namespace() -> None:
    import congressgov.models as cg_models
    from congressgov.models.entities.bill import Bill as BillEntity
    from congressgov.models.entities.member import Member as MemberEntity

    assert cg_models.Bill is BillEntity
    assert cg_models.Member is MemberEntity


def test_congressgov_client_package() -> None:
    from congressgov.client import AuthenticatedClient, Client
    from congressgov._client import AuthenticatedClient as RawAuth, Client as RawClient

    assert AuthenticatedClient is RawAuth
    assert Client is RawClient


@pytest.mark.parametrize(
    "legacy_name",
    ["middleware", "models", "congress_gov_api_client"],
)
def test_legacy_top_level_packages_not_importable(
    legacy_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delitem(sys.modules, legacy_name, raising=False)
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(legacy_name)


def test_congressgov_services_no_deprecation_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("congressgov", "congressgov.services"):
        monkeypatch.delitem(sys.modules, name, raising=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        importlib.import_module("congressgov.services")
