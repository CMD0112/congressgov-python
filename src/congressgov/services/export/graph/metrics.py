"""Network metrics and community detection for graph slices."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import GraphExploreConfig, enum_value
from .networkx_support import NETWORKX_AVAILABLE, build_weighted_graph

if TYPE_CHECKING:
    from .models import GraphEdge, GraphMemberNode

try:
    import networkx as nx
except ImportError:
    nx = None


def build_layout_key(config: GraphExploreConfig) -> str:
    """Build a deterministic layout cache key."""
    min_weight_bucket = config.min_weight if config.min_weight >= 2 else 1
    return (
        f"{enum_value(config.projection)}|{config.congress}|"
        f"layout={enum_value(config.layout_algorithm)}|min_weight_bucket={min_weight_bucket}"
    )


def _build_networkx_graph(
    nodes: list[GraphMemberNode],
    edges: list[GraphEdge],
    *,
    directed: bool = True,
) -> Any:
    return build_weighted_graph(nodes, edges, directed=directed)


def assign_communities(nodes: list[GraphMemberNode], edges: list[GraphEdge]) -> None:
    """Detect communities and assign ``community`` ids to nodes."""
    if not NETWORKX_AVAILABLE or nx is None or not nodes:
        return

    undirected = _build_networkx_graph(nodes, edges, directed=False)
    if undirected is None or undirected.number_of_edges() == 0:
        for node in nodes:
            node.community = "c0"
        return

    try:
        communities = nx.community.greedy_modularity_communities(undirected, weight="weight")
    except Exception:
        for node in nodes:
            node.community = "c0"
        return

    node_lookup = {node.id: node for node in nodes}
    for index, community_nodes in enumerate(communities):
        community_id = f"c{index}"
        for node_id in community_nodes:
            node = node_lookup.get(node_id)
            if node is not None:
                node.community = community_id


def assign_advanced_metrics(
    nodes: list[GraphMemberNode],
    edges: list[GraphEdge],
    *,
    max_nodes: int = 400,
) -> None:
    """Compute betweenness and PageRank for small graphs."""
    if not NETWORKX_AVAILABLE or nx is None or len(nodes) > max_nodes:
        return

    directed = _build_networkx_graph(nodes, edges, directed=True)
    if directed is None or directed.number_of_edges() == 0:
        return

    try:
        betweenness = nx.betweenness_centrality(directed, weight="weight")
        pagerank = nx.pagerank(directed, weight="weight")
    except Exception:
        return

    max_betweenness = max(betweenness.values(), default=0.0)
    max_pagerank = max(pagerank.values(), default=0.0)
    for node in nodes:
        node.betweenness = betweenness.get(node.id, 0.0)
        node.pagerank = pagerank.get(node.id, 0.0)
        if max_betweenness:
            node.betweenness = node.betweenness / max_betweenness
        if max_pagerank:
            node.pagerank = node.pagerank / max_pagerank


def enrich_graph_metrics(
    nodes: list[GraphMemberNode],
    edges: list[GraphEdge],
    config: GraphExploreConfig,
) -> None:
    """Apply community detection and optional advanced metrics."""
    if config.compute_communities:
        assign_communities(nodes, edges)
    if config.compute_advanced_metrics:
        assign_advanced_metrics(nodes, edges, max_nodes=config.advanced_metrics_max_nodes)
