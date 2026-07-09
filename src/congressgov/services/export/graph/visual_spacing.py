"""Anti-crowding spacing for graph layout and Sigma HTML rendering."""

from __future__ import annotations

import math

REFERENCE_NODE_COUNT = 25.0


def compute_graph_visual_spacing(node_count: int, edge_count: int) -> dict[str, float]:
    """Derive coordinate spread and node-size scale from graph size.

    ``coordinate_spread`` expands the layout canvas for force-directed graphs so
    node density stays roughly constant as graphs grow. ``node_size_scale``
    shrinks glyph size so packed layouts (e.g. roster circles) remain legible.
    """
    nodes = max(node_count, 1)
    spread = math.sqrt(nodes / REFERENCE_NODE_COUNT)
    avg_degree = (2.0 * edge_count) / nodes

    if edge_count >= 2000:
        spread *= 1.4
    elif edge_count >= 1000:
        spread *= 1.25
    elif edge_count >= 500:
        spread *= 1.1

    if avg_degree >= 12:
        spread *= 1.15
    elif avg_degree >= 6:
        spread *= 1.08

    spread = max(1.0, min(spread, 16.0))
    node_size_scale = math.sqrt(REFERENCE_NODE_COUNT / nodes)
    node_size_scale = min(1.0, max(0.28, node_size_scale))

    return {
        "coordinate_spread": spread,
        "node_size_scale": node_size_scale,
        "avg_degree": avg_degree,
    }


def layout_spread_for_counts(node_count: int, edge_count: int) -> float:
    """NetworkX layout scale before HTML normalization."""
    nodes = max(node_count, 1)
    base = max(1.0, math.sqrt(nodes) * 0.45)
    spacing = compute_graph_visual_spacing(node_count, edge_count)
    spread = base * math.sqrt(spacing["coordinate_spread"])

    if edge_count >= 1500:
        spread *= 1.25
    elif edge_count >= 750:
        spread *= 1.12

    if nodes >= 500:
        spread *= 1.15
    elif nodes >= 200:
        spread *= 1.08

    return spread


def scaled_max_node_size(base_max: float, node_count: int) -> float:
    """Shrink the node size cap for large graphs."""
    spacing = compute_graph_visual_spacing(node_count, edge_count=0)
    scaled = base_max * spacing["node_size_scale"]
    return max(2.5, min(base_max, scaled))
