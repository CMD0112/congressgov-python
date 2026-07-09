"""Ingest bills from Congress.gov and build sponsorship event datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, Iterator, Protocol

from congressgov.models.entities.bill import Bill

from .member_labels import is_canonical_member_label
from .builder import build_graph_slice
from .models import GraphExploreConfig, GraphSlice, SponsorshipEvent
from .sources import extract_cosponsors, extract_sponsors, sponsorship_events_from_bill

if TYPE_CHECKING:
    from .member_labels import MemberLabelResolver


class BillSearchService(Protocol):
    """Minimal sync bill search protocol."""

    def search(self, **kwargs: Any) -> Any:
        ...


class AsyncBillSearchService(Protocol):
    """Minimal async bill search protocol."""

    async def search_stream(self, **kwargs: Any) -> AsyncIterator[Any]:
        ...


@dataclass
class GraphIngestionConfig:
    """Configuration for graph ingestion jobs."""

    congress: int
    bill_type: str | None = None
    batch_size: int = 100
    cosponsor_limit: int = 250
    search_sort: str | None = None


def _iter_bills(search_result: Any) -> Iterator[Bill]:
    if search_result is None:
        return iter(())
    if isinstance(search_result, Bill):
        return iter((search_result,))
    bills = getattr(search_result, "bills", None)
    if bills:
        return iter(bills)
    if hasattr(search_result, "__iter__") and not isinstance(search_result, (str, bytes, dict)):
        return iter(search_result)
    return iter(())


def _bill_identity(bill: Bill) -> tuple[int, str, int]:
    congress = int(getattr(bill, "congress"))
    bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
    if bill_type is None:
        raise ValueError("Bill is missing type")
    if hasattr(bill_type, "value"):
        bill_type = str(bill_type.value)
    bill_number = getattr(bill, "bill_number", getattr(bill, "number", None))
    if bill_number is None:
        raise ValueError("Bill is missing number")
    return congress, str(bill_type).lower(), int(bill_number)


def _needs_bill_hydration(bill: Bill) -> bool:
    """True when search/list payloads omit sponsors or member display metadata."""
    sponsors = extract_sponsors(bill)
    if not sponsors:
        return True
    for sponsor in sponsors:
        full_name = getattr(sponsor, "fullName", None)
        if full_name and is_canonical_member_label(full_name):
            continue
        if not getattr(sponsor, "lastName", None) and not full_name:
            return True
        if not getattr(sponsor, "state", None):
            return True
    return False


def _hydrate_bill(
    bill_service: BillSearchService,
    bill: Bill,
    *,
    service_client: Any,
) -> Bill:
    """Fetch full bill details when list/search payloads omit sponsors or labels."""
    if service_client is not None and getattr(bill, "client", None) is None:
        bill.client = service_client
    if not _needs_bill_hydration(bill):
        return bill
    if not hasattr(bill_service, "get"):
        return bill
    congress, bill_type, bill_number = _bill_identity(bill)
    return bill_service.get(
        congress=congress,
        bill_type=bill_type,
        bill_number=bill_number,
        client=service_client,
    )


def ingest_bill_events(
    bill_service: BillSearchService,
    config: GraphIngestionConfig,
    *,
    limit: int | None = None,
    fetch_cosponsors: bool = True,
    graph_store: Any | None = None,
) -> list[SponsorshipEvent]:
    """Fetch bills and expand them into sponsorship events."""
    from .sources import make_bill_id

    search_kwargs: dict[str, Any] = {
        "congress": config.congress,
        "limit": config.batch_size,
    }
    if config.search_sort:
        search_kwargs["sort"] = config.search_sort
    if config.bill_type:
        search_kwargs["bill_type"] = config.bill_type
    # `limit` caps the number of *events* returned (see docs/GRAPH_CONSTRUCTION.md),
    # not the bill search batch size -- clamping the search itself by `limit`
    # under-fetches bills whenever a bill yields more than one event (e.g. any
    # bill with 2+ cosponsors), since fewer bills than `limit` could still
    # produce >= `limit` events.
    search_result = bill_service.search(**search_kwargs)
    service_client = getattr(bill_service, "client", None)
    events: list[SponsorshipEvent] = []
    for bill in _iter_bills(search_result):
        if graph_store is not None:
            congress, bill_type, bill_number = _bill_identity(bill)
            bill_id = make_bill_id(congress, bill_type, bill_number)
            if bill_id in graph_store.bill_ids:
                continue

        bill = _hydrate_bill(bill_service, bill, service_client=service_client)
        cosponsors = None
        if fetch_cosponsors and hasattr(bill, "get_cosponsors"):
            cosponsors = bill.get_cosponsors(
                limit=config.cosponsor_limit,
                client=service_client,
            )
        events.extend(sponsorship_events_from_bill(bill, cosponsors))
        if limit is not None and len(events) >= limit:
            break
    return events


async def _hydrate_bill_async(
    bill_service: AsyncBillSearchService,
    bill: Bill,
    *,
    service_client: Any,
) -> Bill:
    """Async counterpart to :func:`_hydrate_bill` with matching hydration logic."""
    if service_client is not None and getattr(bill, "client", None) is None:
        bill.client = service_client
    if not _needs_bill_hydration(bill):
        return bill
    if not hasattr(bill_service, "get"):
        return bill
    congress, bill_type, bill_number = _bill_identity(bill)
    return await bill_service.get(
        congress=congress,
        bill_type=bill_type,
        bill_number=bill_number,
        client=service_client,
    )


async def ingest_bill_events_async(
    bill_service: AsyncBillSearchService,
    config: GraphIngestionConfig,
    *,
    max_bills: int | None = None,
    fetch_cosponsors: bool = True,
    graph_store: Any | None = None,
) -> list[SponsorshipEvent]:
    """Fetch bills asynchronously and expand them into sponsorship events."""
    from .sources import make_bill_id

    search_kwargs: dict[str, Any] = {
        "congress": config.congress,
        "batch_size": config.batch_size,
    }
    if config.search_sort:
        search_kwargs["sort"] = config.search_sort
    if config.bill_type:
        search_kwargs["bill_type"] = config.bill_type

    events: list[SponsorshipEvent] = []
    processed = 0
    service_client = getattr(bill_service, "client", None)
    async for batch in bill_service.search_stream(**search_kwargs):
        for bill in _iter_bills(batch):
            if graph_store is not None:
                congress, bill_type, bill_number = _bill_identity(bill)
                bill_id = make_bill_id(congress, bill_type, bill_number)
                if bill_id in graph_store.bill_ids:
                    continue

            bill = await _hydrate_bill_async(bill_service, bill, service_client=service_client)
            cosponsors = None
            if fetch_cosponsors:
                if hasattr(bill, "get_cosponsors_async"):
                    wrapper = await bill.get_cosponsors_async(
                        limit=config.cosponsor_limit,
                        client=service_client,
                    )
                    cosponsors = extract_cosponsors(wrapper)
                elif hasattr(bill, "get_cosponsors"):
                    cosponsors = bill.get_cosponsors(
                        limit=config.cosponsor_limit,
                        client=service_client,
                    )
            events.extend(sponsorship_events_from_bill(bill, cosponsors))
            processed += 1
            if max_bills is not None and processed >= max_bills:
                return events
    return events


def build_graph_from_bills(
    bills: Iterable[Bill],
    config: GraphExploreConfig,
    *,
    fetch_cosponsors: bool = False,
    cosponsor_limit: int = 250,
    member_resolver: MemberLabelResolver | None = None,
) -> GraphSlice:
    """Build a graph slice directly from in-memory bill objects."""
    events: list[SponsorshipEvent] = []
    for bill in bills:
        cosponsors = None
        if fetch_cosponsors and hasattr(bill, "get_cosponsors"):
            cosponsors = bill.get_cosponsors(limit=cosponsor_limit)
        events.extend(sponsorship_events_from_bill(bill, cosponsors))
    return build_graph_slice(events, config, member_resolver=member_resolver)
