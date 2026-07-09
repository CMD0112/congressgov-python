"""Tests for large/dense graph assessment and synthetic datasets."""

from __future__ import annotations

from pathlib import Path

from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphRenderConfig,
    GraphSizeTier,
    GraphViewMode,
    assess_graph_slice,
    build_graph_slice,
    build_matrix,
    export_interactive_html,
    generate_dense_sponsorship_events,
    profile_graph_rendering,
    recommend_explore_config,
)


def test_generate_dense_sponsorship_events_scales() -> None:
    events = generate_dense_sponsorship_events(
        member_count=20,
        bills_per_sponsor=5,
        cosponsors_per_bill=10,
        seed=1,
    )
    assert len(events) == 20 * 5 * 10


def test_assess_graph_slice_marks_very_large_dense_graphs() -> None:
    events = generate_dense_sponsorship_events(
        member_count=80,
        bills_per_sponsor=15,
        cosponsors_per_bill=35,
        seed=7,
    )
    graph = build_graph_slice(
        events,
        GraphExploreConfig(congress=118, min_weight=1, max_edges=50000),
    )
    assessment = assess_graph_slice(graph)

    assert assessment.node_count > 0
    assert assessment.edge_count > 1000
    assert assessment.tier in {GraphSizeTier.LARGE, GraphSizeTier.VERY_LARGE, GraphSizeTier.MEDIUM}
    assert assessment.recommended_view in {GraphViewMode.OVERVIEW, GraphViewMode.MATRIX}


def test_recommend_explore_config_tightens_dense_graph_filters() -> None:
    events = generate_dense_sponsorship_events(member_count=60, bills_per_sponsor=10, cosponsors_per_bill=25)
    loose = GraphExploreConfig(congress=118, min_weight=1, max_edges=20000)
    graph = build_graph_slice(events, loose)
    assessment = assess_graph_slice(graph)
    recommended = recommend_explore_config(
        loose,
        assessment,
        was_truncated=graph.limits.was_truncated,
    )

    assert recommended.max_edges <= loose.max_edges
    if graph.limits.was_truncated and assessment.tier in {
        GraphSizeTier.LARGE,
        GraphSizeTier.VERY_LARGE,
    }:
        assert recommended.min_weight >= 2
        assert recommended.compute_advanced_metrics is False


def test_recommend_explore_config_preserves_max_edges_when_not_truncated() -> None:
    events = generate_dense_sponsorship_events(member_count=20, bills_per_sponsor=5, cosponsors_per_bill=10)
    config = GraphExploreConfig(congress=118, min_weight=1, max_edges=10000)
    graph = build_graph_slice(events, config)
    assessment = assess_graph_slice(graph)

    assert graph.limits.was_truncated is False
    recommended = recommend_explore_config(
        config,
        assessment,
        was_truncated=graph.limits.was_truncated,
    )
    assert recommended.max_edges == 10000
    assert recommended.min_weight == 1


def test_recommend_explore_config_preserves_min_weight_when_not_truncated() -> None:
    events = generate_dense_sponsorship_events(
        member_count=80,
        bills_per_sponsor=12,
        cosponsors_per_bill=30,
        seed=7,
    )
    config = GraphExploreConfig(congress=118, min_weight=1, max_edges=50000)
    graph = build_graph_slice(events, config)
    assessment = assess_graph_slice(graph)

    assert graph.limits.was_truncated is False
    recommended = recommend_explore_config(
        config,
        assessment,
        was_truncated=graph.limits.was_truncated,
    )
    assert recommended.min_weight == 1
    assert recommended.max_edges == 50000


def test_truncated_graph_surfaces_warnings() -> None:
    events = generate_dense_sponsorship_events(member_count=40, bills_per_sponsor=8, cosponsors_per_bill=20)
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, min_weight=1, max_edges=500))
    assessment = assess_graph_slice(graph)

    assert graph.limits.was_truncated is True
    assert assessment.warnings
    assert "Switch to matrix view" in assessment.recommended_actions or assessment.recommended_view == GraphViewMode.MATRIX


def test_profile_graph_rendering_reports_payload_size() -> None:
    events = generate_dense_sponsorship_events(member_count=25, bills_per_sponsor=6, cosponsors_per_bill=12)
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, max_edges=3000))
    profile = profile_graph_rendering(graph, GraphRenderConfig())

    assert profile["sigmaJsonBytes"] > 0
    assert profile["htmlJsonBytes"] > 0
    assert profile["assessment"]["tier"]


def test_dense_graph_html_includes_assessment_warnings(tmp_path: Path) -> None:
    events = generate_dense_sponsorship_events(member_count=30, bills_per_sponsor=8, cosponsors_per_bill=18)
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, max_edges=1000))
    output = tmp_path / "dense.html"
    export_interactive_html(graph, output)

    content = output.read_text(encoding="utf-8")
    assert "assessment" in content
    assert "warnings" in content
    assert "enableHoverHighlight" in content
    assert "topRelationships" in content


def test_dense_graph_visual_sizes_are_capped() -> None:
    from congressgov.services.export.graph import prepare_sigma_render_payload

    events = generate_dense_sponsorship_events(
        member_count=80,
        bills_per_sponsor=12,
        cosponsors_per_bill=30,
        seed=7,
    )
    loose = GraphExploreConfig(congress=118, min_weight=1, max_edges=20000)
    graph = build_graph_slice(events, loose)
    assessment = assess_graph_slice(graph)
    safer = recommend_explore_config(
        loose,
        assessment,
        was_truncated=graph.limits.was_truncated,
    )
    dense_graph = build_graph_slice(events, safer)
    payload = prepare_sigma_render_payload(dense_graph, GraphRenderConfig())

    node_sizes = [node["attributes"]["size"] for node in payload["graph"]["nodes"]]
    edge_sizes = [edge["attributes"]["size"] for edge in payload["graph"]["edges"]]

    assert max(node_sizes) <= payload["renderConfig"]["maxNodeSize"]
    assert max(edge_sizes) <= payload["renderConfig"]["maxEdgeSize"]
    assert payload["renderConfig"]["edgeOpacity"] <= 0.3
    assert payload["renderConfig"]["hideLabels"] is True
    assert payload["topRelationships"]


def test_matrix_view_handles_dense_slice() -> None:
    events = generate_dense_sponsorship_events(member_count=15, bills_per_sponsor=5, cosponsors_per_bill=8)
    graph = build_graph_slice(events, GraphExploreConfig(congress=118, max_edges=2000))
    matrix = build_matrix(events, GraphExploreConfig(congress=118), sort="party")

    assert matrix.cells
    assert len(matrix.rows) == len(graph.nodes)
