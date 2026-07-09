"""HouseRequirement adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "house_requirement.py"


def test_hand_house_requirement_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class HouseRequirement" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "house_requirement_detail_sync" in src



def test_house_requirement_search_delegates_to_universal_search() -> None:
    from congressgov.services.house_requirement import HouseRequirement

    requirements = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=requirements) as mock_search:
        service = HouseRequirement()
        result = service.search(limit=5)

    assert result is requirements
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "house-requirement"
    assert kwargs["limit"] == 5
