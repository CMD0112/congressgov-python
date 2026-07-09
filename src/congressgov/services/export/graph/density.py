"""Graph density assessment and render strategy recommendations."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any

from .models import GraphDensityAssessment, GraphExploreConfig, GraphRenderConfig, GraphSizeTier, GraphSlice, GraphViewMode
from .render import graph_slice_to_sigma_payload


def _tier_for_counts(node_count: int, edge_count: int) -> GraphSizeTier:
    if node_count > 2000 or edge_count > 15000:
        return GraphSizeTier.VERY_LARGE
    if node_count > 750 or edge_count > 5000:
        return GraphSizeTier.LARGE
    if node_count > 250 or edge_count > 1000:
        return GraphSizeTier.MEDIUM
    return GraphSizeTier.SMALL


def _recommended_view(tier: GraphSizeTier, *, was_truncated: bool) -> GraphViewMode:
    if tier == GraphSizeTier.VERY_LARGE:
        return GraphViewMode.MATRIX
    if tier == GraphSizeTier.LARGE or was_truncated:
        return GraphViewMode.MATRIX
    if tier == GraphSizeTier.MEDIUM:
        return GraphViewMode.OVERVIEW
    return GraphViewMode.OVERVIEW


def assess_graph_slice(graph_slice: GraphSlice) -> GraphDensityAssessment:
    """Classify graph size/density and recommend a rendering strategy."""
    node_count = len(graph_slice.nodes)
    edge_count = len(graph_slice.edges)
    before_limit = graph_slice.limits.edge_count_before_limit
    tier = _tier_for_counts(node_count, edge_count)

    max_possible_edges = node_count * max(node_count - 1, 1)
    density = edge_count / max_possible_edges if node_count > 1 else 0.0
    avg_degree = (edge_count * 2 / node_count) if node_count else 0.0

    warnings: list[str] = []
    actions: list[str] = list(graph_slice.limits.recommended_actions)

    if graph_slice.limits.was_truncated:
        warnings.append(
            f"Showing top {graph_slice.limits.shown_edges:,} of {before_limit:,} eligible edges."
        )
    if tier in {GraphSizeTier.LARGE, GraphSizeTier.VERY_LARGE}:
        warnings.append("Graph is dense enough that a node-link view may be hard to read.")
    if tier == GraphSizeTier.VERY_LARGE:
        warnings.append("Prefer matrix, ranked tables, or ego networks over a full overview graph.")
    if density > 0.15 and node_count >= 100:
        warnings.append("High edge density detected; consider raising min_weight.")

    if not actions:
        if tier == GraphSizeTier.MEDIUM:
            actions = ["Hide low-weight labels", "Increase minimum edge weight if the graph feels cluttered"]
        elif tier in {GraphSizeTier.LARGE, GraphSizeTier.VERY_LARGE}:
            actions = [
                "Increase minimum edge weight",
                "Switch to matrix view",
                "Use ranked relationship tables",
                "Open an ego network for one member",
            ]

    recommended_view = _recommended_view(tier, was_truncated=graph_slice.limits.was_truncated)
    node_link_acceptable = tier in {GraphSizeTier.SMALL, GraphSizeTier.MEDIUM}
    interactive_html_acceptable = tier != GraphSizeTier.VERY_LARGE or edge_count <= 10000

    return GraphDensityAssessment(
        node_count=node_count,
        edge_count=edge_count,
        edge_count_before_limit=before_limit,
        avg_degree=avg_degree,
        density=density,
        tier=tier,
        recommended_view=recommended_view,
        node_link_acceptable=node_link_acceptable,
        interactive_html_acceptable=interactive_html_acceptable,
        warnings=warnings,
        recommended_actions=actions,
    )


def recommend_explore_config(
    config: GraphExploreConfig,
    assessment: GraphDensityAssessment,
    *,
    was_truncated: bool = False,
) -> GraphExploreConfig:
    """Return safer filter settings for dense graphs.

    ``max_edges`` and ``min_weight`` are only tightened when the current slice was
    truncated — explicit CLI limits are otherwise preserved. Metric toggles may still
    adjust for large node counts.
    """
    updates: dict[str, Any] = {}
    if assessment.tier == GraphSizeTier.MEDIUM:
        if was_truncated:
            updates["max_edges"] = min(config.max_edges, 5000)
            updates["min_weight"] = max(config.min_weight, 2)
        updates["compute_advanced_metrics"] = config.compute_advanced_metrics and assessment.node_count <= 400
    elif assessment.tier == GraphSizeTier.LARGE:
        if was_truncated:
            updates["min_weight"] = max(config.min_weight, 2)
            updates["max_edges"] = min(config.max_edges, 3000)
        updates["compute_advanced_metrics"] = False
        updates["compute_communities"] = assessment.node_count <= 1000
    elif assessment.tier == GraphSizeTier.VERY_LARGE:
        if was_truncated:
            updates["min_weight"] = max(config.min_weight, 3)
            updates["max_edges"] = min(config.max_edges, 1000)
        updates["compute_advanced_metrics"] = False
        updates["compute_communities"] = assessment.node_count <= 750

    if not updates:
        return config
    return config.model_copy(update=updates)


def profile_graph_rendering(
    graph_slice: GraphSlice,
    render_config: GraphRenderConfig | None = None,
) -> dict[str, Any]:
    """Measure graph build artifacts relevant to rendering performance."""
    from .interactive import prepare_sigma_render_payload

    config = render_config or GraphRenderConfig()
    assessment = assess_graph_slice(graph_slice)

    build_start = perf_counter()
    sigma_payload = graph_slice_to_sigma_payload(graph_slice)
    sigma_build_ms = (perf_counter() - build_start) * 1000

    html_start = perf_counter()
    html_payload = prepare_sigma_render_payload(graph_slice, config)
    html_build_ms = (perf_counter() - html_start) * 1000

    sigma_json_bytes = len(json.dumps(sigma_payload).encode("utf-8"))
    html_json_bytes = len(json.dumps(html_payload).encode("utf-8"))

    return {
        "assessment": assessment.model_dump(mode="json"),
        "sigmaBuildMs": round(sigma_build_ms, 2),
        "htmlPayloadBuildMs": round(html_build_ms, 2),
        "sigmaJsonBytes": sigma_json_bytes,
        "htmlJsonBytes": html_json_bytes,
        "sigmaJsonMegabytes": round(sigma_json_bytes / (1024 * 1024), 3),
        "htmlJsonMegabytes": round(html_json_bytes / (1024 * 1024), 3),
    }
