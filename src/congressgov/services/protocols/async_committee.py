"""Async protocol declarations for Committee extension methods."""

from __future__ import annotations

from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from congressgov.models.committees.committee import Committee


class AsyncCommitteeProtocol(Protocol):
    async def expand_async(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any,
    ) -> Committee: ...

    async def get_bills_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_reports_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_house_communications_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_senate_communications_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_nominations_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...
