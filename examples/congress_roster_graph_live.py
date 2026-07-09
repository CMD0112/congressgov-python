"""Build a member-first congress roster graph from live Congress.gov data.

Seeds the full member roster for a Congress, then incrementally adds bills to
grow sponsorship edges over time. Dataset state persists in the workspace record
lane (``.congressgov/datasets/graphs/{congress}.json``).

Loads ``CONGRESS_API_KEY`` from the repository ``.env`` file (copy from
``.env.example``). Register for a key at https://api.congress.gov/sign-up/

Example:

    poetry run python examples/congress_roster_graph_live.py
    poetry run python examples/congress_roster_graph_live.py --max-bills 40
    poetry run python examples/congress_roster_graph_live.py --max-edges 10000 --no-safer-filters
    poetry run python examples/congress_roster_graph_live.py --all-bill-types --max-edges 10000
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
    CongressGraphStore,
    GraphIngestionConfig,
    GraphRenderConfig,
    create_member_label_resolver,
    export_graph_slice_json,
    export_graph_slice_to_workspace,
    export_interactive_html,
    make_bill_id,
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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "examples" / "output" / "congress_roster_graph"
OUTPUT_HTML_NAME = "roster_graph_explorer.html"
OUTPUT_JSON_NAME = "roster_graph_api.json"
OUTPUT_SUMMARY_NAME = "roster_graph_summary.json"
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
        description=(
            "Seed a congress member roster and incrementally build a roster graph "
            "from live bills."
        ),
    )
    add_graph_filter_args(parser)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument(
        "--store-path",
        type=Path,
        default=None,
        help="Override path for roster graph dataset JSON",
    )
    parser.add_argument(
        "--all-bill-types",
        action="store_true",
        help="Export all ingested bill types in the slice (--bill-type still controls ingestion)",
    )
    parser.add_argument(
        "--workspace-exports",
        action="store_true",
        help="Also write HTML/JSON into .congressgov/exports/ artifact lane",
    )
    return parser.parse_args()


def _bill_identity(bill: Bill) -> tuple[int, str, int]:
    bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
    if hasattr(bill_type, "value"):
        bill_type = str(bill_type.value)
    bill_number = getattr(bill, "bill_number", getattr(bill, "number", None))
    return int(bill.congress), str(bill_type).lower(), int(bill_number)


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

    workspace = Workspace.open(REPO_ROOT / ".congressgov")
    store = (
        workspace.open_graph(args.congress)
        if args.store_path is None
        else CongressGraphStore.open(args.store_path, congress=args.congress)
    )
    store_path = store.path
    if store.congress != args.congress:
        print(
            f"Dataset at {store_path} is for the {store.congress}th Congress, "
            f"but --congress {args.congress} was requested.",
            file=sys.stderr,
        )
        return 1

    if store.member_count == 0:
        print(f"Seeding member roster for the {args.congress}th Congress...")
        seeded = store.seed_members_from_service(member_service, fetch_all=True)
        store.save()
        print(f"Seeded {seeded:,} members into {store_path.resolve()}")
    else:
        print(
            f"Loaded roster graph dataset: {store.member_count:,} members, "
            f"{store.bill_count:,} bills, {store.event_count:,} events"
        )

    resolved_labels = store.resolve_member_labels(member_resolver)
    if resolved_labels:
        store.save()
        print(f"Resolved {resolved_labels:,} member display names in the roster dataset")

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

    search_kwargs: dict[str, object] = {
        "congress": args.congress,
        "limit": ingestion_config.batch_size,
    }
    if args.bill_type:
        search_kwargs["bill_type"] = args.bill_type
    search_result = bill_service.search(**search_kwargs)
    bills = getattr(search_result, "bills", None) or []
    added_bills = 0
    skipped_bills = 0
    new_events = 0
    for bill in bills[: args.max_bills]:
        congress, bill_type, bill_number = _bill_identity(bill)
        bill_id = make_bill_id(congress, bill_type, bill_number)
        if bill_id in store.bill_ids:
            skipped_bills += 1
            continue

        if hasattr(bill_service, "get") and not getattr(bill, "sponsors", None):
            bill = bill_service.get(
                congress=congress,
                bill_type=bill_type,
                bill_number=bill_number,
                client=client,
            )
        cosponsors = (
            bill.get_cosponsors(limit=ingestion_config.cosponsor_limit)
            if hasattr(bill, "get_cosponsors")
            else None
        )
        result = store.add_bill(bill, cosponsors)
        if result.added:
            added_bills += 1
            new_events += result.event_count
    store.save()
    events = store.events
    print(f"Added {added_bills:,} new bills ({new_events:,} new events)")
    if skipped_bills:
        print(f"Skipped {skipped_bills:,} bills already present in the roster dataset")

    explore_config = build_explore_config(
        args,
        include_all_members=True,
        export_all_bill_types=args.all_bill_types,
    )
    graph = store.build_slice(explore_config, member_resolver=member_resolver)

    if not events:
        print(
            "No sponsorship events in the roster dataset yet. Check that "
            f"CONGRESS_API_KEY in {args.env_file} is your real key, then try "
            "increasing --max-bills or a different --bill-type.",
            file=sys.stderr,
        )
        return 1

    graph, slice_config, assessment = apply_graph_filters(
        explore_config,
        graph,
        no_safer_filters=args.no_safer_filters,
        rebuild=lambda config: store.build_slice(config, member_resolver=member_resolver),
        preserve={"include_all_members": True},
    )
    store.save()

    ranked = rank_relationships(events, slice_config, top_n=10)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    html_path = args.output_dir / OUTPUT_HTML_NAME
    json_path = args.output_dir / OUTPUT_JSON_NAME

    export_bill_type = slice_config.bill_type or "all"
    title = f"{args.congress}th Congress roster graph ({export_bill_type.upper()})"
    export_interactive_html(
        graph,
        html_path,
        render_config=GraphRenderConfig(title=title),
    )
    export_graph_slice_json(graph, json_path)

    if args.workspace_exports:
        artifact_paths = export_graph_slice_to_workspace(
            graph,
            workspace,
            prefix=f"congress_roster_graph/{args.congress}_{export_bill_type}",
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
    print(f"Dataset:              {store_path.resolve()}")

    summary_path = args.output_dir / OUTPUT_SUMMARY_NAME
    summary_path.write_text(
        json.dumps(
            {
                "graphKind": "congress_roster_graph",
                "congress": args.congress,
                "billType": args.bill_type,
                "exportBillType": export_bill_type,
                "eventCount": len(events),
                "nodeCount": len(graph.nodes),
                "edgeCount": len(graph.edges),
                "storeStats": store.stats(),
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
    print("Open the HTML file in a browser. Isolated roster members appear as nodes without edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
