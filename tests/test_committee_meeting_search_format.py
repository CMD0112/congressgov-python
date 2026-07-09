"""Committee meeting search/get must resolve format_=None and chamber enums."""

from unittest.mock import MagicMock, patch

from congressgov._client.models.get_committee_meeting_congress_chamber_chamber import (
    GetCommitteeMeetingCongressChamberChamber,
)
from congressgov._client.models.get_committee_meeting_congress_chamber_format import (
    GetCommitteeMeetingCongressChamberFormat,
)
from congressgov._client.models.get_committee_meeting_congress_chamber_event_id_format import (
    GetCommitteeMeetingCongressChamberEventIdFormat,
)
from congressgov.services.core.search import committeemeetingsearch


def test_committeemeetingsearch_by_congress_chamber_resolves_params() -> None:
    with patch(
        "congressgov._client.api.committee_meeting.committee_meeting_congress_chamber_sync",
        return_value=MagicMock(
            status_code=200,
            content=b'{"committeeMeetings": [], "pagination": {"count": 0}}',
        ),
    ) as list_by_chamber:
        committeemeetingsearch(
            None,
            client=MagicMock(),
            congress=117,
            chamber="house",
            format_=None,
        )

    _, kwargs = list_by_chamber.call_args
    assert kwargs["format_"] == GetCommitteeMeetingCongressChamberFormat.JSON
    assert kwargs["chamber"] == GetCommitteeMeetingCongressChamberChamber.HOUSE


def test_committee_meeting_detail_get_kwargs_coerces_none_format() -> None:
    from congressgov._client.api.committee_meeting.get_committee_meeting_congress_chamber_event_id import (
        GetCommitteeMeetingCongressChamberEventIdChamber,
        _get_kwargs,
    )

    kwargs = _get_kwargs(
        congress=117,
        chamber=GetCommitteeMeetingCongressChamberEventIdChamber.HOUSE,
        event_id="115538",
        format_=None,
    )
    assert kwargs["params"]["format"] == GetCommitteeMeetingCongressChamberEventIdFormat.JSON.value
