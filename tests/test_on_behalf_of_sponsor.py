"""Bill and Amendment accept onBehalfOfSponsor as object or list."""

from __future__ import annotations

from congressgov.models.entities.amendment import Amendment
from congressgov.models.entities.bill import Bill

_ON_BEHALF_PERSON = {
    "bioguideId": "B001288",
    "fullName": "Christopher A. Coons",
    "firstName": "Christopher",
    "lastName": "Coons",
    "party": "D",
    "state": "DE",
    "type": "Submitted on behalf of",
}


def test_amendment_on_behalf_of_sponsor_single_object() -> None:
    amendment = Amendment.model_validate(
        {
            "congress": 119,
            "number": "5321",
            "type": "SAMDT",
            "onBehalfOfSponsor": _ON_BEHALF_PERSON,
        }
    )

    assert amendment.onBehalfOfSponsor is not None
    assert not isinstance(amendment.onBehalfOfSponsor, list)
    assert amendment.onBehalfOfSponsor.bioguideId == "B001288"


def test_amendment_on_behalf_of_sponsor_list() -> None:
    amendment = Amendment.model_validate(
        {
            "congress": 119,
            "number": "5321",
            "type": "SAMDT",
            "onBehalfOfSponsor": [_ON_BEHALF_PERSON],
        }
    )

    assert isinstance(amendment.onBehalfOfSponsor, list)
    assert len(amendment.onBehalfOfSponsor) == 1
    assert amendment.onBehalfOfSponsor[0].bioguideId == "B001288"


def test_amendment_on_behalf_of_sponsor_multiple() -> None:
    second = {
        **_ON_BEHALF_PERSON,
        "bioguideId": "C000141",
        "fullName": "Ben Cardin",
    }
    amendment = Amendment.model_validate(
        {
            "congress": 119,
            "number": "5321",
            "type": "SAMDT",
            "onBehalfOfSponsor": [_ON_BEHALF_PERSON, second],
        }
    )

    assert isinstance(amendment.onBehalfOfSponsor, list)
    assert len(amendment.onBehalfOfSponsor) == 2
    ids = {p.bioguideId for p in amendment.onBehalfOfSponsor}
    assert ids == {"B001288", "C000141"}


def test_bill_on_behalf_of_sponsor_single_object() -> None:
    bill = Bill.model_validate(
        {
            "congress": 119,
            "number": 100,
            "type": "SRES",
            "onBehalfOfSponsor": _ON_BEHALF_PERSON,
        }
    )

    assert bill.onBehalfOfSponsor is not None
    assert not isinstance(bill.onBehalfOfSponsor, list)
    assert bill.onBehalfOfSponsor.bioguideId == "B001288"


def test_bill_on_behalf_of_sponsor_list() -> None:
    bill = Bill.model_validate(
        {
            "congress": 119,
            "number": 100,
            "type": "SRES",
            "onBehalfOfSponsor": [_ON_BEHALF_PERSON],
        }
    )

    assert isinstance(bill.onBehalfOfSponsor, list)
    assert len(bill.onBehalfOfSponsor) == 1
    assert bill.onBehalfOfSponsor[0].bioguideId == "B001288"
