#!/usr/bin/env python3
"""
Patch generated client _get_kwargs so format_=None (or str) does not crash.

openapi-python-client emits ``format_.value``; middleware passes format_=None when
callers omit the parameter. Coerce None/str to the endpoint's JSON enum member.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_FORMAT_PARAM = re.compile(
    r"format_:\s*Union\[[\s\S]*?,\s*([A-Za-z][A-Za-z0-9_]*)\s*\]",
)
_FORMAT_IMPORT = re.compile(
    r"from \.\.\.models\.([a-z0-9_]+) import ([A-Za-z][A-Za-z0-9_]*)",
)
_OLD_BLOCK = """    json_format_: Union[Unset, str] = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value"""
_NEW_BLOCK_TEMPLATE = """    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = {enum_cls}.JSON
    elif isinstance(format_, str):
        format_ = {enum_cls}(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value"""


def _format_enum_for_file(text: str) -> str | None:
    match = _FORMAT_PARAM.search(text)
    if match:
        return match.group(1)
    for import_match in _FORMAT_IMPORT.finditer(text):
        if import_match.group(1).endswith("_format"):
            return import_match.group(2)
    return None


def patch_format_in_get_kwargs(module_path: Path) -> bool:
    text = module_path.read_text(encoding="utf-8")
    if _OLD_BLOCK not in text:
        return False
    enum_cls = _format_enum_for_file(text)
    if not enum_cls:
        return False
    new_block = _NEW_BLOCK_TEMPLATE.format(enum_cls=enum_cls)
    new_text = text.replace(_OLD_BLOCK, new_block, 1)
    if new_text == text:
        return False
    module_path.write_text(new_text, encoding="utf-8")
    return True


def patch_all_client_format_kwargs(client_root: Path) -> list[Path]:
    api_root = client_root / "api"
    if not api_root.is_dir():
        return []
    patched: list[Path] = []
    for module_path in sorted(api_root.rglob("get_*.py")):
        if patch_format_in_get_kwargs(module_path):
            patched.append(module_path)
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
    patched = patch_all_client_format_kwargs(client_root)
    for path in patched:
        print(f"Patched {path.relative_to(client_root.parent.parent)}")
    print(f"Patched {len(patched)} client module(s) for format_=None")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
