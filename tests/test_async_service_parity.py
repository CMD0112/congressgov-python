"""Sync vs async middleware: public API alignment for all adopted services."""

import inspect

import pytest

# (sync module, async class name on middleware.async_api)
SYNC_ASYNC_PAIRS = [
    ("congressgov.services.bill", "AsyncBill"),
    ("congressgov.services.amendment", "AsyncAmendment"),
    ("congressgov.services.member", "AsyncMember"),
    ("congressgov.services.committee", "AsyncCommittee"),
    ("congressgov.services.hearing", "AsyncHearing"),
    ("congressgov.services.nomination", "AsyncNomination"),
    ("congressgov.services.treaty", "AsyncTreaty"),
    ("congressgov.services.house_vote", "AsyncHouseVote"),
    ("congressgov.services.summaries", "AsyncSummaries"),
    ("congressgov.services.crsreport", "AsyncCRSReport"),
    ("congressgov.services.house_communication", "AsyncHouseCommunication"),
    ("congressgov.services.senate_communication", "AsyncSenateCommunication"),
    ("congressgov.services.committee_meeting", "AsyncCommitteeMeeting"),
    ("congressgov.services.committee_report", "AsyncCommitteeReport"),
    ("congressgov.services.committee_print", "AsyncCommitteePrint"),
    ("congressgov.services.congress", "AsyncCongress"),
    ("congressgov.services.house_requirement", "AsyncHouseRequirement"),
    ("congressgov.services.congressional_record", "AsyncCongressionalRecord"),
    ("congressgov.services.bound_congressional_record", "AsyncBoundCongressionalRecord"),
    ("congressgov.services.daily_congressional_record", "AsyncDailyCongressionalRecord"),
]


def _service_class(sync_mod):
    for _name, obj in vars(sync_mod).items():
        if (
            inspect.isclass(obj)
            and obj.__module__ == sync_mod.__name__
            and not _name.startswith("_")
            and issubclass(obj, object)
            and _name[0].isupper()
        ):
            return obj
    raise AssertionError(f"No service class in {sync_mod.__name__}")


def _public_callables(cls: type) -> dict[str, object]:
    return {
        name: obj
        for name, obj in inspect.getmembers(cls)
        if not name.startswith("_")
        and callable(obj)
        and not inspect.isclass(obj)
        and name != "expand"
    }


@pytest.mark.parametrize("sync_path,async_name", SYNC_ASYNC_PAIRS)
def test_async_exposes_same_method_names_as_sync(sync_path: str, async_name: str) -> None:
    import importlib

    sync_mod = importlib.import_module(sync_path)
    sync_cls = _service_class(sync_mod)
    async_mod = importlib.import_module("congressgov.services.async_api")
    async_cls = getattr(async_mod, async_name)
    sync_methods = set(_public_callables(sync_cls))
    async_methods = set(_public_callables(async_cls))
    missing = sync_methods - async_methods
    assert not missing, (
        f"{async_name} missing sync methods from {sync_path}: {sorted(missing)}"
    )


@pytest.mark.parametrize("sync_path,async_name", SYNC_ASYNC_PAIRS)
def test_async_method_signatures_match_sync(sync_path: str, async_name: str) -> None:
    import importlib

    sync_mod = importlib.import_module(sync_path)
    sync_cls = _service_class(sync_mod)
    async_mod = importlib.import_module("congressgov.services.async_api")
    async_cls = getattr(async_mod, async_name)
    for name in _public_callables(sync_cls):
        if name not in _public_callables(async_cls):
            continue
        sync_sig = inspect.signature(getattr(sync_cls, name))
        async_sig = inspect.signature(getattr(async_cls, name))
        assert list(sync_sig.parameters) == list(async_sig.parameters), (
            f"{sync_path}.{name} parameters differ: {sync_sig} vs {async_sig}"
        )


def test_all_adopted_services_have_hand_async_modules() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "src" / "congressgov" / "services" / "async_api"
    for sync_path, _async_name in SYNC_ASYNC_PAIRS:
        stem = sync_path.rsplit(".", 1)[-1]
        hand_module = root / f"{stem}.py"
        assert hand_module.is_file(), f"Missing hand async module: {hand_module}"
