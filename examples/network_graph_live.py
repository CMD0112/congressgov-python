"""Build a sponsor/cosponsor network graph from live Congress.gov data.

This script builds an **ephemeral** bill-driven network graph: members appear
only when they have sponsorship ties in the fetched bill batch. For the
member-first roster graph that persists bills over time, use
``examples/congress_roster_graph_live.py`` instead.

Loads ``CONGRESS_API_KEY`` from the repository ``.env`` file (copy from
``.env.example``). Register for a key at https://api.congress.gov/sign-up/

Example:

    poetry run python examples/network_graph_live.py
    poetry run python examples/network_graph_live.py --max-bills 40
    poetry run python examples/network_graph_live.py --min-weight 2 --max-edges 800 --no-safer-filters
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from congressgov import Bill, Member, get_client_from_env
from congressgov.services.core.workspace import Workspace
from congressgov.services.export.graph import (
    GraphIngestionConfig,
    GraphRenderConfig,
    build_graph_slice,
    create_member_label_resolver,
    export_graph_slice_json,
    export_graph_slice_to_workspace,
    export_interactive_html,
    ingest_bill_events,
    rank_relationships,
)

from _graph_live_common import (
    add_graph_filter_args,
    apply_graph_filters,
    build_explore_config,
    filter_summary_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = REPO_ROOT / ".env"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "examples" / "output" / "network_graph"
OUTPUT_HTML_NAME = "live_network_explorer.html"
OUTPUT_JSON_NAME = "live_graph_api.json"
OUTPUT_SUMMARY_NAME = "live_graph_summary.json"
PLACEHOLDER_API_KEYS = frozenset({"", "your-api-key-here", "your_api_key_here"})


def load_project_env(env_path: Path = DEFAULT_ENV_PATH) -> None:
    """Load environment variables from the project ``.env`` file."""
    if not env_path.exists():
        raise FileNotFoundError(
            f"No .env file found at {env_path}. "
            "Copy .env.example to .env and set CONGRESS_API_KEY."
        )
    load_dotenv(env_path)


def validate_api_key(env_path: Path = DEFAULT_ENV_PATH) -> None:
    """Fail fast when `.env` still contains the placeholder key."""
    key = os.getenv("CONGRESS_API_KEY", "").strip()
    if key.lower() in PLACEHOLDER_API_KEYS:
        raise ValueError(
            f"CONGRESS_API_KEY in {env_path} is unset or still the .env.example "
            "placeholder. Register at https://api.congress.gov/sign-up/ and paste "
            "your real key into .env (do not commit that file)."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch live bills from Congress.gov and export a network graph.",
    )
    add_graph_filter_args(parser)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument(
        "--workspace-exports",
        action="store_true",
        help="Also write HTML/JSON into .congressgov/exports/ artifact lane",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        load_project_env(args.env_file)
        validate_api_key(args.env_file)
        client = get_client_from_env(load_dotenv=False)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    bill_service = Bill(client=client)
    member_service = Member(client=client)
    member_resolver = create_member_label_resolver(
        member_service,
        congress=args.congress,
        client=client,
    )

    ingestion_config = GraphIngestionConfig(
        congress=args.congress,
        bill_type=args.bill_type,
        batch_size=max(1, args.max_bills),
    )

    print(
        f"Fetching up to {args.max_bills} {args.bill_type.upper()} bills "
        f"from the {args.congress}th Congress..."
    )
    print("API responses are persisted locally (request store); repeat runs reuse cached data.")

    events = ingest_bill_events(
        bill_service,
        ingestion_config,
        fetch_cosponsors=True,
    )
    explore_config = build_explore_config(args)
    graph = build_graph_slice(events, explore_config, member_resolver=member_resolver)

    if not events:
        print(
            "No sponsorship events returned. Check that CONGRESS_API_KEY in "
            f"{args.env_file} is your real key (not the .env.example placeholder), "
            "then try increasing --max-bills or a different --bill-type.",
            file=sys.stderr,
        )
        return 1

    graph, slice_config, assessment = apply_graph_filters(
        explore_config,
        graph,
        no_safer_filters=args.no_safer_filters,
        rebuild=lambda config: build_graph_slice(
            events,
            config,
            member_resolver=member_resolver,
        ),
    )

    ranked = rank_relationships(events, slice_config, top_n=10)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    html_path = args.output_dir / OUTPUT_HTML_NAME
    json_path = args.output_dir / OUTPUT_JSON_NAME

    title = f"{args.congress}th Congress {args.bill_type.upper()} network"
    export_interactive_html(
        graph,
        html_path,
        render_config=GraphRenderConfig(title=title),
    )
    export_graph_slice_json(graph, json_path)

    if args.workspace_exports:
        ws = Workspace.open(REPO_ROOT / ".congressgov")
        artifact_paths = export_graph_slice_to_workspace(
            graph,
            ws,
            prefix=f"network_graph/{args.congress}_{args.bill_type}",
            title=title,
        )
        print(f"Workspace HTML:       {artifact_paths['html']}")
        print(f"Workspace JSON:       {artifact_paths['json']}")

    print()
    print(f"Sponsorship events: {len(events):,}")
    print(f"Graph slice: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    print(
        f"Slice limits: {graph.limits.shown_edges:,} shown of "
        f"{graph.limits.edge_count_before_limit:,} eligible "
        f"(max_edges={slice_config.max_edges}, min_weight={slice_config.min_weight})"
    )
    print(
        f"Density tier: {assessment.tier} - "
        f"recommended view: {assessment.recommended_view}"
    )
    if assessment.warnings:
        print(f"Note: {assessment.warnings[0]}")
    print()
    print("Top relationships:")
    for relationship in ranked[:5]:
        source = relationship.source_label or relationship.source_id
        target = relationship.target_label or relationship.target_id
        print(f"  {source} <-> {target} ({relationship.weight} bills)")
    print()
    print(f"Interactive explorer: {html_path.resolve()}")
    print(f"Graph JSON:           {json_path.resolve()}")

    summary_path = args.output_dir / OUTPUT_SUMMARY_NAME
    summary_path.write_text(
        json.dumps(
            {
                "graphKind": "network_graph",
                "congress": args.congress,
                "billType": args.bill_type,
                "eventCount": len(events),
                "nodeCount": len(graph.nodes),
                "edgeCount": len(graph.edges),
                "filters": filter_summary_payload(explore_config, slice_config, graph),
                "assessment": assessment.model_dump(mode="json"),
                "topRelationships": [
                    {
                        "source": item.source_label or item.source_id,
                        "target": item.target_label or item.target_id,
                        "weight": item.weight,
                    }
                    for item in ranked[:10]
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Summary JSON:         {summary_path.resolve()}")
    print()
    print("Open the HTML file in a browser. Use sidebar filters to explore dense ties.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
