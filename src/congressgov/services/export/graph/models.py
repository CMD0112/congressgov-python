"""Data models for sponsor/cosponsor network graph projections."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Literal

from pydantic import Field

from congressgov.models.base.model import Model


class GraphProjectionType(str, Enum):
    """Supported graph projection modes."""

    SPONSOR_TO_COSPONSOR = "sponsor_to_cosponsor"
    COLLABORATION = "collaboration"


def enum_value(
    value: GraphProjectionType | GraphChamberFilter | LayoutAlgorithm | NodeColorMode | str,
) -> str:
    """Return the string value for enum-backed graph settings."""
    if isinstance(value, (GraphProjectionType, GraphChamberFilter, LayoutAlgorithm, NodeColorMode)):
        return value.value
    return str(value)


class GraphChamberFilter(str, Enum):
    """Chamber filter for graph queries."""

    ALL = "all"
    HOUSE = "house"
    SENATE = "senate"


class LayoutAlgorithm(str, Enum):
    """Supported precomputed layout algorithms."""

    SPRING = "spring"
    FORCE_DIRECTED = "force_directed"
    KAMADA_KAWAI = "kamada_kawai"
    CIRCULAR = "circular"
    SHELL_PARTY = "shell_party"


class NodeColorMode(str, Enum):
    """Node coloring strategies for rendering."""

    PARTY = "party"
    COMMUNITY = "community"
    CENTRALITY = "centrality"


class GraphExploreConfig(Model):
    """Filter and projection settings for graph construction."""

    congress: int
    include_all_members: bool = False
    projection: GraphProjectionType = GraphProjectionType.SPONSOR_TO_COSPONSOR
    bill_type: str | None = None
    chamber: GraphChamberFilter = GraphChamberFilter.ALL
    policy_area: str | None = None
    min_weight: int = 1
    max_edges: int = 3000
    cross_party_only: bool = False
    original_only: bool = False
    include_withdrawn: bool = False
    weighting: Literal["raw_count"] = "raw_count"
    layout_algorithm: LayoutAlgorithm = LayoutAlgorithm.SPRING
    node_color_mode: NodeColorMode = NodeColorMode.PARTY
    compute_communities: bool = True
    compute_advanced_metrics: bool = True
    advanced_metrics_max_nodes: int = Field(default=400, ge=1)


class GraphViewMode(str, Enum):
    """Recommended primary view for a graph slice."""

    OVERVIEW = "overview"
    MATRIX = "matrix"
    EGO = "ego"
    TABLES = "tables"


class GraphSizeTier(str, Enum):
    """Size/density tiers aligned with the network graph design thresholds."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


class GraphDensityAssessment(Model):
    """Assessment of whether a graph slice is suitable for node-link rendering."""

    node_count: int
    edge_count: int
    edge_count_before_limit: int
    avg_degree: float
    density: float
    tier: GraphSizeTier
    recommended_view: GraphViewMode
    node_link_acceptable: bool
    interactive_html_acceptable: bool
    warnings: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class GraphRenderConfig(Model):
    """Static or notebook rendering options."""

    node_color_mode: NodeColorMode = NodeColorMode.PARTY
    label_min_centrality: float = 0.35
    show_labels: bool = True
    show_edge_arrows: bool = False
    cross_party_edge_color: str = "#9333ea"
    same_party_edge_color: str = "#94a3b8"
    figsize: tuple[float, float] = (10.0, 8.0)
    title: str | None = None
    dpi: int = 120
    max_node_link_nodes: int = Field(default=750, ge=1)
    max_node_link_edges: int = Field(default=5000, ge=1)
    max_interactive_edges: int = Field(default=10000, ge=1)
    simplify_hover_for_large_graphs: bool = True


class EgoNetworkConfig(GraphExploreConfig):
    """Settings for ego-network subgraph extraction."""

    direction: Literal["outgoing", "incoming", "both", "reciprocal"] = "both"
    # 1-3 hops, matching the HTML explorer's ego view (docs/guide/NETWORK_GRAPH.md).
    depth: int = Field(default=1, ge=1, le=3)
    max_neighbors: int = Field(default=100, ge=1)


class SponsorshipEvent(Model):
    """One sponsor/cosponsor relationship on one bill (raw event layer)."""

    event_id: str
    bill_id: str
    congress: int
    bill_type: str
    bill_number: int
    bill_title: str | None = None
    origin_chamber: str | None = None
    policy_area: str | None = None
    introduced_date: date | None = None
    latest_action_date: date | None = None
    latest_action_text: str | None = None
    sponsor_bioguide_id: str
    sponsor_name: str | None = None
    sponsor_party: str | None = None
    sponsor_state: str | None = None
    sponsor_district: int | None = None
    cosponsor_bioguide_id: str
    cosponsor_name: str | None = None
    cosponsor_party: str | None = None
    cosponsor_state: str | None = None
    cosponsor_district: int | None = None
    sponsorship_date: date | None = None
    is_original_cosponsor: bool | None = None
    sponsorship_withdrawn_date: date | None = None
    is_active: bool = True


class GraphMemberNode(Model):
    """Member node metadata for graph rendering."""

    id: str
    label: str | None = None
    party: str | None = None
    state: str | None = None
    district: str | None = None
    chamber: str | None = None
    size: float = 1.0
    centrality: float | None = None
    betweenness: float | None = None
    pagerank: float | None = None
    community: str | None = None
    x: float | None = None
    y: float | None = None
    weighted_in_degree: float = 0.0
    weighted_out_degree: float = 0.0
    cross_party_ratio: float | None = None


class GraphEdge(Model):
    """Aggregated edge between two members."""

    id: str
    source: str
    target: str
    weight: int
    original_weight: int = 0
    late_weight: int = 0
    unknown_original_weight: int = 0
    withdrawn_weight: int = 0
    active_weight: int = 0
    cross_party_weight: int = 0
    first_date: date | None = None
    last_date: date | None = None
    bill_count: int = 0


class GraphLimits(Model):
    """Truncation metadata returned with graph slices."""

    max_edges: int
    edge_count_before_limit: int
    was_truncated: bool
    shown_edges: int
    recommended_actions: list[str] = Field(default_factory=list)


class BillIngestResult(Model):
    """Outcome of adding one bill to a persistent congress graph."""

    bill_id: str
    added: bool
    event_count: int = 0
    skipped_reason: str | None = None


class CongressGraphSnapshot(Model):
    """Serialized congress graph dataset (member roster + sponsorship events)."""

    schema_version: int = 1
    congress: int
    members: dict[str, GraphMemberNode] = Field(default_factory=dict)
    events: list[SponsorshipEvent] = Field(default_factory=list)
    bill_ids: list[str] = Field(default_factory=list)
    provenance: dict[str, object] | None = Field(
        default=None,
        description="Optional lineage metadata (source store, request keys, built_at).",
    )


class GraphSlice(Model):
    """Filtered graph projection ready for rendering or API responses."""

    graph_key: str
    layout_key: str | None = None
    projection: GraphProjectionType
    nodes: list[GraphMemberNode]
    edges: list[GraphEdge]
    limits: GraphLimits


class MatrixCell(Model):
    """Sparse matrix cell for adjacency-matrix views."""

    row: str
    column: str
    weight: int


class MatrixSlice(Model):
    """Sparse adjacency matrix representation."""

    graph_key: str
    rows: list[str]
    columns: list[str]
    cells: list[MatrixCell]
    sort: str = "party"


class EdgeBillRecord(Model):
    """Bill-level evidence for an aggregated edge."""

    bill_id: str
    title: str | None = None
    introduced_date: date | None = None
    policy_area: str | None = None
    sponsorship_date: date | None = None
    is_original_cosponsor: bool | None = None
    sponsorship_withdrawn_date: date | None = None
    latest_action_date: date | None = None
    latest_action_text: str | None = None


class EdgeEvidence(Model):
    """Bill evidence behind an aggregated member-pair edge."""

    source_id: str
    target_id: str
    weight: int
    original_count: int
    late_count: int
    unknown_original_count: int
    withdrawn_count: int
    cross_party: bool
    policy_split: dict[str, int] = Field(default_factory=dict)
    bills: list[EdgeBillRecord] = Field(default_factory=list)


class MemberEdgeSummary(Model):
    """Summary of one ranked relationship for a member."""

    member_id: str
    label: str | None = None
    weight: int
    cross_party_weight: int = 0


class MemberNetworkSummary(Model):
    """Network summary for a single member."""

    member_id: str
    label: str | None = None
    party: str | None = None
    state: str | None = None
    district: str | None = None
    chamber: str | None = None
    sponsored_bill_count: int = 0
    cosponsored_bill_count: int = 0
    top_outgoing: list[MemberEdgeSummary] = Field(default_factory=list)
    top_incoming: list[MemberEdgeSummary] = Field(default_factory=list)
    cross_party_ratio: float | None = None
    top_policy_areas: dict[str, int] = Field(default_factory=dict)
    original_cosponsor_count: int = 0
    withdrawn_count: int = 0


class RankedRelationship(Model):
    """Ranked member-pair relationship for table views."""

    source_id: str
    target_id: str
    source_label: str | None = None
    target_label: str | None = None
    weight: int
    cross_party_weight: int = 0
    bill_count: int = 0


def model_to_dict(value: Any) -> Any:
    """Serialize graph models to JSON-compatible dictionaries."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [model_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: model_to_dict(item) for key, item in value.items()}
    return value
