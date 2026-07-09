"""Instance methods for the Congress model."""

from __future__ import annotations

from typing import Any

from congressgov.models.entities.congress import Congress, infer_congress_number
from congressgov.services.core.api_service import ApiService
from congressgov.services.extensions._registry import register_method


def _resolve_congress_number(instance: Congress) -> int:
    """Read the Congress session number from model fields, inferring when needed.

    Deliberately backfills ``instance.number`` when it was inferred from
    ``name``/``url`` (see ``test_congress_get_members_infers_from_name`` /
    ``_infers_from_url``), so later reads of ``congress.number`` reflect the
    resolved value instead of staying ``None``.
    """
    if instance.number is None:
        inferred = infer_congress_number(
            number=instance.number,
            congress=instance.congress,
            name=instance.name,
            url=instance.url,
        )
        if inferred is not None:
            instance.number = inferred
    if instance.number is None:
        raise ValueError(
            "Congress.number (or Congress.congress) is required to fetch members; "
            "could not infer from name or url"
        )
    return instance.number


@register_method(Congress)
def get_members(
    self: Congress,
    client: Any = None,
    format_: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    *,
    current_member: bool | None = None,
    fetch_all: bool = False,
) -> Any:
    """
    List members who served in this Congress.

    Delegates to ``Member.list_by_congress(congress=...)`` using ``number`` or
    ``congress`` from this instance.

    Args:
        client: API client override.
        format_: Response format (default: json).
        offset: Number of records to skip (ignored when ``fetch_all`` is True).
        limit: Maximum records per request, or total cap when not using ``fetch_all``.
        current_member: When True, restrict to members currently in office.
        fetch_all: When True, paginate with repeated API calls until all members
            for this Congress are retrieved (250 per page by default).

    Returns:
        ``Members`` collection for this Congress.

    Example:
        >>> congress = Congress(client).get(congress=118)
        >>> members = congress.get_members(fetch_all=True)
    """
    congress_number = _resolve_congress_number(self)
    from congressgov.services.member import Member as MemberService

    resolved_client = ApiService._resolve_client(self, client)
    return MemberService(client=resolved_client).list_by_congress(
        client=client,
        congress=congress_number,
        format_=format_,
        offset=offset,
        limit=limit,
        current_member=current_member,
        fetch_all=fetch_all,
    )
