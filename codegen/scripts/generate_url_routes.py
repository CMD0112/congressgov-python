#!/usr/bin/env python3
"""Generate url_routes_generated.py from legacy_client_aliases.yaml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIASES = REPO_ROOT / "codegen" / "config" / "legacy_client_aliases.yaml"
DEFAULT_OUTPUT = (
    REPO_ROOT / "src" / "congressgov" / "services" / "core" / "url_routes_generated.py"
)

SUBRESOURCE_MODELS: dict[str, str] = {
    "actions": "Actions",
    "amendments": "Amendments",
    "articles": "DailyCongressionalRecord",
    "bills": "Bills",
    "committees": "Committees",
    "cosponsors": "Cosponsors",
    "cosponsored-legislation": "CosponsoredLegislation",
    "hearings": "Hearings",
    "house-communication": "HouseCommunications",
    "matching-communications": "MatchingCommunications",
    "members": "MemberVotes",
    "nominations": "Nominations",
    "nominees": "Nominees",
    "relatedbills": "Bills",
    "reports": "CommitteeReports",
    "senate-communication": "SenateCommunications",
    "sponsored-legislation": "SponsoredLegislation",
    "subjects": "Subject",
    "summaries": "Summaries",
    "text": "TextVersions",
    "titles": "Titles",
}

PACKAGE_DETAIL_MODEL: dict[str, str] = {
    "amendments": "Amendment",
    "bill": "Bill",
    "bound_congressional_record": "BoundCongressionalRecord",
    "committee": "Committee",
    "committee_meeting": "CommitteeMeeting",
    "committee_print": "CommitteePrint",
    "committee_report": "CommitteeReport",
    "congress": "Congress",
    "congressional_record": "CongressionalRecord",
    "crsreport": "CRSReport",
    "daily_congressional_record": "DailyCongressionalRecord",
    "hearing": "Hearing",
    "house_communication": "HouseCommunication",
    "house_requirement": "HouseRequirement",
    "house_vote": "HouseVote",
    "member": "Member",
    "nomination": "Nomination",
    "senate_communication": "SenateCommunication",
    "summaries": "Summary",
    "treaty": "Treaty",
}

PACKAGE_LIST_MODEL: dict[str, str] = {
    "amendments": "Amendments",
    "bill": "Bills",
    "bound_congressional_record": "BoundCongressionalRecords",
    "committee": "Committees",
    "committee_meeting": "CommitteeMeetings",
    "committee_print": "CommitteePrints",
    "committee_report": "CommitteeReports",
    "congress": "Congresses",
    "congressional_record": "CongressionalRecords",
    "crsreport": "CRSReports",
    "daily_congressional_record": "DailyCongressionalRecords",
    "hearing": "Hearings",
    "house_communication": "HouseCommunications",
    "house_requirement": "HouseRequirements",
    "house_vote": "HouseVotes",
    "member": "Members",
    "nomination": "Nominations",
    "senate_communication": "SenateCommunications",
    "summaries": "Summaries",
    "treaty": "Treaties",
}

# The generic "text" -> TextVersions mapping in SUBRESOURCE_MODELS is correct
# for bills, but committee-print and committee-report `/text` endpoints return
# their own dedicated wrapper models, not TextVersions. Checked ahead of the
# generic subresource lookup in `infer_model_name`.
TEXT_MODEL_BY_PACKAGE: dict[str, str] = {
    "committee_print": "CommitteePrintTexts",
    "committee_report": "CommitteeReportTexts",
}

LEGACY_MODEL_OVERRIDES: dict[str, str] = {
    "law_list_by_congress_law_type_and_law_number_sync": "Bill",
    "law_list_by_congress_and_law_type_sync": "Bills",
    "law_list_by_congress_sync": "Bills",
    "bill_summaries_all_sync": "Summaries",
    "bill_summaries_by_congress_sync": "Summaries",
    "bill_summaries_by_type_sync": "Summaries",
    "congress_current_list_sync": "Congress",
    "committee_reports_sync": "CommitteeReports",
    "treaty_list_sync": "Treaties",
    "amendment_sync": "Amendments",
    "crsreport_sync": "CRSReports",
}


def path_signature(url_template: str) -> str:
    normalized = re.sub(r"/+", "/", url_template)
    return normalized.rstrip("/") or "/"


def infer_model_name(legacy_name: str, url_path: str, package: str) -> str:
    if legacy_name in LEGACY_MODEL_OVERRIDES:
        return LEGACY_MODEL_OVERRIDES[legacy_name]
    parts = [p for p in url_path.strip("/").split("/") if p]
    if parts and parts[-1] == "text" and package in TEXT_MODEL_BY_PACKAGE:
        return TEXT_MODEL_BY_PACKAGE[package]
    if parts and parts[-1] in SUBRESOURCE_MODELS:
        return SUBRESOURCE_MODELS[parts[-1]]
    if "detail" in legacy_name or legacy_name.endswith("_details_sync"):
        return PACKAGE_DETAIL_MODEL.get(package, "Model")
    if (
        "list" in legacy_name
        or legacy_name.endswith("_sync") and "get_" in legacy_name
        or legacy_name in {f"{package}_sync", f"get_{package}_sync"}
    ):
        return PACKAGE_LIST_MODEL.get(package, "Model")
    return PACKAGE_DETAIL_MODEL.get(package, "Model")


def infer_normalize_params(url_path: str) -> tuple[str, ...]:
    params: list[str] = []
    for segment in url_path.split("/"):
        if segment.startswith("{") and segment.endswith("}"):
            name = segment[1:-1]
            if name in ("bill_type", "amendment_type", "law_type", "report_type", "chamber"):
                params.append(name)
    return tuple(params)


def load_routes(aliases_path: Path) -> list[dict]:
    data = yaml.safe_load(aliases_path.read_text(encoding="utf-8"))
    routes: list[dict] = []
    for package, entries in (data.get("packages") or {}).items():
        for entry in entries:
            legacy = entry.get("legacy_name", "")
            if not legacy.endswith("_sync"):
                continue
            url_path = entry.get("url_path") or ""
            if not url_path:
                continue
            async_name = legacy[:-5] + "_async"
            routes.append(
                {
                    "path": path_signature(url_path),
                    "package": package,
                    "sync": legacy,
                    "async": async_name,
                    "model": infer_model_name(legacy, url_path, package),
                    "normalize": infer_normalize_params(url_path),
                }
            )
    routes.sort(key=lambda r: (-r["path"].count("/"), r["path"]))
    return routes


def render(routes: list[dict]) -> str:
    lines = [
        '"""Auto-generated URL route table. Do not edit by hand.',
        "",
        "Regenerate: poetry run python -m codegen.scripts.generate_url_routes",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "URL_ROUTES: list[dict] = [",
    ]
    for route in routes:
        norm = repr(route["normalize"])
        lines.append(
            f'    {{'
            f'"path": {route["path"]!r}, '
            f'"package": {route["package"]!r}, '
            f'"sync": {route["sync"]!r}, '
            f'"async": {route["async"]!r}, '
            f'"model": {route["model"]!r}, '
            f'"normalize": {norm}'
            f"}},"
        )
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate URL route table for url_resolver")
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    routes = load_routes(args.aliases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(routes), encoding="utf-8")
    print(f"Wrote {args.output} ({len(routes)} routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
