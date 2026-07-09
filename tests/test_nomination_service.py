"""Nomination adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "nomination.py"


def test_hand_nomination_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Nomination" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "NOMINATION_MAPPINGS" in src
    assert "nomination_detail_sync" in src



def test_nomination_search_delegates_to_universal_search() -> None:
    from congressgov.services.nomination import Nomination

    nominations = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=nominations) as mock_search:
        service = Nomination()
        result = service.search(congress=118)

    assert result is nominations
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "nomination"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_nomination_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.nomination import Nomination

    service = Nomination(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=0, nomination_number=1)
