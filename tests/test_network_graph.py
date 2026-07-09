"""Tests for sponsor/cosponsor network graph projections."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from congressgov.models.entities.bill import Bill
from congressgov.services.export.graph import (
    EgoNetworkConfig,
    GraphChamberFilter,
    GraphExploreConfig,
    build_ego_graph,
    build_graph_slice,
    build_member_summary,
    build_projection_key,
    export_graph_slice_json,
    get_edge_evidence,
    graph_slice_to_sigma_payload,
    rank_relationships,
    sponsorship_events_from_bill,
)


def _sample_bill(*, cosponsors: list[dict[str, object]] | None = None) -> Bill:
    payload: dict[str, object] = {
        "congress": 118,
        "number": 1,
        "type": "HR",
        "title": "Sample Health Bill",
        "originChamber": "House",
        "introducedDate": "2023-01-09",
        "policyArea": {"name": "Health"},
        "latestAction": {"actionDate": "2023-03-01", "text": "Referred to committee"},
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


def test_sponsorship_events_from_bill_creates_one_row_per_pair() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))

    assert len(events) == 2
    assert events[0].bill_id == "118-hr-1"
    assert events[0].policy_area == "Health"
    assert events[0].sponsor_bioguide_id == "S001"
    assert {event.cosponsor_bioguide_id for event in events} == {"C001", "C002"}


def test_withdrawn_cosponsors_are_marked_inactive() -> None:
    bill = _sample_bill(
        cosponsors=[
            {
                "bioguideId": "C003",
                "fullName": "Rep. Withdrawn",
                "party": "D",
                "state": "CA",
                "sponsorshipWithdrawnDate": "2023-04-01",
                "url": "https://api.congress.gov/v3/member/C003",
            }
        ]
    )
    events = sponsorship_events_from_bill(bill)

    assert len(events) == 1
    assert events[0].is_active is False
    assert events[0].sponsorship_withdrawn_date == date(2023, 4, 1)


def test_build_graph_slice_aggregates_and_filters_by_min_weight() -> None:
    bill_one = _sample_bill(cosponsors=_sample_cosponsors())
    bill_two = Bill.model_validate(
        {
            "congress": 118,
            "number": 2,
            "type": "HR",
            "title": "Second bill",
            "originChamber": "House",
            "policyArea": {"name": "Health"},
            "sponsors": [
                {
                    "bioguideId": "S001",
                    "fullName": "Rep. Sponsor One",
                    "party": "D",
                    "state": "NJ",
                    "url": "https://api.congress.gov/v3/member/S001",
                }
            ],
            "cosponsors": [
                {
                    "bioguideId": "C001",
                    "fullName": "Rep. Cosponsor One",
                    "party": "D",
                    "state": "NJ",
                    "url": "https://api.congress.gov/v3/member/C001",
                }
            ],
        }
    )
    events = sponsorship_events_from_bill(bill_one) + sponsorship_events_from_bill(bill_two)
    config = GraphExploreConfig(congress=118, min_weight=2, max_edges=10)
    graph = build_graph_slice(events, config)

    assert len(graph.edges) == 1
    assert graph.edges[0].source == "S001"
    assert graph.edges[0].target == "C001"
    assert graph.edges[0].weight == 2
    assert graph.limits.was_truncated is False


def test_exclude_withdrawn_by_default() -> None:
    active = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    withdrawn_bill = _sample_bill(
        cosponsors=[
            {
                "bioguideId": "C004",
                "fullName": "Rep. Gone",
                "party": "D",
                "state": "NY",
                "sponsorshipWithdrawnDate": "2023-05-01",
                "url": "https://api.congress.gov/v3/member/C004",
            }
        ]
    )
    withdrawn = sponsorship_events_from_bill(withdrawn_bill)
    config = GraphExploreConfig(congress=118, min_weight=1, max_edges=10)
    graph = build_graph_slice(active + withdrawn, config)

    edge_targets = {edge.target for edge in graph.edges}
    assert "C004" not in edge_targets


def test_cross_party_only_filter() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    config = GraphExploreConfig(congress=118, cross_party_only=True, min_weight=1, max_edges=10)
    graph = build_graph_slice(events, config)

    assert len(graph.edges) == 1
    assert graph.edges[0].target == "C002"


def test_get_edge_evidence_returns_bill_audit_trail() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    config = GraphExploreConfig(congress=118)
    evidence = get_edge_evidence(events, "S001", "C001", config)

    assert evidence.weight == 1
    assert evidence.original_count == 1
    assert evidence.cross_party is False
    assert len(evidence.bills) == 1
    assert evidence.bills[0].bill_id == "118-hr-1"


def test_build_member_summary_counts_sponsor_and_cosponsor_roles() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    summary = build_member_summary(events, "S001", GraphExploreConfig(congress=118))

    assert summary.sponsored_bill_count == 1
    assert summary.cosponsored_bill_count == 0
    assert len(summary.top_outgoing) == 2


def test_build_ego_graph_limits_to_selected_member_neighborhood() -> None:
    bill = Bill.model_validate(
        {
            "congress": 118,
            "number": 3,
            "type": "HR",
            "originChamber": "House",
            "sponsors": [
                {
                    "bioguideId": "S001",
                    "fullName": "Rep. Sponsor One",
                    "party": "D",
                    "state": "NJ",
                    "url": "https://api.congress.gov/v3/member/S001",
                }
            ],
            "cosponsors": [
                {
                    "bioguideId": "C001",
                    "fullName": "Rep. Cosponsor One",
                    "party": "D",
                    "state": "NJ",
                    "url": "https://api.congress.gov/v3/member/C001",
                },
                {
                    "bioguideId": "C002",
                    "fullName": "Rep. Cosponsor Two",
                    "party": "R",
                    "state": "TX",
                    "url": "https://api.congress.gov/v3/member/C002",
                },
            ],
        }
    )
    events = sponsorship_events_from_bill(bill)
    ego = build_ego_graph(
        events,
        "C001",
        EgoNetworkConfig(congress=118, direction="incoming", max_neighbors=10, max_edges=10),
    )

    node_ids = {node.id for node in ego.nodes}
    assert node_ids == {"S001", "C001"}


def test_graph_node_labels_use_congressional_format() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, min_weight=1, max_edges=10))
    labels = {node.id: node.label for node in graph.nodes}
    assert labels["S001"] == "Rep. One, Sponsor [D-NJ-7]"
    assert labels["C002"] == "Rep. Two, Cosponsor [R-TX]"


def test_graph_slice_to_sigma_payload_matches_frontend_shape() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, min_weight=1, max_edges=10))
    payload = graph_slice_to_sigma_payload(graph)

    assert payload["graphKey"] == build_projection_key(GraphExploreConfig(congress=118))
    assert payload["nodes"]
    assert payload["edges"][0]["attributes"]["weight"] >= 1
    assert "limits" in payload


def test_export_graph_slice_json_writes_file(tmp_path: Path) -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, min_weight=1, max_edges=10))
    output = tmp_path / "graph.json"
    export_graph_slice_json(graph, output)

    assert output.exists()
    assert "graphKey" in output.read_text(encoding="utf-8")


def test_rank_relationships_returns_sorted_pairs() -> None:
    events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    ranked = rank_relationships(events, GraphExploreConfig(congress=118, min_weight=1), top_n=5)

    assert len(ranked) == 2
    assert ranked[0].weight >= ranked[1].weight


def test_chamber_filter_excludes_non_matching_bills() -> None:
    house_events = sponsorship_events_from_bill(_sample_bill(cosponsors=_sample_cosponsors()))
    senate_bill = Bill.model_validate(
        {
            "congress": 118,
            "number": 10,
            "type": "S",
            "originChamber": "Senate",
            "sponsors": [
                {
                    "bioguideId": "S010",
                    "fullName": "Sen. Ten",
                    "party": "D",
                    "state": "DE",
                    "url": "https://api.congress.gov/v3/member/S010",
                }
            ],
            "cosponsors": [
                {
                    "bioguideId": "S011",
                    "fullName": "Sen. Eleven",
                    "party": "D",
                    "state": "RI",
                    "url": "https://api.congress.gov/v3/member/S011",
                }
            ],
        }
    )
    senate_events = sponsorship_events_from_bill(senate_bill)
    config = GraphExploreConfig(
        congress=118,
        chamber=GraphChamberFilter.HOUSE,
        min_weight=1,
        max_edges=10,
    )
    graph = build_graph_slice(house_events + senate_events, config)

    node_ids = {node.id for node in graph.nodes}
    assert "S010" not in node_ids
    assert "S001" in node_ids
