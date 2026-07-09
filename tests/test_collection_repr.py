"""Collection wrapper repr and list-like protocol registration."""

from __future__ import annotations

import pytest

import congressgov.services.extensions  # noqa: F401 — registers collection protocols

from congressgov.models.actions.action import Actions
from congressgov.models.communications.house_communication import HouseCommunications
from congressgov.models.entities.bill import Bills, Summaries
from congressgov.models.entities.congress import Congresses
from congressgov.models.entities.member import (
    CosponsoredLegislation,
    Members,
    SponsoredLegislation,
)
from congressgov.models.entities.sponsor import Cosponsors
from congressgov.services.extensions._collection_protocols import collection_repr


@pytest.mark.parametrize(
    "model_cls, payload, expected",
    [
        (Members, {"members": [{"bioguideId": "A1"}] * 2}, "<Members: 2 items>"),
        (Members, {"members": [{"bioguideId": "A1"}]}, "<Members: 1 item>"),
        (Members, {"members": []}, "<Members: 0 items>"),
        (Congresses, {"congresses": [{"number": 118}, {"number": 119}]}, "<Congresses: 2 items>"),
        (Bills, {"bills": [{"congress": 119, "type": "HR", "number": 1}]}, "<Bills: 1 item>"),
        (
            HouseCommunications,
            {"houseCommunications": [{"congress": 119, "number": "1"}]},
            "<HouseCommunications: 1 item>",
        ),
        (
            SponsoredLegislation,
            {"sponsoredLegislation": [{"congress": 119, "type": "HR", "number": "1"}]},
            "<SponsoredLegislation: 1 item>",
        ),
        (
            CosponsoredLegislation,
            {"cosponsoredLegislation": [{"congress": 119, "type": "S", "number": "2"}]},
            "<CosponsoredLegislation: 1 item>",
        ),
    ],
)
def test_list_collections_use_compact_repr(model_cls, payload, expected) -> None:
    instance = model_cls.model_validate(payload)
    assert repr(instance) == expected


@pytest.mark.parametrize(
    "model_cls,payload",
    [
        (
            Cosponsors,
            {
                "cosponsors": [
                    {
                        "bioguideId": "A000374",
                        "url": "https://api.congress.gov/v3/member/A000374",
                    }
                ]
            },
        ),
        (Actions, {"actions": [{"actionDate": "2024-01-01", "text": "Introduced"}]}),
        (Summaries, {"summaries": [{"actionDate": "2024-01-01", "text": "Summary"}]}),
    ],
)
def test_bill_subresource_envelopes_keep_model_repr(model_cls, payload) -> None:
    instance = model_cls.model_validate(payload)
    text = repr(instance)
    assert not text.startswith(f"<{model_cls.__name__}:")
    items_field = next(iter(payload))
    assert f"{items_field}=" in text


def test_collection_repr_helper_pluralization() -> None:
    assert collection_repr("Members", 0) == "<Members: 0 items>"
    assert collection_repr("Members", 1) == "<Members: 1 item>"
    assert collection_repr("Members", 20) == "<Members: 20 items>"
