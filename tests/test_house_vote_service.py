"""HouseVote middleware adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "house_vote.py"


def test_hand_house_vote_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class HouseVote" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_congress" in src
    assert "house_vote_details_sync" in src


def test_house_vote_search_delegates_to_universal_search() -> None:
    from congressgov.services.house_vote import HouseVote

    house_votes = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=house_votes) as mock_search:
        service = HouseVote()
        result = service.search(congress=118)

    assert result is house_votes
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "house-vote"
    assert args[1] is service
    assert kwargs["congress"] == 118


def test_hand_house_vote_has_members_method() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "# CUSTOM: members sub-endpoint" in src
    assert "def members(" in src
    assert "house_vote_members_detailed" in src


def test_house_vote_members_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.house_vote import HouseVote

    service = HouseVote(client=MagicMock())
    with pytest.raises(ValidationError):
        service.members(congress=0, session=1, vote_number=1)


def test_house_vote_get_validates_congress() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.house_vote import HouseVote

    service = HouseVote(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=0, session=1, vote_number=1)


def test_house_votes_extension_registers_query_helpers() -> None:
    from congressgov.models.communications.house_vote import HouseVotes
    from congressgov.services.extensions._registry import get_registered_methods, get_registered_models

    assert "HouseVotes" in get_registered_models()
    registered = get_registered_methods("HouseVotes")
    assert "filter" in registered
    assert "query" in registered
    assert hasattr(HouseVotes, "filter")
    assert hasattr(HouseVotes, "__iter__")
