"""Async protocol declarations for Bill extension methods."""

from __future__ import annotations

from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bill
    from congressgov.models.actions.action import Actions


class AsyncBillProtocol(Protocol):
    async def expand_async(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any,
    ) -> Bill: ...

    async def expand_specific_attributes_async(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any,
    ) -> Bill: ...

    async def get_actions_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Actions: ...

    async def get_amendments_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_committees_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_cosponsors_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_related_bills_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_subjects_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_summaries_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_text_versions_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...

    async def get_titles_async(
        self, client: Any = None, format_: str | None = None, **kwargs: Any
    ) -> Any: ...
