"""SenateCommunication adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "senate_communication.py"


def test_hand_senate_communication_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class SenateCommunication" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "senate_communication_detail_sync" in src



def test_senate_communication_search_delegates_to_universal_search() -> None:
    from congressgov.services.senate_communication import SenateCommunication

    communications = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=communications) as mock_search:
        service = SenateCommunication()
        result = service.search(congress=118)

    assert result is communications
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "senate-communication"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_senate_communication_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.senate_communication import SenateCommunication

    service = SenateCommunication(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(
            congress=0,
            communication_type="ec",
            communication_number=1,
        )
