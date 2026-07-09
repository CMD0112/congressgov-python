#!/usr/bin/env python3
"""
Patch generated client modules where OpenAPI schema implies a list body but
Congress.gov returns an envelope dict.

Middleware reads ``response.content`` via ``ApiEnvelope``; broken generated
parsers iterate envelope keys and crash. This script runs after every
``generate-client`` promotion.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Legacy congress modules used a fixed block; kept for tests that reference it.
CONGRESS_ENVELOPE_PATCHES: tuple[tuple[str, str], ...] = (
    ("congress/get_congress.py", '{"committeePrints": [...]}'),
    ("congress/get_congress_congress.py", '{"congress": {...}}'),
    ("congress/get_congress_current.py", '{"congress": {...}}'),
)

# List endpoints: eager from_dict on full envelope before services use ApiEnvelope.
EAGER_ENVELOPE_PATCHES: tuple[str, ...] = (
    "treaty/get_treaty.py",
    "treaty/get_treaty_congress.py",
    "house_vote/get_house_vote.py",
    "house_vote/get_house_vote_congress.py",
)

BROKEN_200_BLOCK = """    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_congresses_item_data in _response_200:
            componentsschemas_congresses_item = Congress.from_dict(componentsschemas_congresses_item_data)

            response_200.append(componentsschemas_congresses_item)

        return response_200"""

_FIXED_200_BLOCK = """    if response.status_code == 200:
        # Congress.gov returns an envelope dict; congressgov.services parses
        # response.content via ApiEnvelope. Generated list iteration fails.
        return None"""

# openapi-python-client: multiline from_dict in list loop.
_LIST_ITERATION_200 = re.compile(
    r"    if response\.status_code == 200:\n"
    r"        response_200 = \[\]\n"
    r"        _response_200 = response\.json\(\)\n"
    r"        for \w+ in _response_200:\n"
    r"            \w+ = \w+\.from_dict\(\n"
    r"                \w+\n"
    r"            \)\n\n"
    r"            response_200\.append\(\w+\)\n\n"
    r"        return response_200",
)

# Single-line from_dict in list loop (hearing, summaries, etc.).
_LIST_ITERATION_200_ONELINE = re.compile(
    r"    if response\.status_code == 200:\n"
    r"        response_200 = \[\]\n"
    r"        _response_200 = response\.json\(\)\n"
    r"        for \w+ in _response_200:\n"
    r"            \w+ = \w+\.from_dict\(\w+\)\n\n"
    r"            response_200\.append\(\w+\)\n\n"
    r"        return response_200",
)

_EAGER_FROM_DICT_200 = re.compile(
    r"    if response\.status_code == 200:\n"
    r"        response_200 = \w+\.from_dict\(response\.json\(\)\)\n\n"
    r"        return response_200",
)


def _fixed_200_block(envelope_comment: str | None = None) -> str:
    if envelope_comment:
        return f"""    if response.status_code == 200:
        # Congress.gov returns an envelope (e.g. {envelope_comment}); congressgov.services
        # parses response.content via ApiEnvelope. Generated list iteration fails.
        return None"""
    return _FIXED_200_BLOCK


def patch_list_iteration_envelope_parsers(client_root: Path) -> list[Path]:
    """Replace broken list-iteration _parse_response blocks under api/."""
    api_root = client_root / "api"
    if not api_root.is_dir():
        return []
    patched: list[Path] = []
    for module_path in sorted(api_root.rglob("get_*.py")):
        text = module_path.read_text(encoding="utf-8")
        if "Generated list iteration fails" in text:
            continue
        new_text = text
        for pattern in (_LIST_ITERATION_200, _LIST_ITERATION_200_ONELINE):
            new_text, count = pattern.subn(_FIXED_200_BLOCK, new_text, count=1)
            if count:
                break
        if new_text != text:
            module_path.write_text(new_text, encoding="utf-8")
            patched.append(module_path)
    return patched


def patch_eager_envelope_parsers(client_root: Path) -> list[Path]:
    """Skip eager from_dict on list endpoints; services parse via ApiEnvelope."""
    api_root = client_root / "api"
    patched: list[Path] = []
    for rel_path in EAGER_ENVELOPE_PATCHES:
        module_path = api_root / rel_path
        if not module_path.is_file():
            continue
        text = module_path.read_text(encoding="utf-8")
        if "Generated eager from_dict fails" in text:
            continue
        new_text, count = _EAGER_FROM_DICT_200.subn(
            """    if response.status_code == 200:
        # Congress.gov returns an envelope dict; congressgov.services parses
        # response.content via ApiEnvelope. Generated eager from_dict fails.
        return None""",
            text,
            count=1,
        )
        if count and new_text != text:
            module_path.write_text(new_text, encoding="utf-8")
            patched.append(module_path)
    return patched


def patch_congress_envelope_parsers(client_root: Path) -> list[Path]:
    """Replace legacy fixed-string congress blocks (pre-regex promotion)."""
    api_root = client_root / "api"
    patched: list[Path] = []
    for rel_path, envelope_comment in CONGRESS_ENVELOPE_PATCHES:
        module_path = api_root / rel_path
        if not module_path.is_file():
            continue
        text = module_path.read_text(encoding="utf-8")
        if BROKEN_200_BLOCK not in text:
            continue
        new_text = text.replace(BROKEN_200_BLOCK, _fixed_200_block(envelope_comment), 1)
        if new_text != text:
            module_path.write_text(new_text, encoding="utf-8")
            patched.append(module_path)
    return patched


def patch_all_envelope_parsers(client_root: Path) -> list[Path]:
    """Apply congress legacy patches, list-iteration fixes, and eager from_dict fixes."""
    seen: set[Path] = set()
    patched: list[Path] = []
    for path in (
        patch_congress_envelope_parsers(client_root)
        + patch_list_iteration_envelope_parsers(client_root)
        + patch_eager_envelope_parsers(client_root)
    ):
        if path not in seen:
            seen.add(path)
            patched.append(path)
    return patched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-root",
        type=Path,
        default=Path("src/congressgov/_client"),
        help="Root of the generated congressgov._client package",
    )
    args = parser.parse_args(argv)
    client_root = args.client_root.resolve()
    if not client_root.is_dir():
        print(f"Client root not found: {client_root}", file=sys.stderr)
        return 1
    patched = patch_all_envelope_parsers(client_root)
    for path in patched:
        print(f"Patched {path.relative_to(client_root.parent.parent)}")
    print(f"Patched {len(patched)} client module(s) for envelope parsers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
