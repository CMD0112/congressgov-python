#!/usr/bin/env python3
"""
Build and apply legacy *_sync / *_async exports for congressgov._client.

After openapi-python-client regen, endpoint modules use get_* names and
sync/asyncio callables. Middleware still imports bill_details_sync, etc. from
package __init__ modules. This script rebuilds those __init__ files by matching
HTTP path signatures between pre-regen module names (in legacy_client_aliases.yaml)
and post-regen get_* modules.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})
URL_RE = re.compile(r'"url":\s*"([^"]+)"')
INIT_IMPORT_RE = re.compile(
    r"from\s+\.(\w+)\s+import\s+(\w+)\s+as\s+(\w+)",
)
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
LEGACY_VENDOR_DIR = Path(__file__).resolve().parents[1] / "data" / "legacy_api_modules"
DEFAULT_ALIASES = CONFIG_DIR / "legacy_client_aliases.yaml"
DEFAULT_CLIENT = Path("src/congressgov/_client")
# Packages that use get_* modules only (no vendor legacy .py restore)
PILOT_PACKAGES = frozenset({
    "bill",
    "amendments",
    "member",
    "committee",
    "hearing",
    "nomination",
    "treaty",
    "house_vote",
    "summaries",
    "crsreport",
    "house_communication",
    "senate_communication",
    "committee_meeting",
    "committee_report",
    "committee_print",
    "congress",
    "house_requirement",
    "congressional_record",
    "bound_congressional_record",
    "daily_congressional_record",
})


def path_signature(url_template: str) -> str:
    """Normalize URL template for matching (preserve param names for disambiguation)."""
    normalized = re.sub(r"/+", "/", url_template)
    return normalized.rstrip("/") or "/"


def alias_url_path(alias: dict[str, Any]) -> str:
    """Return the OpenAPI URL template for an alias (supports legacy url_signature)."""
    if path := alias.get("url_path"):
        return str(path)
    sig = alias.get("url_signature")
    if isinstance(sig, str) and sig and not sig.startswith("/"):
        return sig
    if isinstance(sig, str) and sig.startswith("/"):
        return sig
    return ""


def alias_signature(alias: dict[str, Any], package_dir: Path | None = None) -> str:
    """Resolve normalized signature for matching."""
    url_path = alias_url_path(alias)
    if url_path and "{" in url_path:
        return path_signature(url_path)
    if url_path:
        return path_signature(url_path)
    source_module = alias.get("source_module")
    if package_dir and source_module:
        module_path = package_dir / f"{source_module}.py"
        url = extract_url_from_module(module_path)
        if url:
            return path_signature(url)
    if isinstance(alias.get("url_signature"), str):
        return alias["url_signature"]
    return ""


def extract_url_from_module(module_path: Path) -> str | None:
    try:
        text = module_path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = URL_RE.search(text)
    return match.group(1) if match else None


def detect_sync_exports(module_path: Path) -> tuple[str | None, str | None]:
    """Return (sync_attr, async_attr) names exported from the module."""
    try:
        text = module_path.read_text(encoding="utf-8")
    except OSError:
        return None, None
    # Middleware parses json.loads(resp.content); prefer detailed Response objects.
    if re.search(r"^def sync_detailed\b", text, re.MULTILINE):
        sync_attr = "sync_detailed"
    elif re.search(r"^def sync\b", text, re.MULTILINE):
        sync_attr = "sync"
    else:
        sync_attr = None
    async_attr = None
    if re.search(r"^(?:async )?def asyncio_detailed\b", text, re.MULTILINE):
        async_attr = "asyncio_detailed"
    elif re.search(r"^(?:async )?def asyncio\b", text, re.MULTILINE):
        async_attr = "asyncio"
    return sync_attr, async_attr


def index_modules_by_url(api_package_dir: Path) -> dict[str, str]:
    """Map path_signature -> module stem for all endpoint modules in a package."""
    index: dict[str, str] = {}
    if not api_package_dir.is_dir():
        return index
    for module_path in sorted(api_package_dir.glob("*.py")):
        if module_path.name == "__init__.py":
            continue
        url = extract_url_from_module(module_path)
        if not url:
            continue
        sig = path_signature(url)
        if sig not in index or module_path.stem.startswith("get_"):
            index[sig] = module_path.stem
    return index


def parse_init_exports(init_path: Path) -> list[dict[str, str]]:
    """Parse legacy exports from an existing __init__.py."""
    if not init_path.is_file():
        return []
    entries: list[dict[str, str]] = []
    for line in init_path.read_text(encoding="utf-8").splitlines():
        match = INIT_IMPORT_RE.search(line)
        if not match:
            continue
        source_module, source_attr, legacy_name = match.groups()
        entries.append(
            {
                "source_module": source_module,
                "source_attr": source_attr,
                "legacy_name": legacy_name,
            }
        )
    return entries


def _dump_aliases_yaml(data: dict[str, Any]) -> str:
    """Write aliases YAML with quoted url_path (avoids {} mapping corruption)."""
    lines = ["# Auto-generated by: poetry run emit-client-compat --snapshot\n", "packages:\n"]
    for package in sorted(data.get("packages", {})):
        lines.append(f"  {package}:\n")
        for alias in data["packages"][package]:
            lines.append(f"  - legacy_name: {alias['legacy_name']}\n")
            lines.append(f"    source_module: {alias['source_module']}\n")
            lines.append(f"    source_attr: {alias['source_attr']}\n")
            url_path = alias.get("url_path") or alias_url_path(alias)
            lines.append(f'    url_path: "{url_path}"\n')
            if alias.get("legacy_async"):
                lines.append(f"    legacy_async: {alias['legacy_async']}\n")
        lines.append("\n")
    return "".join(lines)


def snapshot_aliases(client_root: Path, output_path: Path) -> int:
    """Write legacy_client_aliases.yaml from the current client tree."""
    api_root = client_root / "api"
    packages: dict[str, Any] = {}

    for package_dir in sorted(api_root.iterdir()):
        if not package_dir.is_dir():
            continue
        package = package_dir.name
        init_path = package_dir / "__init__.py"
        exports = parse_init_exports(init_path)
        if not exports:
            continue

        aliases: list[dict[str, str]] = []
        for entry in exports:
            module_path = package_dir / f"{entry['source_module']}.py"
            url = extract_url_from_module(module_path)
            if not url:
                continue
            alias_entry: dict[str, str] = {
                "legacy_name": entry["legacy_name"],
                "source_module": entry["source_module"],
                "source_attr": entry["source_attr"],
                "url_path": url,
            }
            _, mod_async = detect_sync_exports(module_path)
            get_stem = None
            sig = path_signature(url)
            for other in package_dir.glob("*.py"):
                if other.stem.startswith("get_"):
                    other_url = extract_url_from_module(other)
                    if other_url and path_signature(other_url) == sig:
                        get_stem = other.stem
                        break
            if not mod_async and get_stem:
                _, mod_async = detect_sync_exports(package_dir / f"{get_stem}.py")
            if mod_async and entry["legacy_name"].endswith("_sync"):
                alias_entry["legacy_async"] = entry["legacy_name"][: -len("_sync")] + "_async"
            aliases.append(alias_entry)

        if aliases:
            packages[package] = aliases

    data = {"packages": packages}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_dump_aliases_yaml(data), encoding="utf-8")
    total = sum(len(v) for v in packages.values())
    print(f"Wrote {output_path} ({total} aliases in {len(packages)} packages)")
    return 0


def vendor_legacy_modules(
    client_root: Path,
    vendor_root: Path = LEGACY_VENDOR_DIR,
    aliases_path: Path | None = None,
) -> int:
    """Copy legacy endpoint modules into codegen/data/legacy_api_modules for offline restore."""
    api_root = client_root / "api"
    copied = 0
    stems_by_package: dict[str, set[str]] = {}

    if aliases_path and aliases_path.exists():
        data = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}
        for package, aliases in data.get("packages", {}).items():
            stems_by_package.setdefault(package, set())
            for alias in aliases:
                stem = alias.get("source_module")
                if stem:
                    stems_by_package[package].add(stem)

    for package_dir in sorted(api_root.iterdir()):
        if not package_dir.is_dir():
            continue
        package = package_dir.name
        wanted = stems_by_package.get(package)
        for module_path in sorted(package_dir.glob("*.py")):
            if module_path.name == "__init__.py":
                continue
            if module_path.stem.startswith("get_"):
                continue
            if wanted is not None and module_path.stem not in wanted:
                continue
            dest = vendor_root / package / module_path.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(module_path, dest)
            copied += 1

    print(f"Vendored {copied} legacy modules to {vendor_root}")
    return 0


def _write_wrapper_module(
    target: Path,
    get_module: str,
    sync_attr: str,
    async_attr: str | None,
) -> None:
    """Thin wrapper re-exporting get_* callables under a legacy module stem."""
    lines = [
        '"""Legacy-compat wrapper; delegates to regen get_* module."""',
        "from __future__ import annotations",
        "",
        f"from .{get_module} import {sync_attr} as sync_detailed",
        "",
    ]
    if async_attr:
        lines.append(f"from .{get_module} import {async_attr} as asyncio_detailed")
        lines.append("")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prune_pilot_legacy_duplicates(client_root: Path) -> list[str]:
    """Remove non-get_* endpoint modules from pilot API packages."""
    removed: list[str] = []
    api_root = client_root / "api"
    for package in sorted(PILOT_PACKAGES):
        package_dir = api_root / package
        if not package_dir.is_dir():
            continue
        for module_path in sorted(package_dir.glob("*.py")):
            if module_path.name == "__init__.py" or module_path.stem.startswith("get_"):
                continue
            module_path.unlink()
            removed.append(str(module_path.relative_to(client_root.parent)))
    return removed


def restore_missing_modules(
    client_root: Path,
    aliases_path: Path,
    vendor_root: Path = LEGACY_VENDOR_DIR,
) -> list[str]:
    """Restore legacy endpoint modules from vendor tree or generate get_* wrappers."""
    if not aliases_path.exists():
        return []
    data = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}
    packages: dict[str, list] = data.get("packages", {})
    api_root = client_root / "api"
    restored: list[str] = []

    for package, aliases in packages.items():
        package_dir = api_root / package
        if not package_dir.is_dir():
            continue
        url_index = index_modules_by_url(package_dir)
        for alias in aliases:
            legacy_name = alias.get("legacy_name", "")
            if not legacy_name.endswith("_sync"):
                continue
            sig = alias_signature(alias, package_dir)
            source_module = alias.get("source_module")
            if not sig or not source_module or sig in url_index:
                continue
            target = package_dir / f"{source_module}.py"
            if target.exists():
                continue

            vendor_file = vendor_root / package / f"{source_module}.py"
            if vendor_file.is_file() and package not in PILOT_PACKAGES:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(vendor_file, target)
                restored.append(str(target.relative_to(client_root.parent)))
                continue

            get_module = url_index.get(sig)
            if get_module and get_module.startswith("get_"):
                if package in PILOT_PACKAGES:
                    continue
                module_path = package_dir / f"{get_module}.py"
                sync_attr, async_attr = detect_sync_exports(module_path)
                if sync_attr:
                    _write_wrapper_module(target, get_module, sync_attr, async_attr)
                    restored.append(str(target.relative_to(client_root.parent)))

    return restored


def emit_package_init(
    package_dir: Path,
    aliases: list[dict[str, Any]],
    url_index: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Build __init__.py lines for one API package. Returns (lines, warnings)."""
    lines = [
        '"""Contains endpoint functions for accessing the API (compat re-exports)."""',
        "# isort: skip_file",
        "",
    ]
    all_exports: list[str] = []
    warnings: list[str] = []

    # (sync_module, sync_attr, legacy_sync, async_module, async_attr)
    sync_pairs: list[tuple[str, str, str, str, str]] = []
    async_by_sync: dict[str, str] = {}

    for alias in aliases:
        legacy_name = alias["legacy_name"]
        if legacy_name.endswith("_async"):
            continue
        if not legacy_name.endswith("_sync"):
            warnings.append(f"{package_dir.name}: skip non-sync alias {legacy_name}")
            continue

        sig = alias_signature(alias, package_dir)
        if not sig:
            warnings.append(f"{package_dir.name}: missing url_path for {legacy_name}")
            continue

        source_module = alias.get("source_module", "")
        get_stem = url_index.get(sig)
        if get_stem and get_stem.startswith("get_"):
            new_module = get_stem
        elif source_module and (package_dir / f"{source_module}.py").exists():
            new_module = source_module
        else:
            new_module = get_stem
        if not new_module:
            warnings.append(
                f"{package_dir.name}: no module for {legacy_name} (sig={sig!r})"
            )
            continue

        module_path = package_dir / f"{new_module}.py"
        sync_attr, async_attr = detect_sync_exports(module_path)
        yaml_attr = alias.get("source_attr")
        # Middleware reads response.content; never downgrade sync_detailed -> sync.
        if sync_attr == "sync_detailed":
            pass
        elif yaml_attr:
            sync_attr = yaml_attr
        if not sync_attr:
            warnings.append(f"{package_dir.name}: no sync in {new_module}.py for {legacy_name}")
            continue

        async_module = new_module
        async_attr_use = async_attr or ""
        if not async_attr_use and get_stem and get_stem.startswith("get_"):
            _, get_async = detect_sync_exports(package_dir / f"{get_stem}.py")
            if get_async:
                async_module = get_stem
                async_attr_use = get_async

        sync_pairs.append((new_module, sync_attr, legacy_name, async_module, async_attr_use))
        async_legacy = alias.get("legacy_async") or legacy_name.replace("_sync", "_async")
        if async_attr_use:
            async_by_sync[legacy_name] = async_legacy

    sync_pairs.sort(key=lambda pair: pair[2])

    for sync_module, sync_attr, legacy_sync, _, _ in sync_pairs:
        lines.append(f"from .{sync_module} import {sync_attr} as {legacy_sync}")
        all_exports.append(legacy_sync)

    lines.append("")
    for _, _, legacy_sync, async_module, async_attr in sync_pairs:
        if not async_attr:
            continue
        async_legacy = async_by_sync.get(legacy_sync)
        if not async_legacy:
            continue
        lines.append(f"from .{async_module} import {async_attr} as {async_legacy}")
        all_exports.append(async_legacy)

    lines.append("")
    lines.append("# Backward compatibility aliases (without _sync suffix)")
    for legacy_sync in [p[2] for p in sync_pairs]:
        short = legacy_sync[: -len("_sync")] if legacy_sync.endswith("_sync") else legacy_sync
        lines.append(f"{short} = {legacy_sync}")
        all_exports.append(short)

    lines.extend(["", "__all__ = [", *[f'    "{name}",' for name in all_exports], "]", ""])
    return lines, warnings


def emit_compat(
    client_root: Path,
    aliases_path: Path,
    allow_unmatched: bool = False,
) -> int:
    if not aliases_path.exists():
        print(f"ERROR: {aliases_path} not found. Run with --snapshot first.", file=sys.stderr)
        return 1

    restored = restore_missing_modules(client_root, aliases_path)
    for path in restored:
        print(f"Restored {path}")

    pruned = prune_pilot_legacy_duplicates(client_root)
    for path in pruned:
        print(f"Pruned pilot duplicate {path}")

    data = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}
    packages: dict[str, list] = data.get("packages", {})
    api_root = client_root / "api"
    all_warnings: list[str] = []

    for package, aliases in sorted(packages.items()):
        package_dir = api_root / package
        if not package_dir.is_dir():
            all_warnings.append(f"package directory missing: {package}")
            continue
        url_index = index_modules_by_url(package_dir)
        lines, warnings = emit_package_init(package_dir, aliases, url_index)
        all_warnings.extend(warnings)
        init_path = package_dir / "__init__.py"
        init_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Updated {init_path}")

    if all_warnings:
        print("WARNINGS:", file=sys.stderr)
        for warning in all_warnings:
            print(f"  - {warning}", file=sys.stderr)
        if allow_unmatched:
            print("Continuing (--allow-unmatched).", file=sys.stderr)
            return 0
    return 1 if all_warnings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Legacy client import compatibility")
    parser.add_argument(
        "--client-root",
        type=Path,
        default=DEFAULT_CLIENT,
        help="Path to congressgov._client package root",
    )
    parser.add_argument(
        "--aliases",
        type=Path,
        default=DEFAULT_ALIASES,
        help="Path to legacy_client_aliases.yaml",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Snapshot current client into legacy_client_aliases.yaml",
    )
    parser.add_argument(
        "--vendor-legacy",
        action="store_true",
        help="Copy legacy endpoint modules to codegen/data/legacy_api_modules",
    )
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Warn on unmatched aliases but exit 0",
    )
    args = parser.parse_args()

    if args.snapshot:
        return snapshot_aliases(args.client_root, args.aliases)
    if args.vendor_legacy:
        return vendor_legacy_modules(args.client_root, aliases_path=args.aliases)
    return emit_compat(args.client_root, args.aliases, allow_unmatched=args.allow_unmatched)


if __name__ == "__main__":
    raise SystemExit(main())
