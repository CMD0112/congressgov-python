"""Bill amendments extension behavior."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import congressgov.services.extensions.bill  # noqa: F401

from congressgov.models.entities.amendment import Amendment
from congressgov.models.entities.bill import Bill
from congressgov.services.core.model_registry import ModelRegistry


def _response(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.content = json.dumps(payload).encode()
    return resp


def test_get_amendments_assigns_list_on_bill() -> None:
    bill = Bill.model_validate({"congress": 118, "type": "HR", "number": 1})
    bill.client = MagicMock()
    payload = {
        "amendments": [
            {"congress": 118, "type": "HAMDT", "number": "100"},
            {"congress": 118, "type": "HAMDT", "number": "101"},
        ]
    }
    with patch(
        "congressgov.services.extensions.bill.bill_amendments_sync",
        return_value=_response(payload),
    ):
        result = bill.get_amendments()

    assert result is bill.amendments
    assert len(result) == 2
    assert all(isinstance(item, Amendment) for item in result)


def test_expand_amendments_unwraps_to_list() -> None:
    from congressgov.services.bill import BILL_MAPPINGS

    bill = Bill.model_validate({"congress": 118, "type": "HR", "number": 1})
    payload = {
        "amendments": [{"congress": 118, "type": "HAMDT", "number": "50"}],
    }
    response = _response(payload)
    fake_api = MagicMock(return_value=response)
    AmendmentsModel = ModelRegistry.get_model("Amendments")

    with patch.dict(BILL_MAPPINGS, {"amendments": {fake_api: AmendmentsModel}}):
        expanded = bill.expand(client=MagicMock(), attributes=["amendments"])

    assert expanded is not bill
    assert isinstance(expanded.amendments, list)
    assert len(expanded.amendments) == 1
    assert isinstance(expanded.amendments[0], Amendment)
