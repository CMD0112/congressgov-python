"""CongressionalRecord adoption: hand service (search-only)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "congressional_record.py"


def test_hand_congressional_record_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class CongressionalRecord" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "def search(" in src
    assert "def get(" not in src



def test_congressional_record_search_delegates_to_universal_search() -> None:
    from congressgov.services.congressional_record import CongressionalRecord

    records = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=records) as mock_search:
        service = CongressionalRecord()
        result = service.search(year=2024, month=1)

    assert result is records
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "congressional-record"
    assert kwargs["year"] == 2024
    assert kwargs["month"] == 1
