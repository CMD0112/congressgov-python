"""Hearing search must tolerate envelope JSON and resolve format_=None."""

import json
from unittest.mock import MagicMock, patch

import httpx

from congressgov._client.api.hearing.get_hearing import _parse_response
from congressgov._client.models.get_hearing_format import GetHearingFormat
from congressgov.client import Client
from congressgov.services.core.search import hearingsearch


def test_hearing_parse_response_accepts_envelope_dict() -> None:
    response = httpx.Response(
        200,
        json={"hearings": [], "pagination": {"count": 0}},
    )
    client = Client(base_url="https://api.congress.gov/v3")
    assert _parse_response(client=client, response=response) is None


def test_hearingsearch_resolves_format() -> None:
    envelope = json.dumps({"hearings": [], "pagination": {"count": 0}}).encode()
    with patch(
        "congressgov._client.api.hearing.hearing_list_sync",
        return_value=MagicMock(status_code=200, content=envelope),
    ) as list_sync:
        hearingsearch(
            None,
            client=MagicMock(),
            format_=None,
        )

    _, kwargs = list_sync.call_args
    assert kwargs["format_"] == GetHearingFormat.JSON
