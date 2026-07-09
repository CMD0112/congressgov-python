"""Tests for advanced network graph rendering and metrics."""

from __future__ import annotations

from pathlib import Path

import pytest

from congressgov.models.entities.bill import Bill
from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphRenderConfig,
    GraphVisualizer,
    LayoutAlgorithm,
    NodeColorMode,
    build_graph_slice,
    build_layout_key,
    build_matrix,
    export_graph_slice_csv,
    export_graph_slice_gexf,
    export_graph_slice_graphml,
    export_interactive_html,
    sponsorship_events_from_bill,
)


def _sample_events():
    bill = Bill.model_validate(
        {
            "congress": 118,
            "number": 1,
            "type": "HR",
            "title": "Sample Health Bill",
            "originChamber": "House",
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
    return sponsorship_events_from_bill(bill)


def test_build_graph_slice_assigns_layout_key_and_communities() -> None:
    graph = build_graph_slice(
        _sample_events(),
        GraphExploreConfig(
            congress=118,
            layout_algorithm=LayoutAlgorithm.SHELL_PARTY,
            compute_communities=True,
            compute_advanced_metrics=True,
        ),
    )

    assert graph.layout_key == build_layout_key(GraphExploreConfig(congress=118, layout_algorithm=LayoutAlgorithm.SHELL_PARTY))
    assert all(node.community for node in graph.nodes)
    assert all(node.x is not None and node.y is not None for node in graph.nodes)


def test_export_interactive_html_writes_sigma_graphology_page(tmp_path: Path) -> None:
    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    output = tmp_path / "explorer.html"
    export_interactive_html(graph, output, render_config=GraphRenderConfig(node_color_mode=NodeColorMode.COMMUNITY))

    content = output.read_text(encoding="utf-8")
    assert "graphology" in content
    assert "sigma@2.4.0" in content
    assert "new Sigma(graph, container" in content
    assert "addEdgeWithKey" in content
    assert "minEdgeWeight" in content
    assert "fitGraph" in content
    assert "partyFilters" in content
    assert "topRelationships" in content
    assert "viewMode" in content
    assert "switchView" in content
    assert "escapeHtml" in content
    assert "openEgoForMember" in content
    assert "egoHud" in content
    assert "viewEgoBtn" in content
    assert "pickDefaultEgoCenter" in content
    assert "filteredMembers" in content
    assert "minCentrality" in content
    assert "toggleSettings" in content
    assert "settingsPanel" in content
    assert "statusBar" in content
    assert "__PAGE_TITLE__" not in content
    assert "exportFilteredJson" in content
    assert "fullLabel" in content
    assert "nodeDisplayLabel" in content
    assert "partyColumns" in content
    assert "degreeRings" in content
    assert '"views"' in content or "views.matrix" in content
    assert "S001" in content
    assert "Rep. One, Sponsor [D-NJ-7]" in content


def test_export_interactive_html_uses_render_title(tmp_path: Path) -> None:
    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    output = tmp_path / "explorer.html"
    export_interactive_html(
        graph,
        output,
        render_config=GraphRenderConfig(title="118th Congress HR network"),
    )

    content = output.read_text(encoding="utf-8")
    assert "<title>118th Congress HR network</title>" in content
    assert "<h1 id=\"pageTitle\">118th Congress HR network</h1>" in content


def test_prepare_sigma_render_payload_includes_render_config() -> None:
    from congressgov.services.export.graph import prepare_sigma_render_payload

    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    payload = prepare_sigma_render_payload(graph, GraphRenderConfig(node_color_mode=NodeColorMode.PARTY))

    assert "graph" in payload
    assert "renderConfig" in payload
    assert "controls" in payload
    assert payload["controls"]["maxEdgeWeight"] >= 1
    assert payload["graph"]["nodes"][0]["attributes"]["color"]
    assert payload["topRelationships"][0]["edgeKey"]
    assert "views" in payload
    assert payload["graph"]["nodes"][0]["attributes"]["fullLabel"]
    assert "Rep." in payload["graph"]["nodes"][0]["attributes"]["fullLabel"]
    assert payload["views"]["members"][0]["label"].startswith("Rep.")
    assert payload["graph"]["nodes"][0]["attributes"]["layoutX"] is not None
    assert payload["renderConfig"]["title"] is None or isinstance(payload["renderConfig"]["title"], str)


def test_explorer_views_payload_helpers() -> None:
    from congressgov.services.export.graph.explorer_views import (
        build_matrix_view_payload,
        build_member_leaderboard_payload,
        build_ranked_edges_payload,
    )
    from congressgov.services.export.graph.render import graph_slice_to_sigma_payload

    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    graph_payload = graph_slice_to_sigma_payload(graph)

    matrix = build_matrix_view_payload(graph_payload)
    assert matrix["rows"]
    assert matrix["cells"]
    assert matrix["labels"]

    ranked = build_ranked_edges_payload(graph_payload)
    assert ranked[0]["weight"] >= ranked[-1]["weight"]

    members = build_member_leaderboard_payload(graph_payload)
    assert members[0]["totalDegree"] >= members[-1]["totalDegree"]


def test_graph_visualizer_draws_graph() -> None:
    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    visualizer = GraphVisualizer(GraphRenderConfig(title="Sample graph"))
    figure = visualizer.draw_graph(graph)
    assert figure.axes


def test_matrix_heatmap_renders() -> None:
    events = _sample_events()
    matrix = build_matrix(events, GraphExploreConfig(congress=118), sort="party")
    visualizer = GraphVisualizer(GraphRenderConfig(title="Matrix"))
    figure = visualizer.draw_matrix_heatmap(matrix)
    assert figure.axes


def test_export_graph_slice_csv_and_graphml(tmp_path: Path) -> None:
    graph = build_graph_slice(_sample_events(), GraphExploreConfig(congress=118))
    csv_dir = tmp_path / "csv"
    nodes_path, edges_path = export_graph_slice_csv(graph, csv_dir)
    graphml_path = tmp_path / "graph.graphml"
    gexf_path = tmp_path / "graph.gexf"

    export_graph_slice_graphml(graph, graphml_path)
    export_graph_slice_gexf(graph, gexf_path)

    assert nodes_path.exists()
    assert edges_path.exists()
    assert "S001" in nodes_path.read_text(encoding="utf-8")
    assert graphml_path.read_text(encoding="utf-8").startswith("<?xml")
    assert gexf_path.read_text(encoding="utf-8").startswith("<?xml")


def test_graph_visualizer_requires_matplotlib(monkeypatch: pytest.MonkeyPatch) -> None:
    import congressgov.services.export.graph.visualize as visualize_module

    monkeypatch.setattr(visualize_module, "MATPLOTLIB_AVAILABLE", False)
    with pytest.raises(ImportError, match="matplotlib"):
        visualize_module.GraphVisualizer()
