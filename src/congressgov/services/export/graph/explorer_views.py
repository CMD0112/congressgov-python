"""Client-side view payloads for the interactive graph explorer."""

from __future__ import annotations

from typing import Any


def node_display_label(attributes: dict[str, Any], node_key: str) -> str:
    """Return the canonical member label for UI tables, search, and tooltips."""
    return (
        attributes.get("fullLabel")
        or attributes.get("label")
        or node_key
    )


def _party_sort_key(party: str | None) -> tuple[int, str]:
    order = {"D": 0, "R": 1, "I": 2}
    label = party or "Unknown"
    return (order.get(label, 9), label)


def build_matrix_view_payload(
    graph_payload: dict[str, Any],
    *,
    max_nodes: int = 120,
) -> dict[str, Any]:
    """Sparse adjacency matrix sorted by party for canvas rendering."""
    nodes = graph_payload.get("nodes") or []
    sorted_nodes = sorted(
        nodes,
        key=lambda node: (
            _party_sort_key(node.get("attributes", {}).get("party")),
            str(node_display_label(node.get("attributes", {}), node.get("key", ""))),
        ),
    )
    rows = [node["key"] for node in sorted_nodes[:max_nodes]]
    row_index = {row_id: index for index, row_id in enumerate(rows)}
    cells: list[dict[str, Any]] = []
    for edge in graph_payload.get("edges") or []:
        source = edge.get("source")
        target = edge.get("target")
        if source not in row_index or target not in row_index:
            continue
        attrs = edge.get("attributes") or {}
        cells.append(
            {
                "row": source,
                "column": target,
                "rowIndex": row_index[source],
                "columnIndex": row_index[target],
                "weight": int(attrs.get("weight") or 0),
                "crossPartyWeight": int(attrs.get("crossPartyWeight") or 0),
            }
        )
    labels = {
        node["key"]: node_display_label(node.get("attributes", {}), node["key"])
        for node in sorted_nodes[:max_nodes]
    }
    return {
        "rows": rows,
        "labels": labels,
        "cells": cells,
        "truncated": len(sorted_nodes) > max_nodes,
        "totalNodes": len(sorted_nodes),
    }


def build_ranked_edges_payload(
    graph_payload: dict[str, Any],
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    node_labels = {
        node["key"]: node_display_label(node.get("attributes", {}), node["key"])
        for node in graph_payload.get("nodes") or []
    }
    ranked = sorted(
        graph_payload.get("edges") or [],
        key=lambda edge: int(
            (edge.get("attributes") or {}).get("weight") or 0
        ),
        reverse=True,
    )[:limit]
    return [
        {
            "edgeKey": edge.get("key"),
            "source": edge.get("source"),
            "target": edge.get("target"),
            "sourceLabel": node_labels.get(
                edge.get("source"), edge.get("source")
            ),
            "targetLabel": node_labels.get(
                edge.get("target"), edge.get("target")
            ),
            "weight": int((edge.get("attributes") or {}).get("weight") or 0),
            "crossPartyWeight": int(
                (edge.get("attributes") or {}).get("crossPartyWeight") or 0
            ),
        }
        for edge in ranked
    ]


def build_member_leaderboard_payload(
    graph_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    for node in graph_payload.get("nodes") or []:
        attrs = node.get("attributes") or {}
        in_degree = float(attrs.get("weightedInDegree") or 0)
        out_degree = float(attrs.get("weightedOutDegree") or 0)
        members.append(
            {
                "id": node["key"],
                "label": node_display_label(attrs, node["key"]),
                "party": attrs.get("party") or "Unknown",
                "state": attrs.get("state"),
                "inDegree": in_degree,
                "outDegree": out_degree,
                "totalDegree": in_degree + out_degree,
                "centrality": float(attrs.get("centrality") or 0),
                "crossPartyRatio": float(attrs.get("crossPartyRatio") or 0),
            }
        )
    members.sort(key=lambda item: (-item["totalDegree"], item["label"]))
    return members
