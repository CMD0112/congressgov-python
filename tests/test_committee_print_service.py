"""CommitteePrint adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "committee_print.py"


def test_hand_committee_print_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class CommitteePrint" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "validate_chamber" in src
    assert "committee_print_detail_sync" in src



def test_committee_print_search_delegates_to_universal_search() -> None:
    from congressgov.services.committee_print import CommitteePrint

    prints = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=prints) as mock_search:
        service = CommitteePrint()
        result = service.search(congress=118)

    assert result is prints
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "committee-print"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_committee_print_get_validates_chamber() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.committee_print import CommitteePrint

    service = CommitteePrint(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=118, jacket_number=1, chamber="invalid")
