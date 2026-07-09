"""Protocol hints for Congress extension methods."""

from __future__ import annotations

from typing import Any, Protocol


class CongressProtocol(Protocol):
    def get_members(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        current_member: bool | None = None,
        fetch_all: bool = False,
    ) -> Any: ...
