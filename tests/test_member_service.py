"""Member adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "member.py"


def test_hand_member_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Member" in src
    assert "# CUSTOM: validation" in src
    assert "_fetch_members" in src
    assert "# CUSTOM: current roster helper" in src
    assert "validate_bioguide_id" in src
    assert "get_current_roster" in src
    assert "member_details_sync" in src



def test_member_search_uses_member_list_by_state() -> None:
    from congressgov.services.member import Member

    members = MagicMock()
    with patch.object(Member, "_fetch_members", return_value=members) as mock_fetch:
        service = Member()
        result = service.search(state="CA", current_member="true")

    assert result is members
    mock_fetch.assert_called_once_with(
        client=None,
        congress=None,
        state="CA",
        district=None,
        format_=None,
        offset=None,
        limit=None,
        from_date_time=None,
        to_date_time=None,
        current_member="true",
    )


def test_get_current_roster_does_not_import_core_search() -> None:
    from congressgov.models.entities.member import Member as MemberModel, Members as MembersModel
    from congressgov.services.member import Member

    house = MemberModel.model_validate(
        {
            "terms": {
                "item": [{"chamber": "House of Representatives", "startYear": 2023}]
            }
        }
    )
    senate = MemberModel.model_validate(
        {"terms": {"item": [{"chamber": "Senate", "startYear": 2023}]}}
    )
    page = MembersModel.model_validate({"members": [house, senate]})

    service = Member(client=MagicMock())
    with patch.object(Member, "_fetch_members", return_value=page):
        roster = service.get_current_roster()

    assert "house_members" in roster
    assert "senate_members" in roster
    assert len(roster["house_members"].members) == 1
    assert len(roster["senate_members"].members) == 1


def test_member_get_validates_bioguide_id() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.member import Member

    service = Member(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(bioguide_id="")
