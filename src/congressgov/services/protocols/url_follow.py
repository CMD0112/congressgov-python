"""Protocol hints for URL-based fetch extension methods."""

from __future__ import annotations

from typing import Any, Protocol


class UrlFetchProtocol(Protocol):
    def fetch(
        self,
        client: Any = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> Any: ...


class MemberUrlFetchProtocol(Protocol):
    def fetch_member(
        self,
        client: Any = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> Any: ...
