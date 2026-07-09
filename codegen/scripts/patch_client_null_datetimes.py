#!/usr/bin/env python3
"""
Patch generated client models where nullable JSON dates are passed to isoparse.

Congress.gov may return null for optional date fields; openapi-python-client
only checks Unset, not None.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# idempotent: patched blocks include "or _var is None"
_ISOPARSE_ELSE_BLOCK = re.compile(
    r"(        if isinstance\((_\w+), Unset\):\n"
    r"            (\w+) = UNSET\n"
    r"        else:\n"
    r"            \3 = isoparse\(\2\)(?:\.date\(\))?)",
    re.MULTILINE,
)


def patch_null_datetime_fields(client_root: Path) -> list[Path]:
    """Add None checks before isoparse in generated model from_dict methods."""
    models_root = client_root / "models"
    if not models_root.is_dir():
        return []
    patched: list[Path] = []
    for module_path in sorted(models_root.rglob("*.py")):
        text = module_path.read_text(encoding="utf-8")
        if "or _" in text and " is None:" in text and "isoparse" in text:
            # Heuristic: skip files already fully patched in this pass
            pass

        def _repl(match: re.Match[str]) -> str:
            var = match.group(2)
            if f"or {var} is None" in match.group(0):
                return match.group(0)
            return (
                f"        if isinstance({var}, Unset) or {var} is None:\n"
                f"            {match.group(3)} = UNSET\n"
                f"        else:\n"
                f"            {match.group(3)} = isoparse({var})"
                + (".date()" if match.group(0).rstrip().endswith(".date())") else "")
            )

        new_text, count = _ISOPARSE_ELSE_BLOCK.subn(_repl, text)
        if count and new_text != text:
            module_path.write_text(new_text, encoding="utf-8")
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
    patched = patch_null_datetime_fields(client_root)
    for path in patched:
        print(f"Patched {path.relative_to(client_root.parent.parent)}")
    print(f"Patched {len(patched)} model file(s) for null datetimes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
