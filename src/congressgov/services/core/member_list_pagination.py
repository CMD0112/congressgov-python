"""Paginate member list API responses into a single ``Members`` collection."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from congressgov.models.entities.member import Members as MembersModel
from congressgov.services.config import MAX_PAGINATION_LIMIT
from congressgov.services.core.expansion_helpers import propagate_client_to_items


def _normalize_page_size(page_size: int | None) -> int:
    size = page_size if page_size is not None else MAX_PAGINATION_LIMIT
    return min(max(size, 1), MAX_PAGINATION_LIMIT)


def _merge_pages(pages: list[MembersModel]) -> MembersModel:
    combined: list = []
    client = None
    for page in pages:
        if client is None:
            client = getattr(page, "client", None)
        if page.members:
            combined.extend(page.members)
    result = MembersModel(members=combined)
    if client is not None:
        result.client = client
        propagate_client_to_items(result, "members", client)
    return result


def paginate_members(
    fetch_page: Callable[[int, int], MembersModel],
    *,
    page_size: int | None = None,
) -> MembersModel:
    """
    Fetch member list pages until a short or empty page is returned.

    Args:
        fetch_page: ``(offset, limit) -> Members`` for one API page.
        page_size: Records per request (clamped to ``MAX_PAGINATION_LIMIT``).
    """
    size = _normalize_page_size(page_size)
    pages: list[MembersModel] = []
    offset = 0

    while True:
        page = fetch_page(offset, size)
        members = page.members or []
        if not members:
            break
        pages.append(page)
        if len(members) < size:
            break
        offset += size

    return _merge_pages(pages)


async def paginate_members_async(
    fetch_page: Callable[[int, int], Awaitable[MembersModel]],
    *,
    page_size: int | None = None,
) -> MembersModel:
    """Async variant of :func:`paginate_members`."""
    size = _normalize_page_size(page_size)
    pages: list[MembersModel] = []
    offset = 0

    while True:
        page = await fetch_page(offset, size)
        members = page.members or []
        if not members:
            break
        pages.append(page)
        if len(members) < size:
            break
        offset += size

    return _merge_pages(pages)
