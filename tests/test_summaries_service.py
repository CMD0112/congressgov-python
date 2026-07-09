"""Summaries adoption: hand service (search-only)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "summaries.py"


def test_hand_summaries_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Summaries" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "def search(" in src
    assert "def get(" not in src



def test_summaries_search_delegates_to_universal_search() -> None:
    from congressgov.services.summaries import Summaries

    summaries = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=summaries) as mock_search:
        service = Summaries()
        result = service.search(limit=10)

    assert result is summaries
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "summary"
    assert args[1] is service
    assert kwargs["limit"] == 10
