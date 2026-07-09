"""Async protocol declarations for Member extension methods."""

from __future__ import annotations

from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class AsyncMemberProtocol(Protocol):
    async def expand_async(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any,
    ) -> Any: ...

    async def expand_specific_attributes_async(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any,
    ) -> Any: ...

    async def get_available_attributes_async(self) -> list[str]: ...

    async def get_sponsored_legislation_async(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        refresh: bool = False,
        **kwargs: Any,
    ) -> Any: ...

    async def get_cosponsored_legislation_async(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        refresh: bool = False,
        **kwargs: Any,
    ) -> Any: ...
