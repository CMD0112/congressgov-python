"""Guard against legacy ``middleware`` import paths in shipped source."""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src" / "congressgov"

LEGACY_DOTTED_PATH = re.compile(r"""['"]middleware\.""")


_SKIP_AST_FILES = {"_template.py"}


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.py") if p.is_file() and p.name not in _SKIP_AST_FILES
    )


def test_no_legacy_middleware_dotted_paths_in_src() -> None:
    violations: list[str] = []
    for path in _iter_py_files(SRC_ROOT):
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if LEGACY_DOTTED_PATH.search(line):
                violations.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()}")
    assert not violations, "Legacy middleware.* string paths found:\n" + "\n".join(violations)


def test_no_executable_import_middleware_in_src() -> None:
    violations: list[str] = []
    for path in _iter_py_files(SRC_ROOT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "middleware" or alias.name.startswith("middleware."):
                        violations.append(
                            f"{path.relative_to(REPO_ROOT)}:{node.lineno}: import {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and (
                    node.module == "middleware" or node.module.startswith("middleware.")
                ):
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}: from {node.module} import ..."
                    )
    assert not violations, "Executable middleware imports found:\n" + "\n".join(violations)


def test_search_registry_has_no_middleware_paths() -> None:
    from congressgov.services.core.search import _SEARCH_REGISTRY

    for resource_type, config in _SEARCH_REGISTRY.items():
        module_path = config["module"]
        assert module_path.startswith("congressgov."), (
            f"{resource_type} registry path must be under congressgov: {module_path!r}"
        )
        assert "middleware" not in module_path, (
            f"{resource_type} still uses legacy path: {module_path!r}"
        )
