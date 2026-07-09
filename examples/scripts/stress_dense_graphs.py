"""Profile advanced rendering on large, highly connected synthetic graphs."""

from __future__ import annotations

from pathlib import Path

from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphViewMode,
    assess_graph_slice,
    build_graph_slice,
    export_interactive_html,
    generate_dense_sponsorship_events,
    profile_graph_rendering,
    recommend_explore_config,
)

SCENARIOS = [
    ("medium_notebook", dict(member_count=80, bills_per_sponsor=12, cosponsors_per_bill=30, seed=7)),
    ("large", dict(member_count=150, bills_per_sponsor=15, cosponsors_per_bill=35, seed=11)),
    ("very_large", dict(member_count=250, bills_per_sponsor=20, cosponsors_per_bill=40, seed=13)),
]

LOOSE = GraphExploreConfig(congress=118, min_weight=1, max_edges=20000)
OUT_DIR = Path(__file__).resolve().parents[1] / "output" / "network_graph"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, kwargs in SCENARIOS:
        events = generate_dense_sponsorship_events(**kwargs)
        loose_graph = build_graph_slice(events, LOOSE)
        assessment = assess_graph_slice(loose_graph)
        safer = recommend_explore_config(LOOSE, assessment, was_truncated=loose_graph.limits.was_truncated)
        graph = build_graph_slice(events, safer)
        safe_assessment = assess_graph_slice(graph)
        profile = profile_graph_rendering(graph)
        html_path = OUT_DIR / f"dense_{name}.html"
        export_interactive_html(graph, html_path)
        html_kb = html_path.stat().st_size / 1024

        print(f"=== {name} ===")
        print(f"  raw events: {len(events):,}")
        print(
            f"  loose slice: {assessment.node_count} nodes, {assessment.edge_count} edges, "
            f"tier={assessment.tier}, truncated={loose_graph.limits.was_truncated}"
        )
        print(
            f"  safer config: min_weight={safer.min_weight}, max_edges={safer.max_edges}, "
            f"adv_metrics={safer.compute_advanced_metrics}"
        )
        print(
            f"  safer slice: {safe_assessment.node_count} nodes, {safe_assessment.edge_count} edges, "
            f"tier={safe_assessment.tier}"
        )
        print(
            f"  recommended_view={safe_assessment.recommended_view}, "
            f"node_link_ok={safe_assessment.node_link_acceptable}, "
            f"html_ok={safe_assessment.interactive_html_acceptable}"
        )
        print(
            f"  sigma build: {profile['sigmaBuildMs']}ms, "
            f"html payload: {profile['htmlPayloadBuildMs']}ms"
        )
        print(
            f"  json size: {profile['sigmaJsonMegabytes']} MB sigma / "
            f"{profile['htmlJsonMegabytes']} MB embedded"
        )
        print(f"  html file: {html_kb:.1f} KB -> {html_path.name}")
        if safe_assessment.warnings:
            print(f"  first warning: {safe_assessment.warnings[0]}")
        matrix_fallback = safe_assessment.recommended_view == GraphViewMode.MATRIX
        print(f"  matrix fallback recommended: {matrix_fallback}")
        print()


if __name__ == "__main__":
    main()
