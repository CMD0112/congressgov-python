"""BoundCongressionalRecord adoption: hand service (search-only)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "bound_congressional_record.py"


def test_hand_bound_congressional_record_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class BoundCongressionalRecord" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "def search(" in src
    assert "def get(" not in src



def test_bound_congressional_record_search_delegates_to_universal_search() -> None:
    from congressgov.services.bound_congressional_record import BoundCongressionalRecord

    records = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=records) as mock_search:
        service = BoundCongressionalRecord()
        result = service.search(year=2020)

    assert result is records
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "bound-congressional-record"
    assert kwargs["year"] == 2020
