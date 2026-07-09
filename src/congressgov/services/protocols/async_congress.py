"""Protocol hints for async Congress extension methods."""

from __future__ import annotations

from typing import Any, Protocol


class AsyncCongressProtocol(Protocol):
    async def get_members_async(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        current_member: bool | None = None,
        fetch_all: bool = False,
    ) -> Any: ...
