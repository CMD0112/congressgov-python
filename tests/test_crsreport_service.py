"""CRSReport adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "crsreport.py"


def test_hand_crsreport_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class CRSReport" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "crsreport_details_sync" in src
    assert "def get(" in src



def test_crsreport_search_delegates_to_universal_search() -> None:
    from congressgov.services.crsreport import CRSReport

    reports = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=reports) as mock_search:
        service = CRSReport()
        result = service.search(limit=5)

    assert result is reports
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "crs-report"
    assert args[1] is service
    assert kwargs["limit"] == 5
