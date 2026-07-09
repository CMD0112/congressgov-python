"""Shared NetworkX availability flag and base graph builder.

``metrics.py`` (community/centrality), ``layout.py`` (positioning), and
``render.py`` (GraphML/GEXF export) each need a NetworkX graph built from a
graph slice's nodes/edges. This module centralizes the minimal
nodes-plus-weighted-edges construction so those three near-duplicate
implementations share one source of truth.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import GraphEdge, GraphMemberNode

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


def build_weighted_graph(
    nodes: list[GraphMemberNode],
    edges: list[GraphEdge],
    *,
    directed: bool = True,
) -> Any:
    """Build a minimal NetworkX graph (node ids + weighted edges) or ``None``.

    Callers needing richer node/edge attributes (e.g. render.py's GraphML/GEXF
    export) should build on top of this via ``nx.set_node_attributes`` /
    ``nx.set_edge_attributes`` rather than reimplementing the add_node/add_edge
    loop.
    """
    if not NETWORKX_AVAILABLE or nx is None:
        return None
    graph: Any = nx.DiGraph() if directed else nx.Graph()
    for node in nodes:
        graph.add_node(node.id)
    for edge in edges:
        graph.add_edge(edge.source, edge.target, weight=edge.weight)
    return graph
