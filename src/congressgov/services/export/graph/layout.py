"""Layout helpers for graph slices."""

from __future__ import annotations

import hashlib
import math
from typing import TYPE_CHECKING, Any

from .models import LayoutAlgorithm, enum_value
from .networkx_support import NETWORKX_AVAILABLE, build_weighted_graph
from .visual_spacing import layout_spread_for_counts

if TYPE_CHECKING:
    from .models import GraphEdge, GraphMemberNode

try:
    import networkx as nx
except ImportError:
    nx = None


def _layout_seed(layout_key: str | None) -> int:
    if not layout_key:
        return 42
    digest = hashlib.sha256(layout_key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _circular_layout(nodes: list[GraphMemberNode]) -> None:
    total = len(nodes)
    if total == 0:
        return
    if total > 75:
        _grid_layout(nodes)
        return
    for index, node in enumerate(nodes):
        angle = (2 * math.pi * index) / total
        node.x = math.cos(angle)
        node.y = math.sin(angle)


def _grid_layout(nodes: list[GraphMemberNode]) -> None:
    """Place many nodes on a centered grid to avoid circular overlap."""
    total = len(nodes)
    if total == 0:
        return
    cols = math.ceil(math.sqrt(total))
    for index, node in enumerate(nodes):
        row, col = divmod(index, cols)
        node.x = float(col) - (cols - 1) / 2.0
        node.y = float(row) - (math.ceil(total / cols) - 1) / 2.0


def _party_shells(nodes: list[GraphMemberNode]) -> list[list[str]]:
    parties: dict[str, list[str]] = {}
    for node in nodes:
        party = node.party or "Unknown"
        parties.setdefault(party, []).append(node.id)
    return [sorted(member_ids) for member_ids in parties.values()]


def _spring_layout_safe(
    graph: Any,
    *,
    nodes: list[GraphMemberNode],
    seed: int,
    spread: float,
    node_count: int,
    iterations: int,
) -> dict[str, tuple[float, float]]:
    """Run spring layout, falling back when SciPy or layout setup is unavailable."""
    if nx is None:
        raise RuntimeError("networkx is not available")
    k = spread / max(node_count, 1) ** 0.5
    try:
        return nx.spring_layout(graph, weight="weight", seed=seed, iterations=iterations, k=k)
    except (ImportError, ModuleNotFoundError, ValueError, RuntimeError):
        try:
            return nx.shell_layout(graph, nlist=_party_shells(nodes), scale=spread)
        except Exception:
            return nx.circular_layout(graph, scale=spread)


def assign_layout_positions(
    nodes: list[GraphMemberNode],
    edges: list[GraphEdge],
    *,
    algorithm: LayoutAlgorithm | str = LayoutAlgorithm.SPRING,
    layout_key: str | None = None,
) -> None:
    """Assign x/y coordinates for graph rendering."""
    if not nodes:
        return

    algorithm_name = enum_value(algorithm)
    if not NETWORKX_AVAILABLE or nx is None:
        _circular_layout(nodes)
        return

    graph = build_weighted_graph(nodes, edges, directed=True)
    if graph is None or graph.number_of_edges() == 0:
        _circular_layout(nodes)
        return

    seed = _layout_seed(layout_key)
    undirected = graph.to_undirected()
    positions: dict[str, tuple[float, float]]
    node_count = len(nodes)
    edge_count = len(edges)
    spread = layout_spread_for_counts(node_count, edge_count)

    if algorithm_name == LayoutAlgorithm.CIRCULAR.value:
        positions = nx.circular_layout(graph, scale=spread)
    elif algorithm_name == LayoutAlgorithm.SHELL_PARTY.value:
        positions = nx.shell_layout(graph, nlist=_party_shells(nodes), scale=spread)
    elif algorithm_name == LayoutAlgorithm.KAMADA_KAWAI.value and node_count <= 200:
        try:
            positions = nx.kamada_kawai_layout(undirected, weight="weight", scale=spread)
        except Exception:
            positions = _spring_layout_safe(
                graph,
                nodes=nodes,
                seed=seed,
                spread=spread,
                node_count=node_count,
                iterations=120,
            )
    elif algorithm_name == LayoutAlgorithm.FORCE_DIRECTED.value:
        positions = _spring_layout_safe(
            graph,
            nodes=nodes,
            seed=seed,
            spread=spread,
            node_count=node_count,
            iterations=300,
        )
    else:
        positions = _spring_layout_safe(
            graph,
            nodes=nodes,
            seed=seed,
            spread=spread,
            node_count=node_count,
            iterations=150,
        )

    for node in nodes:
        coords = positions.get(node.id)
        if coords is None:
            continue
        x_value, y_value = coords
        x_float = float(x_value)
        y_float = float(y_value)
        if not (math.isfinite(x_float) and math.isfinite(y_float)):
            continue
        node.x = x_float
        node.y = y_float

    unpositioned = [node for node in nodes if node.x is None or node.y is None]
    if unpositioned:
        _circular_layout(unpositioned)
