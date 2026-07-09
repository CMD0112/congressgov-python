"""Tests for shared live graph example CLI helpers."""

from __future__ import annotations

import argparse
from types import SimpleNamespace

from congressgov.services.export.graph import build_graph_slice, generate_dense_sponsorship_events

from examples._graph_live_common import (
    add_graph_filter_args,
    apply_graph_filters,
    build_explore_config,
)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    add_graph_filter_args(parser)
    return parser.parse_args(argv)


def test_build_explore_config_all_bill_types_clears_export_filter() -> None:
    args = _parse_args(["--bill-type", "hr", "--max-edges", "5000"])
    config = build_explore_config(args, export_all_bill_types=True)
    assert config.bill_type is None
    assert config.max_edges == 5000


def test_apply_graph_filters_no_safer_filters_preserves_limits() -> None:
    events = generate_dense_sponsorship_events(member_count=40, bills_per_sponsor=8, cosponsors_per_bill=20)
    args = SimpleNamespace(
        congress=118,
        bill_type="hr",
        min_weight=1,
        max_edges=500,
        no_safer_filters=True,
    )
    explore_config = build_explore_config(args)
    graph = build_graph_slice(events, explore_config)

    filtered_graph, slice_config, _assessment = apply_graph_filters(
        explore_config,
        graph,
        no_safer_filters=True,
        rebuild=lambda config: build_graph_slice(events, config),
    )

    assert slice_config.max_edges == 500
    assert slice_config.min_weight == 1
    assert filtered_graph.limits.was_truncated is True
    assert len(filtered_graph.edges) <= 500
