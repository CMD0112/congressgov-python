"""CommitteeMeeting.get must raise APIError for not-found / error payloads."""

from unittest.mock import MagicMock, patch

import pytest

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.committee_meeting import CommitteeMeeting
from congressgov.services.core.api_response import extract_api_error_message
from congressgov.services.exceptions import APIError


def test_extract_api_error_message_from_top_level_error() -> None:
    payload = {"error": "No Meeting matches the given query."}
    env = ApiEnvelope.model_validate(payload)
    assert extract_api_error_message(payload, env) == "No Meeting matches the given query."


def test_extract_api_error_message_from_wrapped_string_value() -> None:
    payload = {"committeeMeeting": "No Meeting matches the given query."}
    env = ApiEnvelope.model_validate(payload)
    assert extract_api_error_message(payload, env) == "No Meeting matches the given query."


def test_committee_meeting_get_raises_api_error_on_404_body() -> None:
    body = b'{"error": "No Meeting matches the given query."}'
    mock_resp = MagicMock(status_code=404, content=body)

    with patch(
        "congressgov.services.committee_meeting.committee_meeting_detail_sync",
        return_value=mock_resp,
    ):
        service = CommitteeMeeting(client=MagicMock())
        with pytest.raises(APIError) as exc_info:
            service.get(congress=117, chamber="house", event_id="115538")

    assert "No Meeting matches" in str(exc_info.value)
    assert exc_info.value.details.get("status_code") == 404


def test_committee_meeting_get_raises_api_error_on_200_string_payload() -> None:
    """Some error shapes may return 200 with a string-like data payload."""
    body = b'{"committeeMeeting": "No Meeting matches the given query."}'
    mock_resp = MagicMock(status_code=200, content=body)

    with patch(
        "congressgov.services.committee_meeting.committee_meeting_detail_sync",
        return_value=mock_resp,
    ):
        service = CommitteeMeeting(client=MagicMock())
        with pytest.raises(APIError) as exc_info:
            service.get(congress=117, chamber="house", event_id="115538")

    assert "No Meeting matches" in str(exc_info.value)
    assert "event_id=115538" in str(exc_info.value)
