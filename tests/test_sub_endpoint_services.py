"""Unit tests for v0.5.0 hand sub-endpoint service methods."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _response(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.content = json.dumps(payload).encode()
    return resp


def test_committee_get_by_congress() -> None:
    from congressgov.services.committee import Committee

    client = MagicMock()
    payload = {"data": {"name": "HSAG", "systemCode": "hsag00"}}
    with patch(
        "congressgov.services.committee.committee_by_congress_detailed",
        return_value=_response(payload),
    ) as mock_api:
        result = Committee().get_by_congress(
            client=client,
            congress=118,
            chamber="house",
            committee_code="hsag00",
        )
    mock_api.assert_called_once()
    assert result.name == "HSAG"


def test_committee_print_get_text() -> None:
    from congressgov.services.committee_print import CommitteePrint

    client = MagicMock()
    payload = {"data": [{"url": "https://example.com/text.pdf", "type": "PDF"}]}
    with patch(
        "congressgov.services.committee_print.committee_print_text_sync",
        return_value=_response(payload),
    ):
        result = CommitteePrint().get_text(
            client=client, congress=118, chamber="house", jacket_number=1
        )
    assert len(result) == 1


def test_committee_report_get_text() -> None:
    from congressgov.services.committee_report import CommitteeReport

    client = MagicMock()
    payload = {"data": [{"url": "https://example.com/report.pdf"}]}
    with patch(
        "congressgov.services.committee_report.committee_report_id_text_sync",
        return_value=_response(payload),
    ):
        result = CommitteeReport().get_text(
            client=client, congress=118, report_type="hrpt", report_number=1
        )
    assert len(result) == 1


def test_house_vote_list_by_congress_session() -> None:
    from congressgov.services.house_vote import HouseVote

    client = MagicMock()
    payload = {"data": {"houseRollCallVotes": []}}
    with patch(
        "congressgov.services.house_vote.house_vote_list_congress_session_sync",
        return_value=_response(payload),
    ) as mock_api:
        HouseVote().list_by_congress_session(client=client, congress=118, session=1)
    mock_api.assert_called_once()


def test_member_list_by_congress() -> None:
    from congressgov.services.member import Member

    client = MagicMock()
    payload = {"data": {"members": []}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(payload),
    ) as mock_api:
        Member().list_by_congress(client=client, congress=118)
    mock_api.assert_called_once()


def test_member_list_by_congress_fetch_all() -> None:
    from congressgov.services.member import Member

    client = MagicMock()
    page1 = {"data": {"members": [{"bioguideId": f"M{i:03d}"} for i in range(250)]}}
    page2 = {"data": {"members": [{"bioguideId": "Z000001"}]}}

    with patch(
        "congressgov.services.member.member_congress_list_sync",
        side_effect=[_response(page1), _response(page2)],
    ) as mock_api:
        result = Member().list_by_congress(
            client=client, congress=118, fetch_all=True
        )

    assert mock_api.call_count == 2
    assert mock_api.call_args_list[0].kwargs["offset"] == 0
    assert mock_api.call_args_list[0].kwargs["limit"] == 250
    assert mock_api.call_args_list[1].kwargs["offset"] == 250
    assert len(result.members) == 251


def test_congress_get_members_fetch_all() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.entities.congress import Congress

    client = MagicMock()
    congress = Congress.model_validate({"number": 118})
    congress.client = client
    page1 = {"data": {"members": [{"bioguideId": f"M{i:03d}"} for i in range(250)]}}
    page2 = {"data": {"members": [{"bioguideId": "A000374"}]}}

    with patch(
        "congressgov.services.member.member_congress_list_sync",
        side_effect=[_response(page1), _response(page2)],
    ) as mock_api:
        result = congress.get_members(fetch_all=True)

    assert mock_api.call_count == 2
    assert len(result.members) == 251


def test_congress_get_members() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.entities.congress import Congress

    client = MagicMock()
    congress = Congress.model_validate({"number": 118})
    congress.client = client
    payload = {"data": {"members": [{"bioguideId": "A000374"}]}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(payload),
    ) as mock_api:
        result = congress.get_members()

    mock_api.assert_called_once()
    assert mock_api.call_args.kwargs["congress"] == 118
    assert result.members is not None
    assert len(result.members) == 1


def test_congress_get_members_requires_number() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.entities.congress import Congress

    congress = Congress.model_validate({"name": "Current session"})
    with pytest.raises(ValueError, match="Congress.number"):
        congress.get_members(client=MagicMock())


def test_congress_get_members_infers_from_name() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.entities.congress import Congress

    client = MagicMock()
    congress = Congress.model_validate({"name": "119th Congress"})
    congress.client = client
    payload = {"data": {"members": []}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(payload),
    ) as mock_api:
        congress.get_members()

    assert congress.number == 119
    assert mock_api.call_args.kwargs["congress"] == 119


def test_congress_get_members_infers_from_url() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.base.model import ApiEnvelope
    from congressgov.models.entities.congress import Congresses

    client = MagicMock()
    payload = {
        "congresses": [
            {
                "name": "119th Congress",
                "startYear": "2025",
                "endYear": "2026",
                "url": "https://api.congress.gov/v3/congress/119?format=json",
            }
        ]
    }
    congress = Congresses.model_validate(
        ApiEnvelope.model_validate(payload).data
    ).congresses[0]
    congress.client = client
    members_payload = {"data": {"members": [{"bioguideId": "A000374"}]}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(members_payload),
    ) as mock_api:
        result = congress.get_members()

    assert congress.number == 119
    assert mock_api.call_args.kwargs["congress"] == 119
    assert len(result.members) == 1


def test_congress_get_members_uses_congress_alias() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.models.entities.congress import Congress

    client = MagicMock()
    congress = Congress.model_validate({"name": "118th Congress"})
    congress.congress = 118
    congress.client = client
    payload = {"data": {"members": []}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(payload),
    ) as mock_api:
        congress.get_members()

    assert mock_api.call_args.kwargs["congress"] == 118


def test_congress_service_get_backfills_number_for_get_members() -> None:
    import congressgov.services.extensions.congress  # noqa: F401

    from congressgov.services.congress import Congress as CongressService

    client = MagicMock()
    # API payload omits number; service should backfill from the request path param.
    payload = {"congress": {"name": "118th Congress", "startYear": 2023, "endYear": 2024}}
    with patch(
        "congressgov.services.congress.congress_details_sync",
        return_value=_response(payload),
    ):
        congress = CongressService(client=client).get(congress=118)

    assert congress.number == 118

    members_payload = {"data": {"members": [{"bioguideId": "A000374"}]}}
    with patch(
        "congressgov.services.member.member_congress_list_sync",
        return_value=_response(members_payload),
    ) as mock_api:
        result = congress.get_members()

    assert mock_api.call_args.kwargs["congress"] == 118
    assert len(result.members) == 1


def test_nomination_get_nominees() -> None:
    from congressgov.services.nomination import Nomination

    client = MagicMock()
    payload = {"data": {"nominees": []}}
    with patch(
        "congressgov.services.nomination.nominees_sync",
        return_value=_response(payload),
    ) as mock_api:
        Nomination().get_nominees(
            client=client, congress=118, nomination_number=1, ordinal=1
        )
    mock_api.assert_called_once()


def test_treaty_get_actions() -> None:
    from congressgov.services.treaty import Treaty

    client = MagicMock()
    payload = {"data": {"actions": []}}
    with patch(
        "congressgov.services.treaty.treaty_actions_sync",
        return_value=_response(payload),
    ) as mock_api:
        Treaty().get_actions(client=client, congress=118, treaty_number=1)
    mock_api.assert_called_once()


def test_api_coverage_has_no_service_method_gaps() -> None:
    import json as json_mod

    coverage_path = REPO_ROOT / "docs" / "api_coverage.json"
    assert coverage_path.is_file(), "Run poetry run api-coverage-matrix"
    rows = json_mod.loads(coverage_path.read_text(encoding="utf-8"))
    gaps = [r for r in rows if r["coverage"] == "service_method"]
    assert not gaps, f"service_method gaps remain: {gaps}"


@pytest.mark.parametrize(
    "sync_path,async_name,method",
    [
        ("congressgov.services.committee", "AsyncCommittee", "get_by_congress"),
        ("congressgov.services.committee_print", "AsyncCommitteePrint", "get_text"),
        ("congressgov.services.committee_report", "AsyncCommitteeReport", "get_text"),
        ("congressgov.services.house_vote", "AsyncHouseVote", "list_by_congress_session"),
        ("congressgov.services.member", "AsyncMember", "list_by_congress"),
        ("congressgov.services.nomination", "AsyncNomination", "get_nominees"),
        ("congressgov.services.treaty", "AsyncTreaty", "get_actions"),
    ],
)
def test_async_sub_endpoints_exist(sync_path: str, async_name: str, method: str) -> None:
    import importlib

    sync_mod = importlib.import_module(sync_path)
    async_mod = importlib.import_module("congressgov.services.async_api")
    async_cls = getattr(async_mod, async_name)
    assert hasattr(sync_mod, method) or any(
        hasattr(obj, method)
        for obj in sync_mod.__dict__.values()
        if isinstance(obj, type)
    )
    assert hasattr(async_cls, method)
