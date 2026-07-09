"""House vote search must accept non-enum result strings from the API."""

from congressgov.models.communications.house_vote import HouseVote, HouseVotes


def test_house_vote_accepts_speaker_election_result() -> None:
    vote = HouseVote.model_validate(
        {
            "congress": 119,
            "rollCallNumber": 1,
            "result": "Elected Speaker Name",
        }
    )
    assert vote.result == "Elected Speaker Name"


def test_house_votes_collection_with_non_enum_result() -> None:
    model = HouseVotes.model_validate(
        {
            "houseRollCallVotes": [
                {"congress": 119, "rollCallNumber": 1, "result": "Passed"},
                {"congress": 119, "rollCallNumber": 2, "result": "Elected Speaker Name"},
            ]
        }
    )
    assert len(model.houseRollCallVotes or []) == 2
    assert model.houseRollCallVotes[1].result == "Elected Speaker Name"
