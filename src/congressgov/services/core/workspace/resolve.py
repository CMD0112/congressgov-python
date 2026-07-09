"""Resolve workspace paths and default blob-store connections."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from .paths import CONGRESS_REQUEST_STORE_ENV, WorkspacePaths, default_workspace_root

logger = logging.getLogger(__name__)


def resolve_workspace(root: str | Path | None = None) -> WorkspacePaths:
    """Build :class:`WorkspacePaths` for *root* or the default workspace."""
    if root is None:
        resolved = default_workspace_root()
    else:
        resolved = Path(root).expanduser().resolve()
    return WorkspacePaths(root=resolved)


def resolve_blob_connection(
    *,
    workspace: WorkspacePaths | None = None,
    override: str | None = None,
) -> str:
    """
    Return the blob-lane connection string.

    Precedence:
    1. Explicit *override* or ``CONGRESS_REQUEST_STORE`` env var
    2. Workspace API database (``api/request_store.db``)
    3. Legacy flat ``.congressgov/request_store.db`` when it exists
    """
    explicit = override or os.environ.get(CONGRESS_REQUEST_STORE_ENV)
    if explicit:
        return explicit

    paths = workspace or resolve_workspace()
    if paths.api_db.exists():
        return paths.api_db_url

    legacy = paths.legacy_api_db()
    if legacy.exists():
        logger.info(
            "Using legacy request store at %s. "
            "New workspaces use %s (set CONGRESS_WORKSPACE to relocate).",
            legacy,
            paths.api_db,
        )
        return f"sqlite:///{legacy.as_posix()}"

    return paths.api_db_url


def migrate_legacy_blob_if_needed(paths: WorkspacePaths) -> bool:
    """
    Copy a legacy flat ``request_store.db`` into ``api/request_store.db``.

    Returns True when a migration was performed.
    """
    legacy = paths.legacy_api_db()
    if not legacy.exists() or paths.api_db.exists():
        return False
    paths.api_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy, paths.api_db)
    logger.info(
        "Migrated legacy request store from %s to %s",
        legacy,
        paths.api_db,
    )
    return True


def maybe_log_legacy_migration(paths: WorkspacePaths) -> None:
    """Migrate or log when the legacy flat DB exists but the workspace API path does not."""
    if migrate_legacy_blob_if_needed(paths):
        return
    legacy = paths.legacy_api_db()
    if legacy.exists() and not paths.api_db.exists():
        logger.info(
            "Legacy request store found at %s. "
            "Future releases prefer %s under the workspace layout.",
            legacy,
            paths.api_db,
        )
