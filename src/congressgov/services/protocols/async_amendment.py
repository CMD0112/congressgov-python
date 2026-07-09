"""Async protocol declarations for Amendment extension methods."""

from __future__ import annotations

from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from congressgov.models.entities.amendment import Amendment
    from congressgov.models.actions.action import Actions


class AsyncAmendmentProtocol(Protocol):
    async def expand_async(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any,
    ) -> Amendment: ...

    async def get_actions_async(
        self, client: Any = None, **kwargs: Any
    ) -> Actions: ...

    async def get_amendments_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_cosponsors_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...

    async def get_text_versions_async(
        self, client: Any = None, **kwargs: Any
    ) -> Any: ...
