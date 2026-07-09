"""Tests for density-aware graph visual spacing."""

from __future__ import annotations

from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphRenderConfig,
    build_graph_slice,
    generate_dense_sponsorship_events,
    prepare_sigma_render_payload,
)
from congressgov.services.export.graph.layout import assign_layout_positions
from congressgov.services.export.graph.models import GraphMemberNode, LayoutAlgorithm
from congressgov.services.export.graph.visual_spacing import (
    compute_graph_visual_spacing,
    layout_spread_for_counts,
    scaled_max_node_size,
)


def test_visual_spacing_grows_with_node_count() -> None:
    small = compute_graph_visual_spacing(25, 100)
    large = compute_graph_visual_spacing(535, 1500)

    assert large["coordinate_spread"] > small["coordinate_spread"]
    assert large["node_size_scale"] < small["node_size_scale"]


def test_layout_spread_increases_for_large_graphs() -> None:
    small = layout_spread_for_counts(25, 100)
    large = layout_spread_for_counts(535, 1500)

    assert large > small


def test_scaled_max_node_size_shrinks_for_roster_scale_graphs() -> None:
    small = scaled_max_node_size(14.0, 25)
    large = scaled_max_node_size(14.0, 535)

    assert large < small
    assert large >= 2.5


def test_prepare_sigma_payload_expands_coordinates_for_dense_graph() -> None:
    events = generate_dense_sponsorship_events(
        member_count=120,
        bills_per_sponsor=10,
        cosponsors_per_bill=20,
        seed=3,
    )
    graph = build_graph_slice(
        events,
        GraphExploreConfig(congress=118, min_weight=1, max_edges=5000),
    )
    payload = prepare_sigma_render_payload(graph, GraphRenderConfig())

    xs = [node["attributes"]["x"] for node in payload["graph"]["nodes"]]
    ys = [node["attributes"]["y"] for node in payload["graph"]["nodes"]]
    spread = payload["renderConfig"]["coordinateSpread"]

    assert spread > 1.0
    assert max(xs) - min(xs) > 1.0
    assert max(ys) - min(ys) > 1.0
    assert payload["renderConfig"]["maxNodeSize"] < 14.0


def test_grid_layout_used_for_large_node_only_graph() -> None:
    nodes = [
        GraphMemberNode(id=f"M{i:03d}", label=f"Member {i}", party="D", state="NY")
        for i in range(100)
    ]
    assign_layout_positions(nodes, [], algorithm=LayoutAlgorithm.SPRING)

    xs = [node.x for node in nodes if node.x is not None]
    ys = [node.y for node in nodes if node.y is not None]
    assert len(xs) == 100
    assert max(xs) - min(xs) > 5
    assert max(ys) - min(ys) > 5
