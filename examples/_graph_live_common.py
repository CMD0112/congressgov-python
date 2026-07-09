"""Shared CLI helpers for network graph live example scripts."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphSlice,
    assess_graph_slice,
    recommend_explore_config,
)
from congressgov.services.export.graph.models import GraphDensityAssessment


def positive_int(value: str) -> int:
    """Argparse type for integers >= 1."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    return parsed


def add_graph_filter_args(parser: argparse.ArgumentParser) -> None:
    """Register graph filter flags shared by live example scripts."""
    parser.add_argument("--congress", type=positive_int, default=118)
    parser.add_argument(
        "--bill-type",
        default="hr",
        choices=("hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"),
    )
    parser.add_argument("--max-bills", type=positive_int, default=25)
    parser.add_argument("--max-edges", type=positive_int, default=1500)
    parser.add_argument("--min-weight", type=positive_int, default=1)
    parser.add_argument(
        "--no-safer-filters",
        action="store_true",
        help="Use --min-weight and --max-edges exactly; skip density auto-tuning",
    )


def build_explore_config(
    args: argparse.Namespace,
    *,
    include_all_members: bool = False,
    export_all_bill_types: bool = False,
) -> GraphExploreConfig:
    """Build ``GraphExploreConfig`` from parsed CLI args."""
    bill_type = None if export_all_bill_types else args.bill_type
    return GraphExploreConfig(
        congress=args.congress,
        bill_type=bill_type,
        min_weight=args.min_weight,
        max_edges=args.max_edges,
        include_all_members=include_all_members,
        compute_communities=True,
        compute_advanced_metrics=True,
    )


def apply_graph_filters(
    explore_config: GraphExploreConfig,
    graph: GraphSlice,
    *,
    no_safer_filters: bool,
    rebuild: Callable[[GraphExploreConfig], GraphSlice],
    preserve: dict[str, Any] | None = None,
) -> tuple[GraphSlice, GraphExploreConfig, GraphDensityAssessment]:
    """Apply optional density recommendations, honoring explicit CLI limits."""
    assessment = assess_graph_slice(graph)
    slice_config = explore_config
    if no_safer_filters:
        print(
            "Using requested filters: "
            f"min_weight={explore_config.min_weight}, "
            f"max_edges={explore_config.max_edges}, "
            f"bill_type={explore_config.bill_type or 'all'}"
        )
        return graph, slice_config, assessment

    safer_config = recommend_explore_config(
        explore_config,
        assessment,
        was_truncated=graph.limits.was_truncated,
    )
    if preserve:
        safer_config = safer_config.model_copy(update=preserve)
    if safer_config != explore_config:
        print(
            "Applying safer filters for dense data: "
            f"min_weight={safer_config.min_weight}, "
            f"max_edges={safer_config.max_edges}, "
            f"bill_type={safer_config.bill_type or 'all'}"
        )
        graph = rebuild(safer_config)
        assessment = assess_graph_slice(graph)
        slice_config = safer_config
    else:
        print(
            "Requested filters retained: "
            f"min_weight={explore_config.min_weight}, "
            f"max_edges={explore_config.max_edges}, "
            f"bill_type={explore_config.bill_type or 'all'}"
        )
    return graph, slice_config, assessment


def filter_summary_payload(
    requested: GraphExploreConfig,
    applied: GraphExploreConfig,
    graph: GraphSlice,
) -> dict[str, Any]:
    """Serialize requested vs applied graph filters for summary JSON."""
    return {
        "requested": requested.model_dump(mode="json"),
        "applied": applied.model_dump(mode="json"),
        "limits": graph.limits.model_dump(mode="json"),
    }
