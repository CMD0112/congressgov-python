"""Ensure repo-root ``codegen`` and ``src/congressgov`` are importable in all test runs."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
for path in (_REPO_ROOT, _REPO_ROOT / "src"):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
