"""Extension methods to fetch entities from API URLs on models and refs."""

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
from congressgov.services.core.expansion_helpers import (
    PARENT_ENTITY_ATTR,
    PARENT_FIELD_ATTR,
    bind_fetch_result_to_parent,
    is_amendment_legislation_item,
)
from congressgov.services.core.url_resolver import (
    extract_api_url,
    fetch_from_url,
)
from congressgov.services.extensions._registry import register_method

_DEPRECATED_FETCH_LEGISLATION = (
    "fetch_legislation() is deprecated; use fetch() instead. "
    "Will be removed in a future release."
)


def _fetch_url_field(
    self: Any,
    *,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    from congressgov.models.base.types import CountRef
    from congressgov.services.core.request_store import fetch_options

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
        result = fetch_from_url(url, client=client, parent=effective_parent, **kwargs)
    if owner is not None:
        bind_fetch_result_to_parent(owner, result)
    return result


@register_method(URL)
def fetch(
    self: URL,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch the API resource at ``self.url``."""
    return _fetch_url_field(self, client=client, parent=parent, **kwargs)


@register_method(CountRef)
def fetch(
    self: CountRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch the API sub-resource at ``self.url`` (e.g. bill actions list)."""
    return _fetch_url_field(self, client=client, parent=parent, **kwargs)


@register_method(BillRef)
def fetch(
    self: BillRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Bill`` from ``url`` or from ``congress``/``type``/``number``."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.bill import Bill as BillService

    congress = getattr(self, "congress", None)
    bill_type = getattr(self, "type", None)
    number = getattr(self, "number", None)
    if congress is None or bill_type is None or number is None:
        raise ValueError("BillRef requires url or congress, type, and number")
    service = BillService(client=client or getattr(self, "client", None))
    return service.get(
        client=client,
        congress=congress,
        bill_type=str(bill_type),
        bill_number=int(number),
        **kwargs,
    )


@register_method(MemberRef)
def fetch(
    self: MemberRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Member`` from ``url`` or ``bioguideId``."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.member import Member as MemberService

    bioguide_id = getattr(self, "bioguideId", None)
    if not bioguide_id:
        raise ValueError("MemberRef requires url or bioguideId")
    service = MemberService(client=client or getattr(self, "client", None))
    return service.get(client=client, bioguide_id=bioguide_id, **kwargs)


@register_method(AmendmentRef)
def fetch(
    self: AmendmentRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Amendment`` from ``url`` or id fields."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.amendment import Amendment as AmendmentService

    congress = getattr(self, "congress", None)
    amendment_type = getattr(self, "type", None) or getattr(self, "amendment_type", None)
    number = getattr(self, "number", None) or getattr(self, "amendment_number", None)
    if congress is None or amendment_type is None or number is None:
        raise ValueError("AmendmentRef requires url or congress, type, and number")
    service = AmendmentService(client=client or getattr(self, "client", None))
    return service.get(
        client=client,
        congress=congress,
        amendment_type=str(amendment_type),
        amendment_number=str(number),
        **kwargs,
    )


@register_method(CommitteeRef)
def fetch(
    self: CommitteeRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Committee`` from ``url`` or ``chamber``/``code``."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.committee import Committee as CommitteeService

    chamber = getattr(self, "chamber", None)
    code = getattr(self, "code", None) or getattr(self, "systemCode", None)
    if chamber is None or code is None:
        raise ValueError("CommitteeRef requires url or chamber and code")
    service = CommitteeService(client=client or getattr(self, "client", None))
    return service.get(client=client, chamber=str(chamber), committee_code=str(code), **kwargs)


@register_method(TreatyRef)
def fetch(
    self: TreatyRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Treaty`` from ``url`` or congress/number fields."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.treaty import Treaty as TreatyService

    congress = getattr(self, "congress", None)
    number = getattr(self, "number", None) or getattr(self, "treaty_number", None)
    if congress is None or number is None:
        raise ValueError("TreatyRef requires url or congress and number")
    service = TreatyService(client=client or getattr(self, "client", None))
    return service.get(client=client, congress=congress, treaty_number=str(number), **kwargs)


@register_method(NominationRef)
def fetch(
    self: NominationRef,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Nomination`` from ``url`` or congress/number fields."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.nomination import Nomination as NominationService

    congress = getattr(self, "congress", None)
    number = getattr(self, "number", None) or getattr(self, "nomination_number", None)
    if congress is None or number is None:
        raise ValueError("NominationRef requires url or congress and number")
    service = NominationService(client=client or getattr(self, "client", None))
    return service.get(
        client=client,
        congress=congress,
        nomination_number=str(number),
        **kwargs,
    )


def _fetch_member_from_sponsor_like(
    self: Any,
    *,
    client: Any = None,
    parent: Any = None,
    label: str = "Sponsor",
    **kwargs: Any,
) -> Any:
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)
    from congressgov.services.member import Member as MemberService

    bioguide_id = getattr(self, "bioguideId", None) or getattr(self, "bioguide_id", None)
    if not bioguide_id:
        raise ValueError(f"{label} requires url or bioguideId")
    service = MemberService(client=client or getattr(self, "client", None))
    return service.get(client=client, bioguide_id=bioguide_id, **kwargs)


@register_method(Sponsor)
def fetch_member(
    self: Sponsor,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch ``Member`` from sponsor ``url`` or ``bioguideId``."""
    return _fetch_member_from_sponsor_like(
        self, client=client, parent=parent, label="Sponsor", **kwargs
    )


@register_method(Cosponsor)
def fetch_member(
    self: Cosponsor,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch ``Member`` from cosponsor ``url`` or ``bioguideId``."""
    return _fetch_member_from_sponsor_like(
        self, client=client, parent=parent, label="Cosponsor", **kwargs
    )


def _fetch_legislation_from_item(
    self: Any,
    *,
    client: Any = None,
    parent: Any = None,
    label: str = "Legislation item",
    **kwargs: Any,
) -> Any:
    """Fetch ``Bill`` or ``Amendment`` from ``url`` or id fields on a sponsorship item."""
    url = extract_api_url(self)
    if url:
        return fetch_from_url(url, client=client, parent=parent or self, **kwargs)

    congress = getattr(self, "congress", None)
    item_type = getattr(self, "type", None)
    if congress is None or item_type is None:
        raise ValueError(f"{label} requires url or congress and type")

    resolved_client = client or getattr(self, "client", None)
    if is_amendment_legislation_item(self):
        from congressgov.services.amendment import Amendment as AmendmentService

        number = getattr(self, "amendmentNumber", None) or getattr(self, "number", None)
        if number is None:
            raise ValueError(f"{label} requires url or congress, type, and number")
        amendment_service = AmendmentService(client=resolved_client)
        return amendment_service.get(
            client=client,
            congress=congress,
            amendment_type=str(item_type),
            amendment_number=str(number),
            **kwargs,
        )

    from congressgov.services.bill import Bill as BillService

    number = getattr(self, "number", None)
    if number is None:
        raise ValueError(f"{label} requires url or congress, type, and number")
    bill_service = BillService(client=resolved_client)
    return bill_service.get(
        client=client,
        congress=congress,
        bill_type=str(item_type),
        bill_number=int(number),
        **kwargs,
    )


@register_method(SponsoredLegislationItem)
def fetch(
    self: SponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Bill`` or ``Amendment`` from item ``url`` or id fields."""
    return _fetch_legislation_from_item(
        self,
        client=client,
        parent=parent,
        label="SponsoredLegislationItem",
        **kwargs,
    )


@register_method(SponsoredLegislationItem)
def fetch_legislation(
    self: SponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Deprecated alias for :meth:`fetch`."""
    warnings.warn(_DEPRECATED_FETCH_LEGISLATION, DeprecationWarning, stacklevel=2)
    return _fetch_legislation_from_item(
        self,
        client=client,
        parent=parent,
        label="SponsoredLegislationItem",
        **kwargs,
    )


@register_method(CosponsoredLegislationItem)
def fetch(
    self: CosponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Fetch full ``Bill`` or ``Amendment`` from item ``url`` or id fields."""
    return _fetch_legislation_from_item(
        self,
        client=client,
        parent=parent,
        label="CosponsoredLegislationItem",
        **kwargs,
    )


@register_method(CosponsoredLegislationItem)
def fetch_legislation(
    self: CosponsoredLegislationItem,
    client: Any = None,
    parent: Any = None,
    **kwargs: Any,
) -> Any:
    """Deprecated alias for :meth:`fetch`."""
    warnings.warn(_DEPRECATED_FETCH_LEGISLATION, DeprecationWarning, stacklevel=2)
    return _fetch_legislation_from_item(
        self,
        client=client,
        parent=parent,
        label="CosponsoredLegislationItem",
        **kwargs,
    )
