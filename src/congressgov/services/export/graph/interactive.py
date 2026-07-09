"""Standalone Sigma.js + Graphology interactive HTML explorer."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any, Union

from .models import GraphDensityAssessment, GraphRenderConfig, GraphSlice, GraphViewMode, NodeColorMode, enum_value
from .density import assess_graph_slice
from .visual_spacing import compute_graph_visual_spacing, scaled_max_node_size
from .explorer_views import (
    build_matrix_view_payload,
    build_member_leaderboard_payload,
    build_ranked_edges_payload,
)
from .render import graph_slice_to_sigma_payload

_EXPLORER_TEMPLATE_PATH = Path(__file__).with_name("explorer.html")

PARTY_COLORS = {
    "D": "#2563eb",
    "R": "#dc2626",
    "I": "#7c3aed",
    "Unknown": "#64748b",
}

COMMUNITY_COLORS = [
    "#2563eb",
    "#dc2626",
    "#16a34a",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#ca8a04",
    "#db2777",
    "#4f46e5",
    "#0d9488",
]

GRAPHOLOGY_CDN = "https://cdn.jsdelivr.net/npm/graphology@0.25.4/dist/graphology.umd.min.js"
SIGMA_CDN = "https://cdn.jsdelivr.net/npm/sigma@2.4.0/build/sigma.min.js"


def _community_color(community: str | None) -> str:
    if not community:
        return PARTY_COLORS["Unknown"]
    index = sum(ord(char) for char in community) % len(COMMUNITY_COLORS)
    return COMMUNITY_COLORS[index]


def _node_color(attributes: dict[str, Any], mode: str) -> str:
    if mode == NodeColorMode.COMMUNITY.value:
        return _community_color(str(attributes.get("community")))
    if mode == NodeColorMode.CENTRALITY.value:
        centrality = float(attributes.get("centrality") or 0.0)
        channel = int(80 + min(max(centrality, 0.0), 1.0) * 175)
        return f"rgb({channel}, {int(channel * 0.55)}, 255)"
    party = str(attributes.get("party") or "Unknown")
    return PARTY_COLORS.get(party, PARTY_COLORS["Unknown"])


def _edge_color(attributes: dict[str, Any], *, alpha: float = 1.0) -> str:
    if int(attributes.get("crossPartyWeight") or 0) > 0:
        return f"rgba(147, 51, 234, {alpha:.3f})"
    return f"rgba(100, 116, 139, {alpha:.3f})"


def _normalize_positions(
    graph_payload: dict[str, Any],
    *,
    node_count: int,
    edge_count: int,
) -> dict[str, float]:
    """Map layout coordinates into Sigma space with density-aware spread.

    Positions are min-max normalized, then expanded around the canvas center so
    force-directed layouts gain area as graphs grow. Returns spacing metadata
  for the embedded explorer.
    """
    nodes = graph_payload["nodes"]
    xs = [float(node["attributes"]["x"]) for node in nodes if node["attributes"].get("x") is not None]
    ys = [float(node["attributes"]["y"]) for node in nodes if node["attributes"].get("y") is not None]
    spacing = compute_graph_visual_spacing(node_count, edge_count)
    if not xs or not ys:
        return spacing

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)
    padding = 0.1
    center = 0.5
    spread = spacing["coordinate_spread"]

    for node in nodes:
        attrs = node["attributes"]
        if attrs.get("x") is None or attrs.get("y") is None:
            continue
        norm_x = padding + ((float(attrs["x"]) - min_x) / span_x) * (1 - 2 * padding)
        norm_y = padding + ((float(attrs["y"]) - min_y) / span_y) * (1 - 2 * padding)
        attrs["x"] = center + (norm_x - center) * spread
        attrs["y"] = center + (norm_y - center) * spread

    return spacing


def _density_visual_settings(
    assessment: GraphDensityAssessment,
    *,
    node_count: int,
) -> dict[str, Any]:
    """Return size/opacity caps tuned for graph density."""
    tier = enum_value(assessment.tier)
    matrix_recommended = enum_value(assessment.recommended_view) == GraphViewMode.MATRIX.value

    if tier in {"large", "very_large"} or matrix_recommended:
        base_max_node = 9.0
        return {
            "densityMode": "compact",
            "maxNodeSize": scaled_max_node_size(base_max_node, node_count),
            "maxEdgeSize": 0.55,
            "edgeOpacity": 0.12 if assessment.edge_count >= 1500 else 0.18,
            "hideLabels": True,
            "labelMinCentrality": 1.0,
        }
    if tier == "medium" or assessment.edge_count >= 750:
        base_max_node = 11.0
        return {
            "densityMode": "balanced",
            "maxNodeSize": scaled_max_node_size(base_max_node, node_count),
            "maxEdgeSize": 0.85,
            "edgeOpacity": 0.28,
            "hideLabels": assessment.edge_count >= 1200,
            "labelMinCentrality": max(0.55, 0.35),
        }
    return {
        "densityMode": "normal",
        "maxNodeSize": scaled_max_node_size(14.0, node_count),
        "maxEdgeSize": 1.2,
        "edgeOpacity": 0.55,
        "hideLabels": False,
        "labelMinCentrality": 0.35,
    }


def _visual_node_size(centrality: float, *, max_size: float) -> float:
    clamped = min(max(centrality, 0.0), 1.0)
    return 4.0 + clamped * max(max_size - 4.0, 1.0)


def _visual_edge_size(weight: int, *, max_weight: int, max_size: float) -> float:
    if max_weight <= 1:
        return min(max_size, 0.35)
    normalized = math.log2(weight + 1) / math.log2(max_weight + 1)
    return 0.15 + normalized * max(max_size - 0.15, 0.1)


def _enforce_max_interactive_edges(graph_payload: dict[str, Any], *, max_edges: int) -> None:
    """Cap the embedded HTML payload to ``max_edges``, dropping now-isolated nodes.

    ``GraphRenderConfig.max_interactive_edges`` was previously defined but never
    applied, so very large slices could still be embedded verbatim in the HTML
    explorer despite the documented cap.
    """
    edges = graph_payload["edges"]
    if len(edges) <= max_edges:
        return
    edges.sort(key=lambda edge: int(edge["attributes"].get("weight") or 0), reverse=True)
    kept_edges = edges[:max_edges]
    graph_payload["edges"] = kept_edges

    connected = {edge["source"] for edge in kept_edges} | {edge["target"] for edge in kept_edges}
    graph_payload["nodes"] = [node for node in graph_payload["nodes"] if node["key"] in connected]


def prepare_sigma_render_payload(
    graph_slice: GraphSlice,
    render_config: GraphRenderConfig,
) -> dict[str, Any]:
    """Build the embedded payload for Sigma.js + Graphology HTML export."""
    graph_payload = graph_slice_to_sigma_payload(graph_slice)
    _enforce_max_interactive_edges(graph_payload, max_edges=render_config.max_interactive_edges)
    node_count = len(graph_payload["nodes"])
    edge_count = len(graph_payload["edges"])
    spacing = _normalize_positions(
        graph_payload,
        node_count=node_count,
        edge_count=edge_count,
    )
    for node in graph_payload["nodes"]:
        attrs = node["attributes"]
        if attrs.get("x") is not None:
            attrs["layoutX"] = float(attrs["x"])
        if attrs.get("y") is not None:
            attrs["layoutY"] = float(attrs["y"])

    for node in graph_payload["nodes"]:
        attrs = node["attributes"]
        attrs["fullLabel"] = attrs.get("label") or node["key"]

    color_mode = enum_value(render_config.node_color_mode)
    assessment = assess_graph_slice(graph_slice)
    visual_settings = _density_visual_settings(assessment, node_count=node_count)
    label_threshold = max(
        render_config.label_min_centrality,
        float(visual_settings["labelMinCentrality"]),
    )
    enable_hover_highlight = (
        not render_config.simplify_hover_for_large_graphs
        or enum_value(assessment.tier) in {"small", "medium"}
    )
    max_edge_weight = max(
        (int(edge["attributes"].get("weight") or 1) for edge in graph_payload["edges"]),
        default=1,
    )

    for node in graph_payload["nodes"]:
        attrs = node["attributes"]
        centrality = float(attrs.get("centrality") or 0.0)
        attrs["color"] = _node_color(attrs, color_mode)
        attrs["size"] = _visual_node_size(centrality, max_size=float(visual_settings["maxNodeSize"]))
        # Sigma render label (may be blank); fullLabel is always kept for UI/search.
        attrs["label"] = attrs["fullLabel"]
        if visual_settings["hideLabels"] or centrality < label_threshold:
            attrs["label"] = ""

    edge_opacity = float(visual_settings["edgeOpacity"])
    for edge in graph_payload["edges"]:
        attrs = edge["attributes"]
        weight = int(attrs.get("weight") or 1)
        attrs["size"] = _visual_edge_size(
            weight,
            max_weight=max_edge_weight,
            max_size=float(visual_settings["maxEdgeSize"]),
        )
        attrs["color"] = _edge_color(attrs, alpha=edge_opacity)
        attrs["label"] = ""

    top_relationships = sorted(
        graph_payload["edges"],
        key=lambda edge: int(edge["attributes"].get("weight") or 0),
        reverse=True,
    )[:20]
    node_labels = {
        node["key"]: node["attributes"].get("fullLabel") or node["key"]
        for node in graph_payload["nodes"]
    }
    parties = sorted(
        {
            str(node["attributes"].get("party") or "Unknown")
            for node in graph_payload["nodes"]
        }
    )

    return {
        "graph": graph_payload,
        "renderConfig": {
            "title": render_config.title,
            "nodeColorMode": color_mode,
            "labelMinCentrality": label_threshold,
            "showEdgeArrows": render_config.show_edge_arrows,
            "partyColors": PARTY_COLORS,
            "communityColors": COMMUNITY_COLORS,
            "enableHoverHighlight": enable_hover_highlight,
            "coordinateSpread": spacing["coordinate_spread"],
            "nodeSizeScale": spacing["node_size_scale"],
            **visual_settings,
        },
        "controls": {
            "maxEdgeWeight": max_edge_weight,
            "minEdgeWeight": 1,
            "parties": parties,
            "defaultEdgeOpacity": edge_opacity,
        },
        "assessment": assessment.model_dump(mode="json"),
        "topRelationships": [
            {
                "edgeKey": edge["key"],
                "source": edge["source"],
                "target": edge["target"],
                "sourceLabel": node_labels.get(edge["source"], edge["source"]),
                "targetLabel": node_labels.get(edge["target"], edge["target"]),
                "weight": int(edge["attributes"].get("weight") or 0),
                "crossPartyWeight": int(edge["attributes"].get("crossPartyWeight") or 0),
            }
            for edge in top_relationships
        ],
        "views": {
            "matrix": build_matrix_view_payload(graph_payload),
            "rankedEdges": build_ranked_edges_payload(graph_payload),
            "members": build_member_leaderboard_payload(graph_payload),
        },
    }


def _load_explorer_template() -> str:
    return _EXPLORER_TEMPLATE_PATH.read_text(encoding="utf-8")


def _embed_script_json(payload: dict[str, Any]) -> str:
    """Serialize payload for inline <script> embedding."""
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def _page_title(render_config: GraphRenderConfig) -> str:
    return render_config.title or "Congress sponsor/cosponsor network"


def export_interactive_html(
    graph_slice: GraphSlice,
    filepath: Union[str, Path],
    *,
    render_config: GraphRenderConfig | None = None,
) -> None:
    """Write a self-contained Sigma.js + Graphology HTML explorer."""
    config = render_config or GraphRenderConfig()
    payload = prepare_sigma_render_payload(graph_slice, config)
    page_title = _page_title(config)
    escaped_title = html.escape(page_title, quote=False)
    html_content = (
        _load_explorer_template()
        .replace("__PAYLOAD_JSON__", _embed_script_json(payload))
        .replace("__GRAPHOLOGY_CDN__", GRAPHOLOGY_CDN)
        .replace("__SIGMA_CDN__", SIGMA_CDN)
        .replace("__PAGE_TITLE__", escaped_title)
    )
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_content, encoding="utf-8")


def export_sigma_html(
    graph_slice: GraphSlice,
    filepath: Union[str, Path],
    *,
    render_config: GraphRenderConfig | None = None,
) -> None:
    """Alias for :func:`export_interactive_html` using Sigma.js + Graphology."""
    export_interactive_html(graph_slice, filepath, render_config=render_config)
