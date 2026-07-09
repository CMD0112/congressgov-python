"""Amendment adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "amendment.py"


def test_hand_amendment_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Amendment" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_amendment_type" in src
    assert "AMENDMENT_MAPPINGS" in src
    assert "amendment_details_sync" in src



def test_amendment_search_delegates_to_universal_search() -> None:
    from congressgov.services.amendment import Amendment

    amendments = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=amendments) as mock_search:
        service = Amendment()
        result = service.search(congress=118, amendment_type="hamdt")

    assert result is amendments
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "amendment"
    assert args[1] is service
    assert kwargs["congress"] == 118
    assert kwargs["amendment_type"] == "hamdt"


def test_amendment_get_validates_amendment_type() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.amendment import Amendment

    service = Amendment(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=118, amendment_type="invalid", amendment_number="1")
