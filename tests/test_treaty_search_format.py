"""Treaty list endpoints must not eager-parse envelope JSON in the generated client."""

import json
from unittest.mock import MagicMock, patch

import httpx

from congressgov._client.api.treaty.get_treaty import _parse_response
from congressgov._client.models.get_treaty_format import GetTreatyFormat
from congressgov.client import Client
from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.search import treatysearch


def test_treaty_parse_response_skips_eager_from_dict() -> None:
    response = httpx.Response(
        200,
        json={"treaties": [], "pagination": {"count": 0}},
    )
    client = Client(base_url="https://api.congress.gov/v3")
    assert _parse_response(client=client, response=response) is None


def test_treatysearch_resolves_format() -> None:
    envelope = json.dumps(
        {
            "treaties": [
                {
                    "congress": 117,
                    "number": 1,
                    "transmittedDate": None,
                    "suffix": "A",
                }
            ],
            "pagination": {"count": 1},
        }
    ).encode()
    with patch(
        "congressgov._client.api.treaty.treaty_list_sync",
        return_value=MagicMock(status_code=200, content=envelope),
    ) as list_sync:
        treatysearch(
            None,
            client=MagicMock(),
            format_=None,
        )

    _, kwargs = list_sync.call_args
    assert kwargs["format_"] == GetTreatyFormat.JSON


def test_treaty_item_null_transmitted_date_in_envelope() -> None:
    payload = {
        "treaties": [{"congress": 117, "number": 1, "transmittedDate": None}],
        "pagination": {"count": 1},
    }
    env = ApiEnvelope.model_validate(payload)
    assert env.data is not None
