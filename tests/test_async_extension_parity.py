"""Sync vs async extension method alignment for mirrored entity helpers."""

from __future__ import annotations

import importlib
import inspect

import pytest

import congressgov.services.extensions  # noqa: F401

importlib.import_module("congressgov.services.extensions.async")

from congressgov.models.base.references import (
    AmendmentRef,
    BillRef,
    CommitteeRef,
    MemberRef,
    NominationRef,
    TreatyRef,
)
from congressgov.models.base.types import CountRef, URL
from congressgov.models.entities.amendment import Amendment
from congressgov.models.entities.bill import Bill
from congressgov.models.entities.congress import Congress
from congressgov.models.entities.member import (
    CosponsoredLegislationItem,
    Member,
    SponsoredLegislationItem,
)
from congressgov.models.entities.sponsor import Cosponsor, Sponsor
from congressgov.services.core.async_method_registry import get_async_methods

# Model classes that should expose async mirrors for instance/url-follow helpers.
MIRRORED_EXTENSION_CLASSES = [
    Bill,
    Amendment,
    Member,
    Congress,
    SponsoredLegislationItem,
    CosponsoredLegislationItem,
    BillRef,
    MemberRef,
    AmendmentRef,
    CommitteeRef,
    TreatyRef,
    NominationRef,
    URL,
    CountRef,
    Sponsor,
    Cosponsor,
]

# Deprecated async aliases (sync counterparts are also deprecated).
DEPRECATED_ASYNC_METHODS = frozenset({"fetch_legislation_async"})

# Collection query helpers intentionally sync-only.
SYNC_ONLY_METHOD_PREFIXES = ("__",)
SYNC_ONLY_METHOD_NAMES = frozenset(
    {
        "fetch_legislation",
        "query",
        "filter",
        "group_by",
        "by_congress",
        "by_type",
        "by_chamber",
        "by_state",
        "by_party",
        "current",
        "democrats",
        "republicans",
        "enacted",
        "house_bills",
        "senate_bills",
        "house_amendments",
        "senate_amendments",
        "house_reports",
        "senate_reports",
        "house_prints",
        "senate_prints",
    }
)


def _sync_instance_methods(cls: type) -> set[str]:
    names: set[str] = set()
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith(SYNC_ONLY_METHOD_PREFIXES):
            continue
        if name in SYNC_ONLY_METHOD_NAMES:
            continue
        if name.endswith("_async"):
            continue
        names.add(name)
    return names


@pytest.mark.parametrize("model_cls", MIRRORED_EXTENSION_CLASSES)
def test_async_extension_methods_have_sync_counterpart(model_cls: type) -> None:
    async_methods = get_async_methods(model_cls)
    if not async_methods:
        pytest.skip(f"No async extension methods registered on {model_cls.__name__}")

    sync_methods = _sync_instance_methods(model_cls)
    for async_name in async_methods:
        if async_name in DEPRECATED_ASYNC_METHODS:
            continue
        sync_name = async_name.removesuffix("_async")
        assert sync_name in sync_methods, (
            f"{model_cls.__name__}.{async_name} has no sync counterpart {sync_name}()"
        )
        assert inspect.iscoroutinefunction(getattr(model_cls, async_name))
        assert not inspect.iscoroutinefunction(getattr(model_cls, sync_name))
