"""CLI for workspace storage inspection and maintenance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from congressgov.services.core.request_store import RequestStore
from congressgov.services.core.request_store.introspection import (
    list_keys,
    print_store_stats,
    purge_stale,
    summarize_store,
)
from congressgov.services.core.request_store.policy_loader import load_policy_config
from congressgov.services.core.store_registry.introspection import record_info
from congressgov.services.core.workspace import Workspace, resolve_blob_connection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and maintain Congress.gov workspace storage.",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace root (default: CONGRESS_WORKSPACE or ./.congressgov)",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="Named store or blob connection override (default: api blob store)",
    )
    parser.add_argument(
        "--policy-file",
        default=None,
        help="Optional JSON/YAML policy file for purge-stale",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stats", help="Show blob store statistics")
    sub.add_parser("workspace-summary", help="Summarize workspace and registered stores")

    list_parser = sub.add_parser("list", help="List stored request keys (blob lane)")
    list_parser.add_argument("--prefix", default=None, help="URL path prefix filter")
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.add_argument("--offset", type=int, default=0)

    sub.add_parser("purge-stale", help="Delete stale blob records by policy TTL")

    json_parser = sub.add_parser("summary-json", help="Emit blob summary as JSON")
    json_parser.add_argument("--indent", type=int, default=2)

    record_parser = sub.add_parser("record-info", help="Inspect a record-lane JSON dataset")
    record_parser.add_argument("name", help="Store name (e.g. graphs/118) or filesystem path")

    return parser


def _is_blob_connection(value: str) -> bool:
    if value in (":memory:", "memory://", "memory"):
        return True
    return "://" in value


def _resolve_blob_store(args: argparse.Namespace) -> RequestStore:
    workspace = Workspace.open(args.workspace, ensure_dirs=False)
    policy = load_policy_config(args.policy_file) if args.policy_file else None

    if args.store and _is_blob_connection(args.store):
        store = RequestStore(args.store)
    elif args.store:
        store = workspace.registry().blob(args.store)
    else:
        connection = resolve_blob_connection(workspace=workspace.paths)
        store = RequestStore(connection)

    if policy is not None:
        store.config.policy = policy
    return store


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "workspace-summary":
            workspace = Workspace.open(args.workspace, ensure_dirs=False)
            json.dump(workspace.summarize(), sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 0

        if args.command == "record-info":
            workspace = Workspace.open(args.workspace, ensure_dirs=False)
            name = args.name
            if "/" in name and not Path(name).exists():
                entry = workspace.registry().get_entry(name)
                path = workspace.registry().resolve_path(entry)
            else:
                path = Path(name)
            json.dump(record_info(path), sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 0

        store = _resolve_blob_store(args)
        try:
            if args.command == "stats":
                print_store_stats(store)
            elif args.command == "list":
                for key in list_keys(
                    store,
                    url_prefix=args.prefix,
                    limit=args.limit,
                    offset=args.offset,
                ):
                    print(key)
            elif args.command == "purge-stale":
                removed = purge_stale(store)
                print(f"Removed {removed} stale record(s)")
            elif args.command == "summary-json":
                json.dump(summarize_store(store), sys.stdout, indent=args.indent)
                sys.stdout.write("\n")
            else:
                parser.error(f"Unknown command: {args.command}")
                return 2
        finally:
            store.close()
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
