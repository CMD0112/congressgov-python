"""Filesystem layout for the Congress.gov project workspace."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

CONGRESS_WORKSPACE_ENV = "CONGRESS_WORKSPACE"
CONGRESS_REQUEST_STORE_ENV = "CONGRESS_REQUEST_STORE"
DEFAULT_WORKSPACE_NAME = ".congressgov"
LEGACY_API_DB_NAME = "request_store.db"
CONFIG_FILENAME = "config.yaml"


@dataclass(frozen=True, slots=True)
class WorkspacePaths:
    """Resolved paths under a single workspace root."""

    root: Path

    @property
    def api_dir(self) -> Path:
        return self.root / "api"

    @property
    def api_db(self) -> Path:
        return self.api_dir / LEGACY_API_DB_NAME

    @property
    def api_db_url(self) -> str:
        return f"sqlite:///{self.api_db.as_posix()}"

    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"

    @property
    def graphs_dir(self) -> Path:
        return self.datasets_dir / "graphs"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def cache_dir(self) -> Path:
        return self.root / "cache"

    @property
    def config_file(self) -> Path:
        return self.root / CONFIG_FILENAME

    def graph_path(self, congress: int) -> Path:
        return self.graphs_dir / f"{congress}.json"

    def legacy_api_db(self) -> Path:
        """Pre-workspace blob store path (``.congressgov/request_store.db``)."""
        return self.root / LEGACY_API_DB_NAME

    def ensure_dirs(self) -> None:
        for directory in (
            self.api_dir,
            self.datasets_dir,
            self.graphs_dir,
            self.exports_dir,
            self.cache_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


def default_workspace_root() -> Path:
    """Return the workspace root from ``CONGRESS_WORKSPACE`` or ``./.congressgov``."""
    return Path(os.environ.get(CONGRESS_WORKSPACE_ENV, DEFAULT_WORKSPACE_NAME)).expanduser().resolve()
