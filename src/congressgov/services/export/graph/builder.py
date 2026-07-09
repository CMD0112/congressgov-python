"""Build graph projections and filtered slices from sponsorship events."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .layout import assign_layout_positions
from .metrics import build_layout_key, enrich_graph_metrics
from .member_labels import (
    MemberLabelResolver,
    finalize_graph_member_label,
    label_quality_score,
)
from .models import (
    EdgeBillRecord,
    EdgeEvidence,
    EgoNetworkConfig,
    GraphChamberFilter,
    GraphEdge,
    GraphExploreConfig,
    GraphLimits,
    GraphMemberNode,
    GraphProjectionType,
    GraphSlice,
    MatrixCell,
    MatrixSlice,
    MemberEdgeSummary,
    MemberNetworkSummary,
    RankedRelationship,
    SponsorshipEvent,
    enum_value,
)
from .sources import normalize_chamber


@dataclass
class _EdgeAggregate:
    source: str
    target: str
    weight_total: int = 0
    weight_active: int = 0
    weight_original: int = 0
    weight_late: int = 0
    weight_unknown_original: int = 0
    weight_withdrawn: int = 0
    weight_cross_party: int = 0
    first_relationship_date: date | None = None
    last_relationship_date: date | None = None
    bill_ids: set[str] | None = None

    def __post_init__(self) -> None:
        if self.bill_ids is None:
            self.bill_ids = set()


def build_projection_key(config: GraphExploreConfig) -> str:
    """Build a deterministic projection cache key."""
    withdrawn = "withdrawn_included" if config.include_withdrawn else "withdrawn_excluded"
    original = "original_only" if config.original_only else "original_included"
    chamber = enum_value(config.chamber)
    policy = config.policy_area or "all"
    bill_type = config.bill_type or "all"
    roster = "full_roster" if config.include_all_members else "edge_members"
    return (
        f"{enum_value(config.projection)}|{config.congress}|{bill_type}|{chamber}|"
        f"{policy}|{withdrawn}|{original}|{config.weighting}|{roster}"
    )


def filter_events(events: Iterable[SponsorshipEvent], config: GraphExploreConfig) -> list[SponsorshipEvent]:
    """Apply graph filter settings to raw sponsorship events."""
    filtered: list[SponsorshipEvent] = []
    for event in events:
        if event.congress != config.congress:
            continue
        if config.bill_type and event.bill_type.lower() != config.bill_type.lower():
            continue
        if config.policy_area and event.policy_area != config.policy_area:
            continue
        if enum_value(config.chamber) != GraphChamberFilter.ALL.value:
            chamber = normalize_chamber(event.origin_chamber)
            if chamber != enum_value(config.chamber):
                continue
        if not config.include_withdrawn and not event.is_active:
            continue
        if config.original_only and not event.is_original_cosponsor:
            continue
        if config.cross_party_only and event.sponsor_party == event.cosponsor_party:
            continue
        filtered.append(event)
    return filtered


def _update_date_bounds(current: date | None, candidate: date | None, *, earliest: bool) -> date | None:
    if candidate is None:
        return current
    if current is None:
        return candidate
    return min(current, candidate) if earliest else max(current, candidate)


def _aggregate_directed_edges(events: Iterable[SponsorshipEvent]) -> dict[tuple[str, str], _EdgeAggregate]:
    aggregates: dict[tuple[str, str], _EdgeAggregate] = {}
    for event in events:
        key = (event.sponsor_bioguide_id, event.cosponsor_bioguide_id)
        aggregate = aggregates.get(key)
        if aggregate is None:
            aggregate = _EdgeAggregate(source=key[0], target=key[1])
            aggregates[key] = aggregate

        aggregate.weight_total += 1
        if event.is_active:
            aggregate.weight_active += 1
        # `is_original_cosponsor=None` means "unknown", not "late" -- treating
        # it as late (bool(None) is False) silently miscounted unresolved data.
        if event.is_original_cosponsor is None:
            aggregate.weight_unknown_original += 1
        elif event.is_original_cosponsor:
            aggregate.weight_original += 1
        else:
            aggregate.weight_late += 1
        if event.sponsorship_withdrawn_date is not None:
            aggregate.weight_withdrawn += 1
        if event.sponsor_party and event.cosponsor_party and event.sponsor_party != event.cosponsor_party:
            aggregate.weight_cross_party += 1
        aggregate.first_relationship_date = _update_date_bounds(
            aggregate.first_relationship_date,
            event.sponsorship_date,
            earliest=True,
        )
        aggregate.last_relationship_date = _update_date_bounds(
            aggregate.last_relationship_date,
            event.sponsorship_date,
            earliest=False,
        )
        if aggregate.bill_ids is not None:
            aggregate.bill_ids.add(event.bill_id)
    return aggregates


def _aggregate_collaboration_edges(events: Iterable[SponsorshipEvent]) -> dict[tuple[str, str], _EdgeAggregate]:
    directed = _aggregate_directed_edges(events)
    collaboration: dict[tuple[str, str], _EdgeAggregate] = {}

    for (source, target), aggregate in directed.items():
        pair = tuple(sorted((source, target)))
        coll = collaboration.get(pair)
        if coll is None:
            coll = _EdgeAggregate(source=pair[0], target=pair[1])
            collaboration[pair] = coll

        coll.weight_total += aggregate.weight_total
        coll.weight_active += aggregate.weight_active
        coll.weight_original += aggregate.weight_original
        coll.weight_late += aggregate.weight_late
        coll.weight_unknown_original += aggregate.weight_unknown_original
        coll.weight_withdrawn += aggregate.weight_withdrawn
        coll.weight_cross_party += aggregate.weight_cross_party
        coll.first_relationship_date = _update_date_bounds(
            coll.first_relationship_date,
            aggregate.first_relationship_date,
            earliest=True,
        )
        coll.last_relationship_date = _update_date_bounds(
            coll.last_relationship_date,
            aggregate.last_relationship_date,
            earliest=False,
        )
        if coll.bill_ids is not None and aggregate.bill_ids is not None:
            coll.bill_ids.update(aggregate.bill_ids)

    return collaboration


def _aggregate_to_graph_edges(
    aggregates: dict[tuple[str, str], _EdgeAggregate],
    *,
    projection: GraphProjectionType | str,
) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    for (source, target), aggregate in aggregates.items():
        edge_id = f"{source}__{target}"
        edges.append(
            GraphEdge(
                id=edge_id,
                source=source,
                target=target,
                weight=aggregate.weight_active if aggregate.weight_active else aggregate.weight_total,
                original_weight=aggregate.weight_original,
                late_weight=aggregate.weight_late,
                unknown_original_weight=aggregate.weight_unknown_original,
                withdrawn_weight=aggregate.weight_withdrawn,
                active_weight=aggregate.weight_active,
                cross_party_weight=aggregate.weight_cross_party,
                first_date=aggregate.first_relationship_date,
                last_date=aggregate.last_relationship_date,
                bill_count=len(aggregate.bill_ids or set()),
            )
        )
    edges.sort(key=lambda edge: edge.weight, reverse=True)
    return edges


def _member_metadata(
    events: Iterable[SponsorshipEvent],
    *,
    member_resolver: MemberLabelResolver | None = None,
) -> dict[str, GraphMemberNode]:
    members: dict[str, GraphMemberNode] = {}

    def upsert(
        bioguide_id: str,
        *,
        label: str | None,
        party: str | None,
        state: str | None,
        district: int | None,
        origin_chamber: str | None = None,
    ) -> None:
        node = members.get(bioguide_id)
        if node is None:
            inferred_chamber = "house" if district is not None else normalize_chamber(origin_chamber)
            members[bioguide_id] = GraphMemberNode(
                id=bioguide_id,
                label=label or bioguide_id,
                party=party,
                state=state,
                district=str(district) if district is not None else None,
                chamber=inferred_chamber,
            )
        else:
            if label and (node.label == bioguide_id or not node.label):
                node.label = label
            node.party = node.party or party
            node.state = node.state or state
            if district is not None and node.district is None:
                node.district = str(district)
            if district is not None:
                node.chamber = "house"
            elif origin_chamber and not node.chamber:
                node.chamber = normalize_chamber(origin_chamber)

    for event in events:
        upsert(
            event.sponsor_bioguide_id,
            label=event.sponsor_name,
            party=event.sponsor_party,
            state=event.sponsor_state,
            district=event.sponsor_district,
            origin_chamber=event.origin_chamber,
        )
        upsert(
            event.cosponsor_bioguide_id,
            label=event.cosponsor_name,
            party=event.cosponsor_party,
            state=event.cosponsor_state,
            district=event.cosponsor_district,
            origin_chamber=event.origin_chamber,
        )

    for node in members.values():
        node.label = finalize_graph_member_label(node)

    if member_resolver is not None:
        member_resolver.enrich_members(members)
    return members


def _merge_member_nodes(
    base: GraphMemberNode,
    update: GraphMemberNode,
) -> GraphMemberNode:
    """Merge event-derived metadata into a seeded member node."""
    if update.label and label_quality_score(update.label, member_id=base.id) > label_quality_score(
        base.label, member_id=base.id
    ):
        base.label = update.label
    base.party = base.party or update.party
    base.state = base.state or update.state
    if update.district is not None and base.district is None:
        base.district = update.district
    if update.chamber and not base.chamber:
        base.chamber = update.chamber
    elif update.district is not None:
        base.chamber = "house"
    base.label = finalize_graph_member_label(base)
    return base


def _resolve_graph_nodes(
    event_members: dict[str, GraphMemberNode],
    shown_edges: list[GraphEdge],
    config: GraphExploreConfig,
    *,
    member_registry: dict[str, GraphMemberNode] | None = None,
) -> list[GraphMemberNode]:
    """Choose visible nodes for a graph slice."""
    if config.include_all_members and member_registry:
        merged = {
            member_id: node.model_copy(deep=True)
            for member_id, node in member_registry.items()
        }
        for member_id, event_node in event_members.items():
            existing = merged.get(member_id)
            if existing is None:
                merged[member_id] = event_node
            else:
                _merge_member_nodes(existing, event_node)
        return [merged[member_id] for member_id in sorted(merged)]

    visible_member_ids: set[str] = set()
    for edge in shown_edges:
        visible_member_ids.add(edge.source)
        visible_member_ids.add(edge.target)
    return [
        event_members[member_id]
        for member_id in sorted(visible_member_ids)
        if member_id in event_members
    ]


def _apply_edge_limits(edges: list[GraphEdge], config: GraphExploreConfig) -> tuple[list[GraphEdge], GraphLimits]:
    eligible = [edge for edge in edges if edge.weight >= config.min_weight]
    before_limit = len(eligible)
    truncated = before_limit > config.max_edges
    shown = eligible[: config.max_edges]
    recommendations: list[str] = []
    if truncated:
        recommendations = [
            "Increase minimum edge weight",
            "Filter by policy area",
            "Switch to matrix view",
            "Open ego network for a member",
        ]
    return shown, GraphLimits(
        max_edges=config.max_edges,
        edge_count_before_limit=before_limit,
        was_truncated=truncated,
        shown_edges=len(shown),
        recommended_actions=recommendations,
    )


def _compute_node_metrics(nodes: dict[str, GraphMemberNode], edges: list[GraphEdge]) -> None:
    in_degree: Counter[str] = Counter()
    out_degree: Counter[str] = Counter()
    cross_party_events: Counter[str] = Counter()
    total_events: Counter[str] = Counter()

    for edge in edges:
        out_degree[edge.source] += edge.weight
        in_degree[edge.target] += edge.weight
        total_events[edge.source] += edge.weight
        total_events[edge.target] += edge.weight
        if edge.cross_party_weight:
            cross_party_events[edge.source] += edge.cross_party_weight
            cross_party_events[edge.target] += edge.cross_party_weight

    max_degree = 0.0
    for node_id, node in nodes.items():
        weighted_out = float(out_degree[node_id])
        weighted_in = float(in_degree[node_id])
        node.weighted_out_degree = weighted_out
        node.weighted_in_degree = weighted_in
        node.size = max(weighted_in, weighted_out, 1.0)
        max_degree = max(max_degree, node.size)
        total = total_events[node_id]
        if total:
            node.cross_party_ratio = cross_party_events[node_id] / total

    if max_degree <= 0:
        return

    for node in nodes.values():
        node.centrality = node.size / max_degree


def build_graph_slice(
    events: Iterable[SponsorshipEvent],
    config: GraphExploreConfig,
    *,
    member_registry: dict[str, GraphMemberNode] | None = None,
    member_resolver: MemberLabelResolver | None = None,
) -> GraphSlice:
    """Build a filtered graph slice from raw sponsorship events."""
    filtered = filter_events(events, config)
    if enum_value(config.projection) == GraphProjectionType.COLLABORATION.value:
        aggregates = _aggregate_collaboration_edges(filtered)
    else:
        aggregates = _aggregate_directed_edges(filtered)

    edges = _aggregate_to_graph_edges(aggregates, projection=config.projection)
    shown_edges, limits = _apply_edge_limits(edges, config)
    if member_registry and member_resolver is not None:
        member_resolver.seed_registry(member_registry)
    members = _member_metadata(filtered, member_resolver=member_resolver)

    nodes = _resolve_graph_nodes(
        members,
        shown_edges,
        config,
        member_registry=member_registry,
    )
    if member_resolver is not None and config.include_all_members and member_registry is not None:
        member_resolver.enrich_unresolved(member_registry)
        node_lookup = {node.id: node for node in nodes}
        for member_id, registry_node in member_registry.items():
            graph_node = node_lookup.get(member_id)
            if graph_node is None:
                continue
            if label_quality_score(registry_node.label, member_id=member_id) > label_quality_score(
                graph_node.label, member_id=member_id
            ):
                graph_node.label = registry_node.label
                graph_node.party = graph_node.party or registry_node.party
                graph_node.state = graph_node.state or registry_node.state
                graph_node.district = graph_node.district or registry_node.district
                graph_node.chamber = graph_node.chamber or registry_node.chamber
    node_lookup = {node.id: node for node in nodes}
    _compute_node_metrics(node_lookup, shown_edges)
    enrich_graph_metrics(nodes, shown_edges, config)
    layout_key = build_layout_key(config)
    assign_layout_positions(
        nodes,
        shown_edges,
        algorithm=config.layout_algorithm,
        layout_key=layout_key,
    )

    return GraphSlice(
        graph_key=build_projection_key(config),
        layout_key=layout_key,
        projection=config.projection,
        nodes=nodes,
        edges=shown_edges,
        limits=limits,
    )


def build_ego_graph(events: Iterable[SponsorshipEvent], member_id: str, config: EgoNetworkConfig) -> GraphSlice:
    """Build an ego network around one member."""
    filtered = filter_events(events, config)
    directed = _aggregate_directed_edges(filtered)
    selected_pairs: set[tuple[str, str]] = set()

    if config.direction in {"outgoing", "both", "reciprocal"}:
        for source, target in directed:
            if source == member_id:
                selected_pairs.add((source, target))
    if config.direction in {"incoming", "both", "reciprocal"}:
        for source, target in directed:
            if target == member_id:
                selected_pairs.add((source, target))
    if config.direction == "reciprocal":
        selected_pairs = {
            pair for pair in selected_pairs if (pair[1], pair[0]) in directed
        }

    if config.depth >= 2:
        # Genuine hop-by-hop BFS expansion (mirrors the HTML explorer's
        # egoHopDistances()), rather than a single fixed expansion that
        # silently behaved the same for every depth >= 2.
        frontier = {target for source, target in selected_pairs} | {source for source, _ in selected_pairs}
        visited = frontier | {member_id}
        for _ in range(config.depth - 1):
            next_frontier: set[str] = set()
            for source, target in directed:
                if source in frontier or target in frontier:
                    selected_pairs.add((source, target))
                    if source in frontier and target not in visited:
                        next_frontier.add(target)
                    if target in frontier and source not in visited:
                        next_frontier.add(source)
            if not next_frontier:
                break
            visited |= next_frontier
            frontier = next_frontier

    if enum_value(config.projection) == GraphProjectionType.COLLABORATION.value:
        # Collaboration edges are undirected: rank/limit by the combined weight
        # across both directions of the same relationship and keep both
        # directions together. Ranking directed pairs independently could
        # spend two neighbor slots on one relationship, or truncate only one
        # direction and understate the resulting collaboration edge's weight.
        combined_weight: dict[tuple[str, str], int] = {}
        for pair in selected_pairs:
            undirected_key = tuple(sorted(pair))
            aggregate = directed[pair]
            combined_weight[undirected_key] = combined_weight.get(undirected_key, 0) + (
                aggregate.weight_active or aggregate.weight_total
            )
        ranked_undirected = set(
            sorted(combined_weight, key=lambda key: combined_weight[key], reverse=True)[
                : config.max_neighbors
            ]
        )
        ranked_pairs = {pair for pair in selected_pairs if tuple(sorted(pair)) in ranked_undirected}
    else:
        ranked_pairs = set(
            sorted(
                selected_pairs,
                key=lambda pair: directed[pair].weight_active or directed[pair].weight_total,
                reverse=True,
            )[: config.max_neighbors]
        )
    ego_events = [
        event
        for event in filtered
        if (event.sponsor_bioguide_id, event.cosponsor_bioguide_id) in ranked_pairs
    ]
    ego_config = GraphExploreConfig(
        congress=config.congress,
        projection=config.projection,
        bill_type=config.bill_type,
        chamber=config.chamber,
        policy_area=config.policy_area,
        min_weight=1,
        max_edges=config.max_edges,
        cross_party_only=config.cross_party_only,
        original_only=config.original_only,
        include_withdrawn=config.include_withdrawn,
        weighting=config.weighting,
    )
    return build_graph_slice(ego_events, ego_config)


def build_matrix(events: Iterable[SponsorshipEvent], config: GraphExploreConfig, *, sort: str = "party") -> MatrixSlice:
    """Build a sparse adjacency matrix from sponsorship events."""
    graph = build_graph_slice(
        events,
        GraphExploreConfig(
            congress=config.congress,
            projection=config.projection,
            bill_type=config.bill_type,
            chamber=config.chamber,
            policy_area=config.policy_area,
            min_weight=config.min_weight,
            max_edges=max(config.max_edges, 100_000),
            cross_party_only=config.cross_party_only,
            original_only=config.original_only,
            include_withdrawn=config.include_withdrawn,
            weighting=config.weighting,
        ),
    )
    member_lookup = {node.id: node for node in graph.nodes}
    member_ids = list(member_lookup)

    if sort == "state":
        member_ids.sort(key=lambda member_id: (member_lookup[member_id].state or "", member_lookup[member_id].label or ""))
    elif sort == "centrality":
        member_ids.sort(key=lambda member_id: member_lookup[member_id].centrality or 0.0, reverse=True)
    else:
        member_ids.sort(
            key=lambda member_id: (
                member_lookup[member_id].party or "",
                member_lookup[member_id].state or "",
                member_lookup[member_id].label or member_id,
            )
        )

    cells = [
        MatrixCell(row=edge.source, column=edge.target, weight=edge.weight)
        for edge in graph.edges
    ]
    return MatrixSlice(
        graph_key=graph.graph_key,
        rows=member_ids,
        columns=member_ids,
        cells=cells,
        sort=sort,
    )


def get_edge_evidence(
    events: Iterable[SponsorshipEvent],
    source_id: str,
    target_id: str,
    config: GraphExploreConfig,
) -> EdgeEvidence:
    """Return bill-level evidence for an aggregated edge."""
    filtered = filter_events(events, config)
    if enum_value(config.projection) == GraphProjectionType.COLLABORATION.value:
        # Collaboration edges are undirected (source/target are a sorted pair,
        # not necessarily the sponsor/cosponsor roles), so evidence must include
        # events in either direction between the two members.
        pair = {source_id, target_id}
        matching = [
            event
            for event in filtered
            if {event.sponsor_bioguide_id, event.cosponsor_bioguide_id} == pair
        ]
    else:
        matching = [
            event
            for event in filtered
            if event.sponsor_bioguide_id == source_id and event.cosponsor_bioguide_id == target_id
        ]
    policy_split: Counter[str] = Counter()
    bills: list[EdgeBillRecord] = []
    original_count = 0
    late_count = 0
    unknown_original_count = 0
    withdrawn_count = 0

    for event in matching:
        if event.is_original_cosponsor is None:
            unknown_original_count += 1
        elif event.is_original_cosponsor:
            original_count += 1
        else:
            late_count += 1
        if event.sponsorship_withdrawn_date is not None:
            withdrawn_count += 1
        if event.policy_area:
            policy_split[event.policy_area] += 1
        bills.append(
            EdgeBillRecord(
                bill_id=event.bill_id,
                title=event.bill_title,
                introduced_date=event.introduced_date,
                policy_area=event.policy_area,
                sponsorship_date=event.sponsorship_date,
                is_original_cosponsor=event.is_original_cosponsor,
                sponsorship_withdrawn_date=event.sponsorship_withdrawn_date,
                latest_action_date=event.latest_action_date,
                latest_action_text=event.latest_action_text,
            )
        )

    cross_party = any(
        event.sponsor_party and event.cosponsor_party and event.sponsor_party != event.cosponsor_party
        for event in matching
    )
    active_count = sum(1 for event in matching if event.is_active)
    return EdgeEvidence(
        source_id=source_id,
        target_id=target_id,
        weight=active_count or len(matching),
        original_count=original_count,
        late_count=late_count,
        unknown_original_count=unknown_original_count,
        withdrawn_count=withdrawn_count,
        cross_party=cross_party,
        policy_split=dict(policy_split),
        bills=bills,
    )


def build_member_summary(
    events: Iterable[SponsorshipEvent],
    member_id: str,
    config: GraphExploreConfig,
    *,
    top_n: int = 10,
) -> MemberNetworkSummary:
    """Build a member-centric network summary."""
    filtered = filter_events(events, config)
    members = _member_metadata(filtered)
    member = members.get(
        member_id,
        GraphMemberNode(id=member_id, label=member_id),
    )
    directed = _aggregate_directed_edges(filtered)

    sponsored_bills = {event.bill_id for event in filtered if event.sponsor_bioguide_id == member_id}
    cosponsored_bills = {event.bill_id for event in filtered if event.cosponsor_bioguide_id == member_id}
    outgoing = sorted(
        (
            MemberEdgeSummary(
                member_id=target,
                label=members.get(target, GraphMemberNode(id=target)).label,
                weight=aggregate.weight_active or aggregate.weight_total,
                cross_party_weight=aggregate.weight_cross_party,
            )
            for (source, target), aggregate in directed.items()
            if source == member_id
        ),
        key=lambda item: item.weight,
        reverse=True,
    )[:top_n]
    incoming = sorted(
        (
            MemberEdgeSummary(
                member_id=source,
                label=members.get(source, GraphMemberNode(id=source)).label,
                weight=aggregate.weight_active or aggregate.weight_total,
                cross_party_weight=aggregate.weight_cross_party,
            )
            for (source, target), aggregate in directed.items()
            if target == member_id
        ),
        key=lambda item: item.weight,
        reverse=True,
    )[:top_n]

    member_events = [event for event in filtered if member_id in {event.sponsor_bioguide_id, event.cosponsor_bioguide_id}]
    policy_areas: Counter[str] = Counter()
    original_count = 0
    withdrawn_count = 0
    cross_party_count = 0
    for event in member_events:
        if event.policy_area:
            policy_areas[event.policy_area] += 1
        if event.is_original_cosponsor:
            original_count += 1
        if event.sponsorship_withdrawn_date is not None:
            withdrawn_count += 1
        if event.sponsor_party and event.cosponsor_party and event.sponsor_party != event.cosponsor_party:
            cross_party_count += 1

    return MemberNetworkSummary(
        member_id=member_id,
        label=member.label,
        party=member.party,
        state=member.state,
        district=member.district,
        chamber=member.chamber,
        sponsored_bill_count=len(sponsored_bills),
        cosponsored_bill_count=len(cosponsored_bills),
        top_outgoing=outgoing,
        top_incoming=incoming,
        cross_party_ratio=(cross_party_count / len(member_events)) if member_events else None,
        top_policy_areas=dict(policy_areas.most_common(top_n)),
        original_cosponsor_count=original_count,
        withdrawn_count=withdrawn_count,
    )


def rank_relationships(events: Iterable[SponsorshipEvent], config: GraphExploreConfig, *, top_n: int = 50) -> list[RankedRelationship]:
    """Return ranked member-pair relationships for table views."""
    filtered = filter_events(events, config)
    aggregates = (
        _aggregate_collaboration_edges(filtered)
        if enum_value(config.projection) == GraphProjectionType.COLLABORATION.value
        else _aggregate_directed_edges(filtered)
    )
    members = _member_metadata(filtered)
    ranked: list[RankedRelationship] = []
    for (source, target), aggregate in aggregates.items():
        weight = aggregate.weight_active or aggregate.weight_total
        if weight < config.min_weight:
            continue
        ranked.append(
            RankedRelationship(
                source_id=source,
                target_id=target,
                source_label=members.get(source, GraphMemberNode(id=source)).label,
                target_label=members.get(target, GraphMemberNode(id=target)).label,
                weight=weight,
                cross_party_weight=aggregate.weight_cross_party,
                bill_count=len(aggregate.bill_ids or set()),
            )
        )
    ranked.sort(key=lambda item: item.weight, reverse=True)
    return ranked[:top_n]
