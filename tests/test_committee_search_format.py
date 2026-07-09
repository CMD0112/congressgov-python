"""Committee service must not pass format_=None into the generated client."""

from unittest.mock import MagicMock, patch

from congressgov._client.models.get_committee_chamber_chamber import GetCommitteeChamberChamber
from congressgov._client.models.get_committee_chamber_committee_code_chamber import (
    GetCommitteeChamberCommitteeCodeChamber,
)
from congressgov._client.models.get_committee_chamber_committee_code_format import (
    GetCommitteeChamberCommitteeCodeFormat,
)
from congressgov._client.models.get_committee_chamber_format import GetCommitteeChamberFormat
from congressgov.services.committee import Committee
from congressgov.services.core.search import committeesearch


def test_committeesearch_by_chamber_resolves_format_and_chamber() -> None:
    with patch(
        "congressgov._client.api.committee.committee_list_by_chamber_sync",
        return_value=MagicMock(content=b'{"data": {"committees": []}}'),
    ) as list_by_chamber:
        committeesearch(None, client=MagicMock(), chamber="house", format_=None)

    list_by_chamber.assert_called_once()
    _, kwargs = list_by_chamber.call_args
    assert kwargs["format_"] == GetCommitteeChamberFormat.JSON
    assert kwargs["chamber"] == GetCommitteeChamberChamber.HOUSE


def test_committee_get_resolves_format_and_chamber() -> None:
    with patch(
        "congressgov.services.committee.committee_details_sync",
        return_value=MagicMock(content=b'{"data": {"systemCode": "HSGOV"}}'),
    ) as details:
        Committee(client=MagicMock()).get(chamber="house", committee_code="HSGOV")

    _, kwargs = details.call_args
    assert kwargs["format_"] == GetCommitteeChamberCommitteeCodeFormat.JSON
    assert kwargs["chamber"] == GetCommitteeChamberCommitteeCodeChamber.HOUSE
