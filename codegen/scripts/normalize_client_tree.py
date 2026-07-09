"""Normalize generated client import order for deterministic CI drift checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import isort

RUFF_CONFIG = Path(__file__).resolve().parents[1] / "config" / "ruff_generated_client.toml"


def normalize_client_imports(client_root: Path, *, repo_root: Path | None = None) -> None:
    """Sort imports with isort and run ruff format/check on the generated client tree."""
    if not client_root.is_dir():
        return

    for py_file in sorted(client_root.rglob("*.py")):
        # Compat __init__ files: keep sync block then async block (isort would interleave).
        if py_file.name == "__init__.py" and "api" in py_file.parts:
            continue
        text = py_file.read_text(encoding="utf-8")
        py_file.write_text(
            isort.code(text, profile="black", line_length=120),
            encoding="utf-8",
        )

    if not RUFF_CONFIG.is_file():
        return

    root = repo_root or Path(__file__).resolve().parents[2]
    for target in (client_root / "api", client_root / "models"):
        if not target.is_dir():
            continue
        # Format endpoint modules only; compat api/*/__init__.py keeps emit order.
        ruff_paths = [
            str(p)
            for p in target.rglob("*.py")
            if not (p.name == "__init__.py" and target.name == "api")
        ]
        if not ruff_paths:
            continue
        subprocess.run(
            ["ruff", "format", *ruff_paths, "--config", str(RUFF_CONFIG)],
            cwd=root,
            check=False,
        )
        subprocess.run(
            ["ruff", "check", *ruff_paths, "--fix", "--config", str(RUFF_CONFIG)],
            cwd=root,
            check=False,
        )
