"""Summaries search must tolerate envelope JSON."""

import httpx

from congressgov._client.api.summaries.get_summaries import _parse_response
from congressgov.client import Client


def test_summaries_parse_response_accepts_envelope_dict() -> None:
    response = httpx.Response(
        200,
        json={"summaries": [], "pagination": {"count": 0}},
    )
    client = Client(base_url="https://api.congress.gov/v3")
    assert _parse_response(client=client, response=response) is None
