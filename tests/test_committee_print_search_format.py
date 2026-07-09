"""Committee print search must tolerate envelope JSON and resolve format_=None."""

import json
from unittest.mock import MagicMock, patch

import httpx

from congressgov._client.models.get_committee_print_congress_format import (
    GetCommitteePrintCongressFormat,
)
from congressgov._client.api.committee_print.get_committee_print_congress import (
    _parse_response,
)
from congressgov.client import Client
from congressgov.services.core.search import committeeprintsearch


def test_committee_print_congress_parse_response_accepts_envelope_dict() -> None:
    """Regression: iterating dict keys caused ValueError on committeePrints."""
    response = httpx.Response(
        200,
        json={"committeePrints": [], "pagination": {"count": 0}},
    )
    client = Client(base_url="https://api.congress.gov/v3")
    assert _parse_response(client=client, response=response) is None


def test_committeeprintsearch_by_congress_resolves_format() -> None:
    envelope = json.dumps(
        {"committeePrints": [], "pagination": {"count": 0}}
    ).encode()
    with patch(
        "congressgov._client.api.committee_print.committee_prints_by_congress_sync",
        return_value=MagicMock(status_code=200, content=envelope),
    ) as by_congress:
        committeeprintsearch(
            None,
            client=MagicMock(),
            congress=119,
            format_=None,
        )

    _, kwargs = by_congress.call_args
    assert kwargs["format_"] == GetCommitteePrintCongressFormat.JSON
