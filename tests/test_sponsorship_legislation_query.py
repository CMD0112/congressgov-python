"""SponsoredLegislation / CosponsoredLegislation query helpers."""

from __future__ import annotations

import congressgov.services.extensions  # noqa: F401

from congressgov.models.entities.member import (
    CosponsoredLegislation,
    CosponsoredLegislationItem,
    SponsoredLegislation,
    SponsoredLegislationItem,
)


def test_cosponsored_legislation_query_to_list() -> None:
    cosp = CosponsoredLegislation(
        cosponsoredLegislation=[
            CosponsoredLegislationItem(type="HR", congress=118, number="1"),
            CosponsoredLegislationItem(type="S", congress=118, number="2"),
        ]
    )
    assert hasattr(cosp, "query")
    hr_only = cosp.filter(type="HR")
    assert len(hr_only) == 1
    assert cosp.query().to_list() == list(cosp)


def test_sponsored_legislation_query_to_list() -> None:
    sp = SponsoredLegislation(
        sponsoredLegislation=[
            SponsoredLegislationItem(type="HR", congress=118, number="10"),
        ]
    )
    assert sp.query().to_list()[0].number == "10"
