"""Async extension methods to fetch entities from API URLs."""

from __future__ import annotations

import warnings
from typing import Any

from congressgov.models.base.references import (
    AmendmentRef,
    BillRef,
    CommitteeRef,
    MemberRef,
    NominationRef,
    TreatyRef,
)
from congressgov.models.base.types import CountRef, URL
from congressgov.models.entities.member import (
    CosponsoredLegislationItem,
    SponsoredLegislationItem,
)
from congressgov.models.entities.sponsor import Cosponsor, Sponsor
from congressgov.services.core.async_method_registry import register_async_method
from congressgov.services.core.expansion_helpers import (
    PARENT_ENTITY_ATTR,
    PARENT_FIELD_ATTR,
    bind_fetch_result_to_parent,
    is_amendment_legislation_item,
)
from congressgov.services.core.request_store import fetch_options
from congressgov.services.core.url_resolver import (
    extract_api_url,
    fetch_from_url_async,
)

_DEPRECATED_FETCH_LEGISLATION_ASYNC = (
    "fetch_legislation_async() is deprecated; use fetch_async() instead. "
    "Will be removed in a future release."
)
async def _fetch_url_field_async(
    self: Any,
    *,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    from congressgov.models.base.types import CountRef

    # Mirrors the sync `_fetch_url_field` shortcut/binding: reuse an already
    # hydrated parent attribute instead of refetching, and bind fresh fetch
    # results back onto the owning parent (previously only done in sync).
    force_fetch = bool(kwargs.pop("force_fetch", False))
    owner = getattr(self, PARENT_ENTITY_ATTR, None)
    effective_parent = parent or owner or self

    if (
        not force_fetch
        and owner is not None
        and isinstance(self, CountRef)
    ):
        field = getattr(self, PARENT_FIELD_ATTR, None)
        if field is not None:
            current = getattr(owner, field, None)
            if current is not None and not isinstance(current, CountRef):
                if getattr(current, "client", None) is None and client is not None:
                    current.client = client
                return current

    url = extract_api_url(self)
    if not url:
        raise ValueError(f"{type(self).__name__} has no API url to fetch")
    with fetch_options(force_fetch=force_fetch):
        result = await fetch_from_url_async(url, client=client, parent=effective_parent, **kwargs)
    if owner is not None:
        bind_fetch_result_to_parent(owner, result)
    return result


@register_async_method(URL)
async def fetch_async(
    self: URL,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    return await _fetch_url_field_async(self, client=client, parent=parent, **kwargs)


@register_async_method(CountRef)
async def fetch_async(
    self: CountRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    return await _fetch_url_field_async(self, client=client, parent=parent, **kwargs)


async def _fetch_bill_ref_async(self: BillRef, client: Any = None, parent: Any = None, **kwargs: Any):
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.bill import AsyncBill

    congress = getattr(self, "congress", None)
    bill_type = getattr(self, "type", None)
    number = getattr(self, "number", None)
    if congress is None or bill_type is None or number is None:
        raise ValueError("BillRef requires url or congress, type, and number")
    service = AsyncBill(client=client or getattr(self, "client", None))
    return await service.get(
        client=client,
        congress=congress,
        bill_type=str(bill_type),
        bill_number=int(number),
        **kwargs,
    )


@register_async_method(BillRef)
async def fetch_async(
    self: BillRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    return await _fetch_bill_ref_async(self, client=client, parent=parent, **kwargs)


@register_async_method(MemberRef)
async def fetch_async(
    self: MemberRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.member import AsyncMember

    bioguide_id = getattr(self, "bioguideId", None)
    if not bioguide_id:
        raise ValueError("MemberRef requires url or bioguideId")
    service = AsyncMember(client=client or getattr(self, "client", None))
    return await service.get(client=client, bioguide_id=bioguide_id, **kwargs)


@register_async_method(AmendmentRef)
async def fetch_async(
    self: AmendmentRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.amendment import AsyncAmendment

    congress = getattr(self, "congress", None)
    amendment_type = getattr(self, "type", None) or getattr(self, "amendment_type", None)
    number = getattr(self, "number", None) or getattr(self, "amendment_number", None)
    if congress is None or amendment_type is None or number is None:
        raise ValueError("AmendmentRef requires url or congress, type, and number")
    service = AsyncAmendment(client=client or getattr(self, "client", None))
    return await service.get(
        client=client,
        congress=congress,
        amendment_type=str(amendment_type),
        amendment_number=str(number),
        **kwargs,
    )


@register_async_method(CommitteeRef)
async def fetch_async(
    self: CommitteeRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.committee import AsyncCommittee

    chamber = getattr(self, "chamber", None)
    code = getattr(self, "code", None) or getattr(self, "systemCode", None)
    if chamber is None or code is None:
        raise ValueError("CommitteeRef requires url or chamber and code")
    service = AsyncCommittee(client=client or getattr(self, "client", None))
    return await service.get(
        client=client, chamber=str(chamber), committee_code=str(code), **kwargs
    )


@register_async_method(TreatyRef)
async def fetch_async(
    self: TreatyRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.treaty import AsyncTreaty

    congress = getattr(self, "congress", None)
    number = getattr(self, "number", None) or getattr(self, "treaty_number", None)
    if congress is None or number is None:
        raise ValueError("TreatyRef requires url or congress and number")
    service = AsyncTreaty(client=client or getattr(self, "client", None))
    return await service.get(client=client, congress=congress, treaty_number=str(number), **kwargs)


@register_async_method(NominationRef)
async def fetch_async(
    self: NominationRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.nomination import AsyncNomination

    congress = getattr(self, "congress", None)
    number = getattr(self, "number", None) or getattr(self, "nomination_number", None)
    if congress is None or number is None:
        raise ValueError("NominationRef requires url or congress and number")
    service = AsyncNomination(client=client or getattr(self, "client", None))
    return await service.get(
        client=client,
        congress=congress,
        nomination_number=str(number),
        **kwargs,
    )


@register_async_method(Sponsor)
async def fetch_member_async(
    self: Sponsor,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.member import AsyncMember

    bioguide_id = getattr(self, "bioguideId", None) or getattr(self, "bioguide_id", None)
    if not bioguide_id:
        raise ValueError("Sponsor requires url or bioguideId")
    service = AsyncMember(client=client or getattr(self, "client", None))
    return await service.get(client=client, bioguide_id=bioguide_id, **kwargs)


@register_async_method(Cosponsor)
async def fetch_member_async(
    self: Cosponsor,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.async_api.member import AsyncMember

    bioguide_id = getattr(self, "bioguideId", None) or getattr(self, "bioguide_id", None)
    if not bioguide_id:
        raise ValueError("Cosponsor requires url or bioguideId")
    service = AsyncMember(client=client or getattr(self, "client", None))
    return await service.get(client=client, bioguide_id=bioguide_id, **kwargs)


async def _fetch_legislation_from_item_async(
    self: Any,
    *,
    client: Any = None,
    parent: Any = None,
    label: str = "Legislation item",
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return await fetch_from_url_async(
            url, client=client, parent=parent or self, **kwargs
        )

    congress = getattr(self, "congress", None)
    item_type = getattr(self, "type", None)
    if congress is None or item_type is None:
        raise ValueError(f"{label} requires url or congress and type")

    resolved_client = client or getattr(self, "client", None)
    if is_amendment_legislation_item(self):
        from congressgov.services.async_api.amendment import AsyncAmendment

        number = getattr(self, "amendmentNumber", None) or getattr(self, "number", None)
        if number is None:
            raise ValueError(f"{label} requires url or congress, type, and number")
        amendment_service = AsyncAmendment(client=resolved_client)
        return await amendment_service.get(
            client=client,
            congress=congress,
            amendment_type=str(item_type),
            amendment_number=str(number),
            **kwargs,
        )

    from congressgov.services.async_api.bill import AsyncBill

    number = getattr(self, "number", None)
    if number is None:
        raise ValueError(f"{label} requires url or congress, type, and number")
    bill_service = AsyncBill(client=resolved_client)
    return await bill_service.get(
        client=client,
        congress=congress,
        bill_type=str(item_type),
        bill_number=int(number),
        **kwargs,
    )


@register_async_method(SponsoredLegislationItem)
async def fetch_async(
    self: SponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Bill`` or ``Amendment`` from item ``url`` or id fields."""
    return await _fetch_legislation_from_item_async(
        self,
        client=client,
        parent=parent,
        label="SponsoredLegislationItem",
        **kwargs,
    )


@register_async_method(SponsoredLegislationItem)
async def fetch_legislation_async(
    self: SponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Deprecated alias for :meth:`fetch_async`."""
    warnings.warn(_DEPRECATED_FETCH_LEGISLATION_ASYNC, DeprecationWarning, stacklevel=2)
    return await _fetch_legislation_from_item_async(
        self,
        client=client,
        parent=parent,
        label="SponsoredLegislationItem",
        **kwargs,
    )


@register_async_method(CosponsoredLegislationItem)
async def fetch_async(
    self: CosponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Bill`` or ``Amendment`` from item ``url`` or id fields."""
    return await _fetch_legislation_from_item_async(
        self,
        client=client,
        parent=parent,
        label="CosponsoredLegislationItem",
        **kwargs,
    )


@register_async_method(CosponsoredLegislationItem)
async def fetch_legislation_async(
    self: CosponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Deprecated alias for :meth:`fetch_async`."""
    warnings.warn(_DEPRECATED_FETCH_LEGISLATION_ASYNC, DeprecationWarning, stacklevel=2)
    return await _fetch_legislation_from_item_async(
        self,
        client=client,
        parent=parent,
        label="CosponsoredLegislationItem",
        **kwargs,
    )
