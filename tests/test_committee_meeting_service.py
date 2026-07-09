"""CommitteeMeeting adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "committee_meeting.py"


def test_hand_committee_meeting_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class CommitteeMeeting" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "validate_chamber" in src
    assert "committee_meeting_detail_sync" in src



def test_committee_meeting_search_delegates_to_universal_search() -> None:
    from congressgov.services.committee_meeting import CommitteeMeeting

    meetings = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=meetings) as mock_search:
        service = CommitteeMeeting()
        result = service.search(congress=118, chamber="house")

    assert result is meetings
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "committee-meeting"
    assert args[1] is service
    assert kwargs["congress"] == 118
    assert kwargs["chamber"] == "house"


def test_committee_meeting_get_validates_chamber() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.committee_meeting import CommitteeMeeting

    service = CommitteeMeeting(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=118, chamber="invalid", event_id="12345")
