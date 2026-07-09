"""Treaty adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "treaty.py"


def test_hand_treaty_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Treaty" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "TREATY_MAPPINGS" in src
    assert "treaty_detail_sync" in src



def test_treaty_search_delegates_to_universal_search() -> None:
    from congressgov.services.treaty import Treaty

    treaties = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=treaties) as mock_search:
        service = Treaty()
        result = service.search(congress=118)

    assert result is treaties
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "treaty"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_treaty_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.treaty import Treaty

    service = Treaty(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=0, treaty_number=1)
