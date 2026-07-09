"""Tests for congressional member display label formatting."""

from __future__ import annotations

from congressgov.services.export.graph.member_labels import format_congress_member_label


def test_preserves_api_canonical_house_label() -> None:
    label = format_congress_member_label(
        bioguide_id="M001",
        full_name="Rep. Maloney, Carolyn B. [D-NY-12]",
        party="D",
        state="NY",
        district=12,
    )
    assert label == "Rep. Maloney, Carolyn B. [D-NY-12]"


def test_preserves_api_canonical_senate_label() -> None:
    label = format_congress_member_label(
        bioguide_id="P000",
        full_name="Sen. Portman, Rob [R-OH]",
        party="R",
        state="OH",
    )
    assert label == "Sen. Portman, Rob [R-OH]"


def test_builds_label_from_name_parts_and_metadata() -> None:
    label = format_congress_member_label(
        bioguide_id="S001",
        full_name="Rep. Sponsor One",
        party="D",
        state="NJ",
        district=7,
        origin_chamber="house",
    )
    assert label == "Rep. One, Sponsor [D-NJ-7]"


def test_builds_senate_label_without_district() -> None:
    label = format_congress_member_label(
        bioguide_id="S010",
        full_name="Sen. Ten",
        party="D",
        state="DE",
        origin_chamber="senate",
    )
    assert label == "Sen. Ten [D-DE]"


def test_uses_first_and_last_name_fields() -> None:
    label = format_congress_member_label(
        bioguide_id="C001",
        first_name="Gerald E.",
        last_name="Connolly",
        party="D",
        state="VA",
        district=11,
        origin_chamber="house",
    )
    assert label == "Rep. Connolly, Gerald E. [D-VA-11]"


def test_normalizes_party_aliases() -> None:
    label = format_congress_member_label(
        bioguide_id="X001",
        first_name="Alex",
        last_name="Indie",
        party="Independent",
        state="VT",
        origin_chamber="senate",
    )
    assert label == "Sen. Indie, Alex [I-VT]"


def test_member_to_graph_node_uses_member_record() -> None:
    from congressgov.models.entities.member import Member, Term, Terms

    from congressgov.services.export.graph.member_labels import member_to_graph_node

    member = Member.model_validate(
        {
            "bioguideId": "M001",
            "firstName": "Carolyn B.",
            "lastName": "Maloney",
            "partyName": "Democratic",
            "state": "NY",
            "district": 12,
            "terms": Terms(
                item=[
                    Term(
                        congress=118,
                        chamber="House of Representatives",
                        stateCode="NY",
                        partyCode="D",
                        district="12",
                    )
                ]
            ),
        }
    )
    node = member_to_graph_node(member, congress=118)
    assert node is not None
    assert node.label == "Rep. Maloney, Carolyn B. [D-NY-12]"


def test_member_label_resolver_enriches_sparse_event_nodes() -> None:
    from congressgov.services.export.graph import GraphExploreConfig, build_graph_slice, sponsorship_events_from_bill
    from congressgov.services.export.graph.member_labels import MemberLabelResolver
    from congressgov.models.entities.bill import Bill
    from congressgov.models.entities.member import Member, Term, Terms

    bill = Bill.model_validate(
        {
            "congress": 118,
            "number": 1,
            "type": "HR",
            "title": "Sample",
            "originChamber": "House",
            "sponsors": [
                {
                    "bioguideId": "M001",
                    "fullName": "Rep. Maloney",
                    "url": "https://api.congress.gov/v3/member/M001",
                }
            ],
            "cosponsors": [
                {
                    "bioguideId": "M002",
                    "fullName": "Rep. Foxx",
                    "url": "https://api.congress.gov/v3/member/M002",
                }
            ],
        }
    )
    events = sponsorship_events_from_bill(bill)

    class StubMemberService:
        def get(self, *, bioguide_id: str, client=None):
            if bioguide_id == "M001":
                return Member.model_validate(
                    {
                        "bioguideId": "M001",
                        "firstName": "Carolyn B.",
                        "lastName": "Maloney",
                        "terms": Terms(
                            item=[
                                Term(
                                    congress=118,
                                    chamber="House of Representatives",
                                    stateCode="NY",
                                    partyCode="D",
                                    district="12",
                                )
                            ]
                        ),
                    }
                )
            return Member.model_validate(
                {
                    "bioguideId": "M002",
                    "firstName": "Virginia",
                    "lastName": "Foxx",
                    "terms": Terms(
                        item=[
                            Term(
                                congress=118,
                                chamber="House of Representatives",
                                stateCode="NC",
                                partyCode="R",
                                district="5",
                            )
                        ]
                    ),
                }
            )

    resolver = MemberLabelResolver(StubMemberService(), congress=118)
    graph = build_graph_slice(
        events,
        GraphExploreConfig(congress=118, min_weight=1, max_edges=10),
        member_resolver=resolver,
    )
    labels = {node.id: node.label for node in graph.nodes}
    assert labels["M001"] == "Rep. Maloney, Carolyn B. [D-NY-12]"
    assert labels["M002"] == "Rep. Foxx, Virginia [R-NC-5]"
    assert resolver.resolve_node("M001") is not None
