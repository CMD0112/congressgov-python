"""Async instance methods for the Congress model."""

from __future__ import annotations

from typing import Any

from congressgov.models.entities.congress import Congress
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.extensions.congress import _resolve_congress_number


@register_async_method(Congress)
async def get_members_async(
    self: Congress,
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    *,
    current_member: bool | None = None,
    fetch_all: bool = False,
) -> Any:
    """Async version of ``Congress.get_members()``."""
    congress_number = _resolve_congress_number(self)
    from congressgov.services.async_api.member import AsyncMember

    resolved_client = await AsyncApiService._resolve_client(self, client)
    return await AsyncMember(client=resolved_client).list_by_congress(
        client=client,
        congress=congress_number,
        format_=format_,
        offset=offset,
        limit=limit,
        current_member=current_member,
        fetch_all=fetch_all,
    )
