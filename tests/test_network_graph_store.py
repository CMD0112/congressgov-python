"""Tests for persistent congress graph datasets."""

from __future__ import annotations

from pathlib import Path

from congressgov.models.entities.bill import Bill
from congressgov.models.entities.member import Member, Term, Terms
from congressgov.services.export.graph import (
    CongressGraphStore,
    GraphExploreConfig,
    build_graph_slice,
    sponsorship_events_from_bill,
)


def _sample_bill(*, number: int = 1, cosponsors: list[dict[str, object]] | None = None) -> Bill:
    payload: dict[str, object] = {
        "congress": 118,
        "number": number,
        "type": "HR",
        "title": f"Sample Bill {number}",
        "originChamber": "House",
        "introducedDate": "2023-01-09",
        "policyArea": {"name": "Health"},
        "sponsors": [
            {
                "bioguideId": "S001",
                "fullName": "Rep. Sponsor One",
                "party": "D",
                "state": "NJ",
                "district": 7,
                "url": "https://api.congress.gov/v3/member/S001",
            }
        ],
    }
    if cosponsors is not None:
        payload["cosponsors"] = cosponsors
    return Bill.model_validate(payload)


def _sample_cosponsors() -> list[dict[str, object]]:
    return [
        {
            "bioguideId": "C001",
            "fullName": "Rep. Cosponsor One",
            "party": "D",
            "state": "NJ",
            "sponsorshipDate": "2023-01-10",
            "isOriginalCosponsor": True,
            "url": "https://api.congress.gov/v3/member/C001",
        },
        {
            "bioguideId": "C002",
            "fullName": "Rep. Cosponsor Two",
            "party": "R",
            "state": "TX",
            "sponsorshipDate": "2023-02-01",
            "isOriginalCosponsor": False,
            "url": "https://api.congress.gov/v3/member/C002",
        },
    ]


def _sample_member(*, bioguide_id: str, party: str = "D", state: str = "NJ", district: str | None = "7") -> Member:
    return Member.model_validate(
        {
            "bioguideId": bioguide_id,
            "firstName": "Member",
            "lastName": bioguide_id,
            "partyName": party,
            "state": state,
            "district": district,
            "terms": Terms(
                item=[
                    Term(
                        congress=118,
                        chamber="House of Representatives",
                        stateCode=state,
                        partyCode=party,
                        district=district,
                    )
                ]
            ),
        }
    )


def test_store_seeds_full_member_roster() -> None:
    store = CongressGraphStore(":memory:", congress=118)
    added = store.seed_members(
        [
            _sample_member(bioguide_id="S001"),
            _sample_member(bioguide_id="C001"),
            _sample_member(bioguide_id="M999", party="R", state="TX", district="12"),
        ]
    )

    assert added == 3
    assert store.member_count == 3
    assert "M999" in store.members


def test_store_adds_bills_incrementally_with_deduplication(tmp_path: Path) -> None:
    store_path = tmp_path / "118-graph.json"
    store = CongressGraphStore.open(store_path, congress=118)
    store.seed_members([_sample_member(bioguide_id="S001"), _sample_member(bioguide_id="C001")])

    bill = _sample_bill(cosponsors=_sample_cosponsors())
    first = store.add_bill(bill)
    second = store.add_bill(bill)
    store.save()

    assert first.added is True
    assert first.event_count == 2
    assert second.added is False
    assert second.skipped_reason == "already_ingested"
    assert store.bill_count == 1
    assert store.event_count == 2

    reloaded = CongressGraphStore.load(store_path)
    assert reloaded.bill_count == 1
    assert reloaded.event_count == 2
    assert reloaded.member_count == 2


def test_build_slice_with_full_roster_includes_isolated_members() -> None:
    store = CongressGraphStore(":memory:", congress=118)
    store.seed_members(
        [
            _sample_member(bioguide_id="S001"),
            _sample_member(bioguide_id="C001"),
            _sample_member(bioguide_id="M999", party="R", state="TX", district="12"),
        ]
    )
    store.add_bill(_sample_bill(cosponsors=_sample_cosponsors()))

    graph = store.build_slice(
        GraphExploreConfig(congress=118, min_weight=1, max_edges=10, include_all_members=True)
    )

    node_ids = {node.id for node in graph.nodes}
    assert node_ids == {"C001", "C002", "M999", "S001"}
    assert graph.edges
    isolated = next(node for node in graph.nodes if node.id == "M999")
    assert isolated.weighted_in_degree == 0.0
    assert isolated.weighted_out_degree == 0.0


def test_include_all_members_flag_on_builder() -> None:
    from congressgov.services.export.graph.member_labels import member_to_graph_node

    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    registry = {
        "S001": member_to_graph_node(_sample_member(bioguide_id="S001"), congress=118),
        "C001": member_to_graph_node(_sample_member(bioguide_id="C001"), congress=118),
        "M999": member_to_graph_node(
            _sample_member(bioguide_id="M999", party="R", state="TX", district="12"),
            congress=118,
        ),
    }
    graph = build_graph_slice(
        events,
        GraphExploreConfig(congress=118, min_weight=1, max_edges=10, include_all_members=True),
        member_registry=registry,
    )

    assert {node.id for node in graph.nodes} == {"C001", "C002", "M999", "S001"}


def test_build_slice_resolves_isolated_roster_labels() -> None:
    from congressgov.services.export.graph.member_labels import (
        MemberLabelResolver,
        member_to_graph_node,
    )

    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    isolated = member_to_graph_node(_sample_member(bioguide_id="M999", party="R", state="TX", district="12"), congress=118)
    assert isolated is not None
    isolated.label = "M999"
    registry = {
        "S001": member_to_graph_node(_sample_member(bioguide_id="S001"), congress=118),
        "M999": isolated,
    }

    class StubMemberService:
        def get(self, *, bioguide_id: str, client=None):
            return _sample_member(bioguide_id=bioguide_id, party="R", state="TX", district="12")

    resolver = MemberLabelResolver(StubMemberService(), congress=118)
    graph = build_graph_slice(
        events,
        GraphExploreConfig(congress=118, min_weight=1, max_edges=10, include_all_members=True),
        member_registry=registry,
        member_resolver=resolver,
    )
    labels = {node.id: node.label for node in graph.nodes}
    assert labels["M999"] == "Rep. M999, Member [R-TX-12]"


def test_store_resolve_member_labels_persists_canonical_names(tmp_path: Path) -> None:
    from congressgov.services.export.graph.member_labels import MemberLabelResolver, member_to_graph_node

    store_path = tmp_path / "118-graph.json"
    store = CongressGraphStore.open(store_path, congress=118)
    sparse = member_to_graph_node(_sample_member(bioguide_id="M999", party="R", state="TX", district="12"), congress=118)
    assert sparse is not None
    sparse.label = "M999"
    store._snapshot.members["M999"] = sparse

    class StubMemberService:
        def get(self, *, bioguide_id: str, client=None):
            return _sample_member(bioguide_id=bioguide_id, party="R", state="TX", district="12")

    resolver = MemberLabelResolver(StubMemberService(), congress=118)
    updated = store.resolve_member_labels(resolver, save=True)
    assert updated == 1
    assert store.members["M999"].label == "Rep. M999, Member [R-TX-12]"

    reloaded = CongressGraphStore.load(store_path)
    assert reloaded.members["M999"].label == "Rep. M999, Member [R-TX-12]"
