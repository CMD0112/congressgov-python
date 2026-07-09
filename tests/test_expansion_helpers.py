"""Tests for expansion helper utilities."""

from __future__ import annotations

from enum import Enum
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from congressgov.services.core.expansion_helpers import (
    expand_sync_instance,
    extract_parameters_from_target,
    normalize_param_value,
)


class SampleType(str, Enum):
    HR = "HR"


def test_normalize_param_value_lowercases_string() -> None:
    assert normalize_param_value("HR") == "hr"


def test_normalize_param_value_handles_enum() -> None:
    assert normalize_param_value(SampleType.HR) == "hr"


def test_extract_parameters_from_target_with_aliases() -> None:
    target = MagicMock()
    target.congress = 118
    target.type = "HR"
    target.number = 42
    del target.bill_type
    del target.bill_number

    params = extract_parameters_from_target(
        target,
        {
            "congress": "congress",
            "bill_type": ["bill_type", "type"],
            "bill_number": ["bill_number", "number"],
        },
        normalize_params=["bill_type"],
    )

    assert params == {"congress": 118, "bill_type": "hr", "bill_number": 42}


def test_extract_parameters_from_target_raises_when_missing() -> None:
    class Target:
        congress = 118
        type = None
        number = 1

    with pytest.raises(ValueError, match="Missing or empty"):
        extract_parameters_from_target(
            Target(),
            {"congress": "congress", "bill_type": ["bill_type", "type"]},
        )


def test_expand_sync_instance_sets_attribute() -> None:
    class ActionsModel(BaseModel):
        count: int

    class BillModel(BaseModel):
        congress: int
        type: str
        number: int
        actions: ActionsModel | None = None

    bill = BillModel(congress=118, type="hr", number=1)
    client = MagicMock()

    def fake_actions(*, client, congress, bill_type, bill_number, **kwargs):
        resp = MagicMock()
        resp.content = b'{"actions": {"count": 3}}'
        assert client is not None
        assert congress == 118
        assert bill_type == "hr"
        assert bill_number == 1
        return resp

    mapping = {"actions": {fake_actions: ActionsModel}}

    expanded = expand_sync_instance(
        bill,
        mapping=mapping,
        parameters={
            "congress": "congress",
            "bill_type": ["bill_type", "type"],
            "bill_number": ["bill_number", "number"],
        },
        client=client,
        attributes=["actions"],
        normalize_params=["bill_type"],
    )

    assert expanded is not bill
    assert expanded.actions is not None
    assert expanded.actions.count == 3
