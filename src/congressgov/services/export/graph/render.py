"""Render graph slices for Sigma.js / Graphology and JSON export."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Union

from .models import GraphSlice, MatrixSlice, enum_value, model_to_dict
from .networkx_support import build_weighted_graph

try:
    import networkx as nx
except ImportError:
    nx = None


def graph_slice_to_sigma_payload(graph_slice: GraphSlice) -> dict[str, Any]:
    """Convert a graph slice into a Sigma.js + Graphology compatible payload."""
    return {
        "graphKey": graph_slice.graph_key,
        "layoutKey": graph_slice.layout_key,
        "projection": enum_value(graph_slice.projection),
        "nodes": [
            {
                "key": node.id,
                "attributes": {
                    "label": node.label,
                    "party": node.party,
                    "state": node.state,
                    "district": node.district,
                    "chamber": node.chamber,
                    "size": node.size,
                    "centrality": node.centrality,
                    "betweenness": node.betweenness,
                    "pagerank": node.pagerank,
                    "community": node.community,
                    "x": node.x,
                    "y": node.y,
                    "weightedInDegree": node.weighted_in_degree,
                    "weightedOutDegree": node.weighted_out_degree,
                    "crossPartyRatio": node.cross_party_ratio,
                },
            }
            for node in graph_slice.nodes
        ],
        "edges": [
            {
                "key": edge.id,
                "source": edge.source,
                "target": edge.target,
                "attributes": {
                    "weight": edge.weight,
                    "originalWeight": edge.original_weight,
                    "lateWeight": edge.late_weight,
                    "withdrawnWeight": edge.withdrawn_weight,
                    "activeWeight": edge.active_weight,
                    "crossPartyWeight": edge.cross_party_weight,
                    "firstDate": edge.first_date.isoformat() if edge.first_date else None,
                    "lastDate": edge.last_date.isoformat() if edge.last_date else None,
                    "billCount": edge.bill_count,
                },
            }
            for edge in graph_slice.edges
        ],
        "limits": model_to_dict(graph_slice.limits),
    }


def graph_slice_to_api_payload(graph_slice: GraphSlice) -> dict[str, Any]:
    """Convert a graph slice into the overview API response shape from the design doc."""
    return {
        "graphKey": graph_slice.graph_key,
        "layoutKey": graph_slice.layout_key,
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "party": node.party,
                "state": node.state,
                "district": node.district,
                "chamber": node.chamber,
                "size": node.size,
                "centrality": node.centrality,
                "betweenness": node.betweenness,
                "pagerank": node.pagerank,
                "community": node.community,
                "x": node.x,
                "y": node.y,
            }
            for node in graph_slice.nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "originalWeight": edge.original_weight,
                "withdrawnWeight": edge.withdrawn_weight,
                "crossPartyWeight": edge.cross_party_weight,
                "firstDate": edge.first_date.isoformat() if edge.first_date else None,
                "lastDate": edge.last_date.isoformat() if edge.last_date else None,
            }
            for edge in graph_slice.edges
        ],
        "limits": model_to_dict(graph_slice.limits),
    }


def matrix_slice_to_api_payload(matrix_slice: MatrixSlice) -> dict[str, Any]:
    """Convert a matrix slice into the sparse matrix API response shape."""
    return model_to_dict(matrix_slice)


def _build_networkx_graph(graph_slice: GraphSlice) -> Any:
    graph = build_weighted_graph(graph_slice.nodes, graph_slice.edges, directed=True)
    if graph is None:
        return None
    for node in graph_slice.nodes:
        graph.nodes[node.id].update(
            label=node.label,
            party=node.party,
            state=node.state,
            community=node.community,
            x=node.x,
            y=node.y,
        )
    for edge in graph_slice.edges:
        graph.edges[edge.source, edge.target].update(
            key=edge.id,
            cross_party_weight=edge.cross_party_weight,
        )
    return graph


def export_graph_slice_json(
    graph_slice: GraphSlice,
    filepath: Union[str, Path],
    *,
    format: str = "sigma",
    indent: int = 2,
) -> None:
    """Write a graph slice to JSON on disk."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = graph_slice_to_sigma_payload(graph_slice) if format == "sigma" else graph_slice_to_api_payload(graph_slice)
    path.write_text(json.dumps(payload, indent=indent), encoding="utf-8")


def export_matrix_slice_json(matrix_slice: MatrixSlice, filepath: Union[str, Path], *, indent: int = 2) -> None:
    """Write a matrix slice to JSON on disk."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(matrix_slice_to_api_payload(matrix_slice), indent=indent), encoding="utf-8")


def export_graph_slice_csv(graph_slice: GraphSlice, directory: Union[str, Path]) -> tuple[Path, Path]:
    """Write node and edge tables as CSV files."""
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = output_dir / "nodes.csv"
    edges_path = output_dir / "edges.csv"

    node_rows = [node.model_dump(mode="json") for node in graph_slice.nodes]
    edge_rows = [edge.model_dump(mode="json") for edge in graph_slice.edges]

    if node_rows:
        with nodes_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=node_rows[0].keys())
            writer.writeheader()
            writer.writerows(node_rows)
    else:
        nodes_path.write_text("", encoding="utf-8")

    if edge_rows:
        with edges_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=edge_rows[0].keys())
            writer.writeheader()
            writer.writerows(edge_rows)
    else:
        edges_path.write_text("", encoding="utf-8")

    return nodes_path, edges_path


def export_graph_slice_graphml(graph_slice: GraphSlice, filepath: Union[str, Path]) -> None:
    """Write a graph slice to GraphML."""
    graph = _build_networkx_graph(graph_slice)
    if graph is None:
        raise ImportError("networkx is required for GraphML export. Install with: pip install congressgov[graph]")
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, path)


def export_graph_slice_gexf(graph_slice: GraphSlice, filepath: Union[str, Path]) -> None:
    """Write a graph slice to GEXF."""
    graph = _build_networkx_graph(graph_slice)
    if graph is None:
        raise ImportError("networkx is required for GEXF export. Install with: pip install congressgov[graph]")
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gexf(graph, path)
