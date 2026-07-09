"""Matplotlib rendering helpers for graph slices."""

from __future__ import annotations

from typing import Any

from .models import GraphRenderConfig, GraphSlice, MatrixSlice, NodeColorMode, enum_value
from .density import assess_graph_slice

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.colors import to_hex
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    nx = None
    Figure = Any
    to_hex = None

PARTY_COLORS = {
    "D": "#2563eb",
    "R": "#dc2626",
    "I": "#7c3aed",
}
DEFAULT_NODE_COLOR = "#64748b"


def _community_colormap() -> Any:
    if not MATPLOTLIB_AVAILABLE or plt is None:
        return None
    return plt.get_cmap("tab20")


class GraphVisualizer:
    """Render graph slices and matrix views with matplotlib."""

    def __init__(self, config: GraphRenderConfig | None = None) -> None:
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "matplotlib and networkx are required for graph visualization. "
                "Install with: pip install congressgov[graph,viz]"
            )
        self.config = config or GraphRenderConfig()

    def _node_color(self, node: Any) -> str:
        mode = enum_value(self.config.node_color_mode)
        community_cmap = _community_colormap()
        if mode == NodeColorMode.COMMUNITY.value:
            if node.community and community_cmap is not None and to_hex is not None:
                index = sum(ord(char) for char in node.community) % 20
                return to_hex(community_cmap(index))
        if mode == NodeColorMode.CENTRALITY.value and node.centrality is not None and community_cmap is not None:
            if to_hex is not None:
                return to_hex(community_cmap(min(max(node.centrality, 0.0), 1.0)))
        return PARTY_COLORS.get(node.party, DEFAULT_NODE_COLOR)

    def _edge_color(self, edge: Any) -> str:
        if edge.cross_party_weight:
            return self.config.cross_party_edge_color
        return self.config.same_party_edge_color

    def _labels_for_nodes(self, graph_slice: GraphSlice, *, label_threshold: float) -> dict[str, str]:
        if not self.config.show_labels:
            return {}
        labels: dict[str, str] = {}
        for node in graph_slice.nodes:
            if node.centrality is None or node.centrality >= label_threshold:
                labels[node.id] = node.label or node.id
        return labels

    def draw_graph(self, graph_slice: GraphSlice) -> Figure:
        """Draw a node-link graph with party/community encoding and weighted edges."""
        assert nx is not None and plt is not None

        node_count = len(graph_slice.nodes)
        edge_count = len(graph_slice.edges)
        if node_count > self.config.max_node_link_nodes or edge_count > self.config.max_node_link_edges:
            raise ValueError(
                f"Graph slice ({node_count:,} nodes, {edge_count:,} edges) exceeds "
                f"GraphRenderConfig limits (max_node_link_nodes="
                f"{self.config.max_node_link_nodes:,}, max_node_link_edges="
                f"{self.config.max_node_link_edges:,}). Increase the limits, "
                "raise min_weight/lower max_edges when building the slice, or use "
                "a matrix/ego view instead of a node-link render."
            )

        assessment = assess_graph_slice(graph_slice)
        # Computed locally (not written to self.config) so a mid-draw failure
        # can't leave the shared config permanently mutated for later calls.
        label_threshold = self.config.label_min_centrality
        if not assessment.node_link_acceptable:
            label_threshold = max(label_threshold, 0.6)

        digraph = nx.DiGraph()
        for node in graph_slice.nodes:
            digraph.add_node(node.id, node=node)
        for edge in graph_slice.edges:
            digraph.add_edge(edge.source, edge.target, edge=edge)

        pos = {
            node.id: (node.x if node.x is not None else 0.0, node.y if node.y is not None else 0.0)
            for node in graph_slice.nodes
        }
        if not any(pos.values()) and digraph.number_of_nodes():
            pos = nx.spring_layout(digraph, seed=42)

        node_colors = [self._node_color(digraph.nodes[node_id]["node"]) for node_id in digraph.nodes]
        node_sizes = [
            120 + 80 * min(max(digraph.nodes[node_id]["node"].centrality or 0.0, 0.0), 1.0)
            for node_id in digraph.nodes
        ]
        edge_colors = [self._edge_color(data["edge"]) for _, _, data in digraph.edges(data=True)]
        edge_widths = [0.5 + 0.8 * data["edge"].weight for _, _, data in digraph.edges(data=True)]

        fig, ax = plt.subplots(figsize=self.config.figsize, dpi=self.config.dpi)
        nx.draw_networkx_edges(
            digraph,
            pos,
            width=edge_widths,
            edge_color=edge_colors,
            alpha=0.55,
            arrows=self.config.show_edge_arrows,
            ax=ax,
        )
        nx.draw_networkx_nodes(digraph, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
        labels = self._labels_for_nodes(graph_slice, label_threshold=label_threshold)
        if labels:
            nx.draw_networkx_labels(digraph, pos, labels=labels, font_size=8, ax=ax)
        ax.set_title(self.config.title or graph_slice.graph_key)
        ax.axis("off")
        fig.tight_layout()
        return fig

    def draw_matrix_heatmap(
        self,
        matrix_slice: MatrixSlice,
        *,
        member_labels: dict[str, str] | None = None,
    ) -> Figure:
        """Draw a sparse adjacency matrix as a heatmap."""
        assert plt is not None

        labels = member_labels or {}
        row_labels = [labels.get(member_id, member_id) for member_id in matrix_slice.rows]
        size = len(matrix_slice.rows)
        grid = [[0 for _ in range(size)] for _ in range(size)]
        row_index = {member_id: index for index, member_id in enumerate(matrix_slice.rows)}

        for cell in matrix_slice.cells:
            row = row_index.get(cell.row)
            column = row_index.get(cell.column)
            if row is None or column is None:
                continue
            grid[row][column] = cell.weight

        fig, ax = plt.subplots(figsize=self.config.figsize, dpi=self.config.dpi)
        image = ax.imshow(grid, cmap="Blues", aspect="auto")
        ax.set_xticks(range(size), row_labels, rotation=90, fontsize=7)
        ax.set_yticks(range(size), row_labels, fontsize=7)
        ax.set_title(self.config.title or f"Adjacency matrix ({matrix_slice.sort})")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Relationship weight")
        fig.tight_layout()
        return fig

    def save_graph(self, graph_slice: GraphSlice, filepath: str, **kwargs: Any) -> None:
        """Render and save a graph slice to an image file."""
        figure = self.draw_graph(graph_slice)
        figure.savefig(filepath, bbox_inches="tight", **kwargs)
        plt.close(figure)

    def save_matrix(self, matrix_slice: MatrixSlice, filepath: str, **kwargs: Any) -> None:
        """Render and save a matrix heatmap to an image file."""
        figure = self.draw_matrix_heatmap(matrix_slice, **kwargs)
        figure.savefig(filepath, bbox_inches="tight")
        plt.close(figure)
