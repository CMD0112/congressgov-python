"""Hearing adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "hearing.py"


def test_hand_hearing_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Hearing" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "validate_chamber" in src
    assert "hearing_detail_sync" in src



def test_hearing_search_delegates_to_universal_search() -> None:
    from congressgov.services.hearing import Hearing

    hearings = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=hearings) as mock_search:
        service = Hearing()
        result = service.search(congress=118, chamber="house")

    assert result is hearings
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "hearing"
    assert args[1] is service
    assert kwargs["congress"] == 118
    assert kwargs["chamber"] == "house"


def test_hearing_get_validates_chamber() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.hearing import Hearing

    service = Hearing(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=118, chamber="invalid", jacket_number=1)
