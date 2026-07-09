"""Codegen-adopted API client packages: get_* layout without duplicate legacy endpoint modules."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "src" / "congressgov" / "_client" / "api"

GET_ONLY_PACKAGES = (
    "bill",
    "amendments",
    "member",
    "committee",
    "hearing",
    "nomination",
    "treaty",
    "house_vote",
    "summaries",
    "crsreport",
    "house_communication",
    "senate_communication",
    "committee_meeting",
    "committee_report",
    "committee_print",
    "congress",
    "house_requirement",
    "congressional_record",
    "bound_congressional_record",
    "daily_congressional_record",
)

KNOWN_LEGACY_SHIMS = {
    "bill": {"bill_details.py", "bill_actions.py"},
    "amendments": {"amendmentdetails.py", "amendmentactions.py"},
    "member": {"member_details.py", "member_list.py"},
    "committee": {"committee_details.py", "committee_bills_list.py"},
    "hearing": {"hearing_detail.py", "hearing_list_by_congress.py"},
    "nomination": {"nomination_detail.py", "nomination_actions.py"},
    "treaty": {"treaty_detail.py", "treaty_actions.py"},
    "house_vote": {"house_vote_details.py", "house_vote_list.py"},
    "summaries": {"bill_summaries_all.py"},
    "crsreport": {"crsreport_details.py", "crsreport_list.py"},
    "house_communication": {"house_communication_detail.py", "house_communication_list.py"},
    "senate_communication": {"senate_communication_detail.py", "senate_communication_list.py"},
    "committee_meeting": {"committee_meeting_detail.py", "committee_meeting_list.py"},
    "committee_report": {"committee_report_details.py", "committee_reports_list.py"},
    "committee_print": {"committee_print_detail.py", "committee_print_list.py"},
    "congress": {"congress_details.py", "congress_list.py"},
    "house_requirement": {"house_requirement_detail.py", "house_requirement_list.py"},
    "congressional_record": {"congressional_record_list.py"},
    "bound_congressional_record": {"bound_congressional_record_list.py"},
    "daily_congressional_record": {"daily_congressional_record_list.py"},
}


def test_get_only_packages_have_no_legacy_duplicate_modules() -> None:
    for package in GET_ONLY_PACKAGES:
        package_dir = API_ROOT / package
        assert package_dir.is_dir(), f"Missing api package: {package}"
        py_files = [p.name for p in package_dir.glob("*.py")]
        for name in py_files:
            assert name == "__init__.py" or name.startswith("get_"), (
                f"{package}/{name} should be removed (use get_* only)"
            )
        for legacy_name in KNOWN_LEGACY_SHIMS[package]:
            assert not (package_dir / legacy_name).exists(), (
                f"{package}/{legacy_name} duplicate should not exist"
            )


def test_pilot_init_exports_sync_names() -> None:
    from congressgov._client.api.amendments import amendment_details_sync
    from congressgov._client.api.bill import bill_details_sync
    from congressgov._client.api.committee import committee_details_sync
    from congressgov._client.api.member import member_details_sync

    assert callable(bill_details_sync)
    assert callable(amendment_details_sync)
    assert callable(member_details_sync)
    assert callable(committee_details_sync)


def test_tier2_init_exports_sync_names() -> None:
    from congressgov._client.api.hearing import hearing_detail_sync, hearing_list_sync
    from congressgov._client.api.nomination import nomination_detail_sync
    from congressgov._client.api.treaty import treaty_detail_sync, treaty_list_sync

    assert callable(hearing_detail_sync)
    assert callable(hearing_list_sync)
    assert callable(nomination_detail_sync)
    assert callable(treaty_detail_sync)
    assert callable(treaty_list_sync)


def test_tier3b_init_exports_sync_names() -> None:
    from congressgov._client.api.summaries import bill_summaries_all_sync
    from congressgov._client.api.crsreport import crsreport_details_sync, crsreport_sync
    from congressgov._client.api.house_communication import house_communication_detail_sync
    from congressgov._client.api.senate_communication import senate_communication_detail_sync
    from congressgov._client.api.house_vote import house_vote_details_sync

    assert callable(bill_summaries_all_sync)
    assert callable(crsreport_sync)
    assert callable(crsreport_details_sync)
    assert callable(house_communication_detail_sync)
    assert callable(senate_communication_detail_sync)
    assert callable(house_vote_details_sync)


def test_tier4_init_exports_sync_names() -> None:
    from congressgov._client.api.committee_meeting import (
        committee_meeting_detail_sync,
        committee_meeting_list_sync,
    )
    from congressgov._client.api.committee_report import (
        committee_report_details_sync,
        committee_reports_sync,
    )
    from congressgov._client.api.committee_print import (
        committee_print_detail_sync,
        committee_print_list_sync,
    )

    assert callable(committee_meeting_detail_sync)
    assert callable(committee_meeting_list_sync)
    assert callable(committee_report_details_sync)
    assert callable(committee_reports_sync)
    assert callable(committee_print_detail_sync)
    assert callable(committee_print_list_sync)


def test_tier6_init_exports_daily_congressional_record_sync_names() -> None:
    from congressgov._client.api.daily_congressional_record import (
        daily_congressional_record_list_sync,
    )

    assert callable(daily_congressional_record_list_sync)


def test_tier5_init_exports_sync_names() -> None:
    from congressgov._client.api.congress import congress_details_sync, congress_list_sync
    from congressgov._client.api.house_requirement import house_requirement_detail_sync
    from congressgov._client.api.congressional_record import congressional_record_list_sync
    from congressgov._client.api.bound_congressional_record import (
        bound_congressional_record_list_sync,
    )

    assert callable(congress_details_sync)
    assert callable(congress_list_sync)
    assert callable(house_requirement_detail_sync)
    assert callable(congressional_record_list_sync)
    assert callable(bound_congressional_record_list_sync)
