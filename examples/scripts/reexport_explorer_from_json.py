"""Re-export interactive HTML from a saved sigma-format graph JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from congressgov.services.export.graph import GraphRenderConfig, GraphSlice, export_interactive_html
from congressgov.services.export.graph.models import GraphEdge, GraphLimits, GraphMemberNode, GraphProjectionType

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = REPO_ROOT / "examples" / "output" / "network_graph" / "live_graph_api.json"
DEFAULT_HTML = REPO_ROOT / "examples" / "output" / "network_graph" / "live_network_explorer.html"


def graph_slice_from_sigma_json(payload: dict) -> GraphSlice:
    nodes = [
        GraphMemberNode(
            id=node["key"],
            label=attrs.get("label"),
            party=attrs.get("party"),
            state=attrs.get("state"),
            district=attrs.get("district"),
            chamber=attrs.get("chamber"),
            size=float(attrs.get("size") or 1.0),
            centrality=attrs.get("centrality"),
            betweenness=attrs.get("betweenness"),
            pagerank=attrs.get("pagerank"),
            community=attrs.get("community"),
            x=attrs.get("x"),
            y=attrs.get("y"),
            weighted_in_degree=float(attrs.get("weightedInDegree") or 0.0),
            weighted_out_degree=float(attrs.get("weightedOutDegree") or 0.0),
            cross_party_ratio=attrs.get("crossPartyRatio"),
        )
        for node in payload["nodes"]
        for attrs in [node.get("attributes") or {}]
    ]
    edges = [
        GraphEdge(
            id=edge["key"],
            source=edge["source"],
            target=edge["target"],
            weight=int(attrs.get("weight") or 0),
            original_weight=int(attrs.get("originalWeight") or 0),
            late_weight=int(attrs.get("lateWeight") or 0),
            withdrawn_weight=int(attrs.get("withdrawnWeight") or 0),
            active_weight=int(attrs.get("activeWeight") or 0),
            cross_party_weight=int(attrs.get("crossPartyWeight") or 0),
            bill_count=int(attrs.get("billCount") or 0),
        )
        for edge in payload["edges"]
        for attrs in [edge.get("attributes") or {}]
    ]
    limits_payload = payload.get("limits") or {}
    limits = GraphLimits(
        max_edges=int(limits_payload.get("max_edges") or len(edges)),
        edge_count_before_limit=int(
            limits_payload.get("edge_count_before_limit") or len(edges)
        ),
        was_truncated=bool(limits_payload.get("was_truncated")),
        shown_edges=int(limits_payload.get("shown_edges") or len(edges)),
        recommended_actions=list(limits_payload.get("recommended_actions") or []),
    )
    return GraphSlice(
        graph_key=str(payload.get("graphKey") or "reexport"),
        layout_key=payload.get("layoutKey"),
        projection=GraphProjectionType(str(payload.get("projection") or "sponsor_to_cosponsor")),
        nodes=nodes,
        edges=edges,
        limits=limits,
    )


def main() -> int:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JSON
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HTML
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    graph = graph_slice_from_sigma_json(payload)
    export_interactive_html(
        graph,
        html_path,
        render_config=GraphRenderConfig(title="Congress sponsor/cosponsor network"),
    )
    print(html_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
