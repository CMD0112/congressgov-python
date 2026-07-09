"""Congress adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "congress.py"


def test_hand_congress_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Congress" in src
    assert "# CUSTOM: current session method" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: direct list search" in src
    assert "congress_current_list_sync" in src
    assert "congress_details_sync" in src
    assert "congress_list_sync" in src
    assert "resolve_response_format" in src



def test_congress_search_does_not_use_universal_search() -> None:
    from congressgov.services.congress import Congress

    congresses = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=congresses) as mock_search:
        with patch(
            "congressgov.services.congress.congress_list_sync",
            return_value=MagicMock(content=b'{"data": {"congresses": []}}'),
        ):
            service = Congress(client=MagicMock())
            service.search()

    mock_search.assert_not_called()


def test_congress_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.congress import Congress

    service = Congress(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=0)
