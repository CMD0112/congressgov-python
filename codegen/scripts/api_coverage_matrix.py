#!/usr/bin/env python3
"""Build API path coverage matrix: OpenAPI paths vs hand services/extensions/client."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = REPO_ROOT / "codegen" / "config" / "openapi_spec.yaml"
DEFAULT_ENTITY_MAPPINGS = REPO_ROOT / "codegen" / "config" / "entity_mappings.yaml"
DEFAULT_ALIASES = REPO_ROOT / "codegen" / "config" / "legacy_client_aliases.yaml"
SERVICES_ROOT = REPO_ROOT / "src" / "congressgov" / "services"
DOCS_MD = REPO_ROOT / "docs" / "maintainers" / "API_COVERAGE.md"
DOCS_JSON = REPO_ROOT / "docs" / "api_coverage.json"

# OpenAPI tag (kebab) -> adopted hand service module stem
TAG_TO_SERVICE: dict[str, str] = {
    "bill": "bill",
    "amendments": "amendment",
    "member": "member",
    "committee": "committee",
    "hearing": "hearing",
    "nomination": "nomination",
    "treaty": "treaty",
    "house-vote": "house_vote",
    "summaries": "summaries",
    "crsreport": "crsreport",
    "house-communication": "house_communication",
    "senate-communication": "senate_communication",
    "committee-meeting": "committee_meeting",
    "committee-report": "committee_report",
    "committee-print": "committee_print",
    "congress": "congress",
    "house-requirement": "house_requirement",
    "congressional-record": "congressional_record",
    "daily-congressional-record": "daily_congressional_record",
    "bound-congressional-record": "bound_congressional_record",
}

# Hand service method name -> normalized OpenAPI path (per service module stem)
HAND_METHOD_PATHS: dict[str, dict[str, str]] = {
    "committee": {
        "get_by_congress": "/committee/{}/{}/{}",
    },
    "committee_print": {
        "get_text": "/committee-print/{}/{}/{}/text",
    },
    "committee_report": {
        "get_text": "/committee-report/{}/{}/{}/text",
    },
    "house_vote": {
        "members": "/house-vote/{}/{}/{}/members",
        "list_by_congress_session": "/house-vote/{}/{}",
    },
    "house_requirement": {
        "matching_communications": "/house-requirement/{}/matching-communications",
    },
    "member": {
        "list_by_congress": "/member/congress/{}",
    },
    "nomination": {
        "get_nominees": "/nomination/{}/{}/{}",
    },
    "treaty": {
        "get_actions": "/treaty/{}/{}/actions",
    },
    "daily_congressional_record": {
        "search": "/daily-congressional-record",
        "get_volume": "/daily-congressional-record/{}",
        "get_issue": "/daily-congressional-record/{}/{}",
        "get_articles": "/daily-congressional-record/{}/{}/articles",
    },
    "bound_congressional_record": {
        "get_by_year": "/bound-congressional-record/{}",
        "get_by_year_month": "/bound-congressional-record/{}/{}",
        "get_by_date": "/bound-congressional-record/{}/{}/{}",
    },
}

SYNC_REF_RE = re.compile(r"\b([a-z][a-z0-9_]*_sync)\b")
ASYNC_REF_RE = re.compile(r"\b([a-z][a-z0-9_]*_async)\b")
DETAILED_ALIAS_RE = re.compile(
    r"(?:sync_detailed|asyncio_detailed)\s+as\s+([a-z][a-z0-9_]*)"
)
METHOD_DEF_RE = re.compile(r"\bdef\s+([a-z_][a-z0-9_]*)\s*\(")


@dataclass
class PathRow:
    method: str
    path: str
    tags: list[str]
    x_entity: str | None
    x_api_function: str | None
    coverage: str
    notes: str


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _service_module_text(service_key: str) -> str:
    path = SERVICES_ROOT / f"{service_key}.py"
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _hand_method_for_path(service_key: str, norm: str) -> str | None:
    text = _service_module_text(service_key)
    if not text:
        return None
    defined = set(METHOD_DEF_RE.findall(text))
    for method, pattern in HAND_METHOD_PATHS.get(service_key, {}).items():
        if method not in defined:
            continue
        if norm == pattern or _paths_similar(norm, pattern):
            return method
    return None


def _collect_hand_service_api_refs() -> tuple[set[str], set[str], dict[str, set[str]]]:
    """Return (sync_names, async_names, sync_name -> set of hand service file stems)."""
    sync_names: set[str] = set()
    async_names: set[str] = set()
    by_file: dict[str, set[str]] = defaultdict(set)

    for py in SERVICES_ROOT.rglob("*.py"):
        if ".generated." in py.name or py.name.endswith(".generated.py"):
            continue
        rel = py.relative_to(SERVICES_ROOT)
        stem = rel.stem if rel.parent == Path(".") else f"{rel.parent.name}/{rel.stem}"
        text = py.read_text(encoding="utf-8", errors="replace")
        for m in SYNC_REF_RE.finditer(text):
            sync_names.add(m.group(1))
            by_file[m.group(1)].add(str(stem).replace("\\", "/"))
        for m in ASYNC_REF_RE.finditer(text):
            async_names.add(m.group(1))
        for m in DETAILED_ALIAS_RE.finditer(text):
            alias = m.group(1)
            sync_names.add(alias)
            by_file[alias].add(str(stem).replace("\\", "/"))
    return sync_names, async_names, by_file


def _alias_url_index(aliases_path: Path) -> dict[str, tuple[str, str]]:
    """Map legacy *_sync name -> (package, url_path)."""
    data = _load_yaml(aliases_path)
    out: dict[str, tuple[str, str]] = {}
    for package, entries in (data.get("packages") or {}).items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = entry.get("legacy_name", "")
            url = entry.get("url_path", "")
            if name.endswith("_sync") and url:
                out[name] = (package, url)
    return out


def _normalize_path(url: str) -> str:
    """Normalize URL template for comparison."""
    return re.sub(r"\{[^}]+\}", "{}", url)


def _classify_path(
    path: str,
    method: str,
    tags: list[str],
    x_entity: str | None,
    x_api_function: str | None,
    sync_in_hand_services: set[str],
    sync_by_file: dict[str, set[str]],
    alias_by_sync: dict[str, tuple[str, str]],
) -> tuple[str, str]:
    norm = _normalize_path(path)
    tag = tags[0] if tags else ""

    if tag in TAG_TO_SERVICE:
        service_key = TAG_TO_SERVICE[tag]
        hand_method = _hand_method_for_path(service_key, norm)
        if hand_method:
            return "hand_service", f"hand.{hand_method} on {service_key}"

    if x_api_function and x_api_function in sync_in_hand_services:
        if x_api_function in alias_by_sync:
            _pkg, alias_url = alias_by_sync[x_api_function]
            if _normalize_path(alias_url) == norm:
                locs = ", ".join(sorted(sync_by_file.get(x_api_function, [])))
                return "hand_service", f"annotated {x_api_function}" + (
                    f" in {locs}" if locs else ""
                )
        else:
            locs = ", ".join(sorted(sync_by_file.get(x_api_function, [])))
            return "hand_service", f"annotated {x_api_function}" + (
                f" in {locs}" if locs else ""
            )

    for sync_name, (pkg, url) in alias_by_sync.items():
        if _normalize_path(url) == norm and sync_name in sync_in_hand_services:
            locs = ", ".join(sorted(sync_by_file.get(sync_name, [])))
            return "hand_service", f"via {sync_name}" + (f" in {locs}" if locs else "")

    for sync_name, (pkg, url) in alias_by_sync.items():
        if pkg.replace("_", "-") == tag.replace("_", "-") or pkg == tag:
            if sync_name in sync_in_hand_services and _paths_similar(norm, _normalize_path(url)):
                return "service_method", sync_name

    if tag in TAG_TO_SERVICE:
        service = TAG_TO_SERVICE[tag]
        if x_entity:
            return "hand_service", f"primary/list annotation for {x_entity}"
        depth = norm.count("{}")
        if depth <= 1:
            return "hand_service", f"list or primary on {service}"
        return "service_method", f"sub-path on {service} (implement or extension)"

    if tag:
        return "client_only", f"tag {tag}; no hand service module"

    return "uncovered", "no tag"


def _paths_similar(a: str, b: str) -> bool:
    if a == b:
        return True
    if a.count("{}") != b.count("{}"):
        return False
    return a.startswith(b) or b.startswith(a)


def build_matrix(
    spec_path: Path,
    aliases_path: Path,
) -> list[PathRow]:
    spec = _load_yaml(spec_path)
    paths_spec = spec.get("paths") or {}
    sync_in_mw, _async_in_mw, sync_by_file = _collect_hand_service_api_refs()
    alias_by_sync = _alias_url_index(aliases_path)

    rows: list[PathRow] = []
    for path, methods in sorted(paths_spec.items()):
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            if not isinstance(op, dict):
                continue
            tags = op.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]
            x_entity = op.get("x-entity-name")
            x_api = op.get("x-api-function")
            coverage, notes = _classify_path(
                path, method.upper(), tags, x_entity, x_api,
                sync_in_mw, sync_by_file, alias_by_sync,
            )
            rows.append(
                PathRow(
                    method=method.upper(),
                    path=path,
                    tags=list(tags),
                    x_entity=x_entity,
                    x_api_function=x_api,
                    coverage=coverage,
                    notes=notes,
                )
            )
    return rows


def render_markdown(rows: list[PathRow]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r.coverage] += 1

    lines = [
        "# API coverage matrix",
        "",
        "> **Maintainer documentation.** This page is for people maintaining the congressgov "
        "repository. If you're using the SDK, you don't need this — see the "
        "[user guide](../guide/USAGE.md) instead.",
        "",
        "Auto-generated by `poetry run api-coverage-matrix`. Do not edit by hand.",
        "",
        "## Coverage labels",
        "",
        "| Label | Meaning |",
        "|-------|---------|",
        "| `hand_service` | Covered by hand-maintained `congressgov.services` (search, extensions, or dedicated methods) |",
        "| `service_method` | Gap — not yet implemented on the hand service (CI `--check-service-methods` fails on these) |",
        "| `client_only` | Tag maps to a service area but no hand module covers this path yet |",
        "| `uncovered` | No OpenAPI tag or unclassified path |",
        "",
        "## Summary",
        "",
        "| Coverage | Count |",
        "|----------|------:|",
    ]
    for key in sorted(counts.keys()):
        lines.append(f"| `{key}` | {counts[key]} |")
    lines.append(f"| **Total** | **{len(rows)}** |")
    lines.append("")
    lines.append("## Gap backlog (`uncovered` and `client_only`)")
    lines.append("")
    lines.append("| Method | Path | Tags | Notes |")
    lines.append("|--------|------|------|-------|")
    for r in rows:
        if r.coverage in ("uncovered", "client_only"):
            lines.append(
                f"| {r.method} | `{r.path}` | {', '.join(r.tags)} | {r.notes} |"
            )
    lines.append("")
    lines.append("## Full matrix")
    lines.append("")
    lines.append("| Method | Path | Coverage | Entity | API function | Notes |")
    lines.append("|--------|------|----------|--------|--------------|-------|")
    for r in rows:
        lines.append(
            f"| {r.method} | `{r.path}` | `{r.coverage}` | "
            f"{r.x_entity or ''} | {r.x_api_function or ''} | {r.notes} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate API coverage matrix")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--markdown", type=Path, default=DOCS_MD)
    parser.add_argument("--json", type=Path, default=DOCS_JSON)
    parser.add_argument("--check", action="store_true", help="Exit 1 if any uncovered paths")
    parser.add_argument(
        "--check-service-methods",
        action="store_true",
        help="Exit 1 if any service_method rows remain",
    )
    args = parser.parse_args()

    rows = build_matrix(args.spec, args.aliases)
    md_content = render_markdown(rows)
    json_content = json.dumps([asdict(r) for r in rows], indent=2)

    import sys

    if args.check:
        stale = False
        if not args.markdown.exists() or args.markdown.read_text(encoding="utf-8") != md_content:
            print(
                "::error::docs/maintainers/API_COVERAGE.md is stale. "
                "Run: poetry run python -m codegen.scripts.api_coverage_matrix",
                file=sys.stderr,
            )
            stale = True
        if not args.json.exists() or args.json.read_text(encoding="utf-8") != json_content:
            print(
                "::error::docs/api_coverage.json is stale. "
                "Run: poetry run python -m codegen.scripts.api_coverage_matrix",
                file=sys.stderr,
            )
            stale = True
        if stale:
            return 1
    else:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(md_content, encoding="utf-8")
        args.json.write_text(json_content, encoding="utf-8")
        print(f"Wrote {args.markdown} ({len(rows)} operations)")
        print(f"Wrote {args.json}")

    uncovered = sum(1 for r in rows if r.coverage == "uncovered")
    service_methods = sum(1 for r in rows if r.coverage == "service_method")
    if args.check and uncovered:
        print(f"::error::{uncovered} uncovered path(s)", file=sys.stderr)
        return 1
    if args.check_service_methods and service_methods:
        print(
            f"::error::{service_methods} service_method path(s) remain",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
