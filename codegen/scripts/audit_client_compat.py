#!/usr/bin/env python3
"""Audit legacy client compat: aliases vs exports and entity_mappings api_function_mappings."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from codegen.scripts.emit_client_compat import (
    DEFAULT_ALIASES,
    DEFAULT_CLIENT,
    alias_signature,
    detect_sync_exports,
    index_modules_by_url,
)

INIT_EXPORT_RE = re.compile(r'^\s*"([^"]+)"', re.MULTILINE)
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
ENTITY_MAPPINGS = CONFIG_DIR / "entity_mappings.yaml"


def parse_init_all_exports(init_path: Path) -> set[str]:
    if not init_path.is_file():
        return set()
    text = init_path.read_text(encoding="utf-8")
    if "__all__" not in text:
        return set()
    block = text.split("__all__", 1)[1]
    if "[" not in block:
        return set()
    block = block.split("[", 1)[1].split("]", 1)[0]
    return set(INIT_EXPORT_RE.findall(block))


def load_api_function_mappings() -> dict[str, dict[str, str]]:
    if not ENTITY_MAPPINGS.is_file():
        return {}
    data = yaml.safe_load(ENTITY_MAPPINGS.read_text(encoding="utf-8")) or {}
    raw = data.get("api_function_mappings", {})
    return {k: v for k, v in raw.items() if isinstance(v, dict)}


def audit(client_root: Path, aliases_path: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    data = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}
    packages: dict = data.get("packages", {})
    api_root = client_root / "api"

    sig_to_aliases: dict[str, list[str]] = defaultdict(list)
    all_sync_aliases: set[str] = set()

    for package, aliases in packages.items():
        package_dir = api_root / package
        for alias in aliases:
            name = alias.get("legacy_name", "")
            if name.endswith("_sync"):
                all_sync_aliases.add(name)
            sig = alias_signature(alias, package_dir if package_dir.is_dir() else None)
            if sig:
                sig_to_aliases[sig].append(f"{package}.{name}")

    for sig, names in sig_to_aliases.items():
        if len(names) > 1:
            warnings.append(f"ambiguous alias signature {sig!r}: {', '.join(names)}")

    for package, aliases in packages.items():
        package_dir = api_root / package
        url_index = index_modules_by_url(package_dir) if package_dir.is_dir() else {}
        exports = parse_init_all_exports(api_root / package / "__init__.py")
        for alias in aliases:
            legacy = alias.get("legacy_name", "")
            if not legacy.endswith("_sync"):
                continue
            if legacy not in exports:
                errors.append(f"missing export {package}: {legacy} in __init__.py")
            sig = alias_signature(alias, package_dir)
            get_stem = url_index.get(sig) if sig else None
            source_module = alias.get("source_module", "")
            mod_path = package_dir / f"{source_module}.py" if source_module else None
            _, async_attr = detect_sync_exports(mod_path) if mod_path and mod_path.is_file() else (None, None)
            if not async_attr and get_stem:
                _, async_attr = detect_sync_exports(package_dir / f"{get_stem}.py")
            async_name = alias.get("legacy_async") or legacy.replace("_sync", "_async")
            if async_attr and async_name not in exports:
                errors.append(f"missing async export {package}: {async_name}")

    mappings = load_api_function_mappings()
    for entity, functions in mappings.items():
        for role, fn_name in functions.items():
            if fn_name not in all_sync_aliases:
                errors.append(
                    f"api_function_mappings.{entity}.{role}: {fn_name} not in legacy_client_aliases"
                )

    if warnings:
        print("AUDIT WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("AUDIT ISSUES:", file=sys.stderr)
        for issue in errors:
            print(f"  - {issue}", file=sys.stderr)
        return 1
    print("OK: client compat audit passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit legacy client compat coverage")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    args = parser.parse_args()
    if not args.aliases.exists():
        print(f"ERROR: {args.aliases} not found", file=sys.stderr)
        return 1
    return audit(args.client_root, args.aliases)


if __name__ == "__main__":
    raise SystemExit(main())
