"""CLI entry point — delegates to the workspace storage CLI."""

from __future__ import annotations

from congressgov.services.core.workspace.__main__ import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
