"""CommitteeReport adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "committee_report.py"


def test_hand_committee_report_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class CommitteeReport" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "committee_report_details_sync" in src



def test_committee_report_search_delegates_to_universal_search() -> None:
    from congressgov.services.committee_report import CommitteeReport

    reports = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=reports) as mock_search:
        service = CommitteeReport()
        result = service.search(congress=118)

    assert result is reports
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "committee-report"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_committee_report_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.committee_report import CommitteeReport

    service = CommitteeReport(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=0, report_type="hrpt", report_number=1)
