"""Tests for member list pagination helpers."""

from __future__ import annotations

from congressgov.models.entities.member import Member, Members
from congressgov.services.core.member_list_pagination import paginate_members


def _page(members: list[Member], *, client=None) -> Members:
    result = Members(members=members)
    result.client = client
    return result


def test_paginate_members_single_page() -> None:
    pages = [_page([Member(bioguideId="A000374")])]
    calls: list[tuple[int, int]] = []

    def fetch(offset: int, limit: int) -> Members:
        calls.append((offset, limit))
        return pages.pop(0)

    result = paginate_members(fetch, page_size=250)
    assert calls == [(0, 250)]
    assert len(result.members) == 1


def test_paginate_members_multiple_pages() -> None:
    full = [Member(bioguideId=f"M{i:03d}") for i in range(250)]
    tail = [Member(bioguideId="Z000001")]
    queue = [_page(full), _page(tail)]
    calls: list[tuple[int, int]] = []

    def fetch(offset: int, limit: int) -> Members:
        calls.append((offset, limit))
        return queue.pop(0)

    result = paginate_members(fetch, page_size=250)
    assert calls == [(0, 250), (250, 250)]
    assert len(result.members) == 251
