"""Extract raw sponsorship events from Bill and Cosponsor models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable, Iterator, Protocol

from congressgov.models.base.types import CountRef, PolicyArea
from congressgov.models.entities.bill import Bill
from congressgov.models.entities.sponsor import Cosponsor, Cosponsors, Sponsor

from .member_labels import format_member_label_from_record
from .models import SponsorshipEvent


class CosponsorFetcher(Protocol):
    """Callable that fetches cosponsors for a bill."""

    def __call__(self, bill: Bill) -> list[Cosponsor] | Cosponsors | None:
        ...


def normalize_policy_area(value: Any) -> str | None:
    """Normalize policy area from Bill or Subject payloads."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, PolicyArea):
        return value.name
    if isinstance(value, dict):
        name = value.get("name")
        return str(name) if name is not None else None
    name = getattr(value, "name", None)
    return str(name) if name is not None else None


def normalize_chamber(value: Any) -> str | None:
    """Normalize origin chamber to ``house`` or ``senate``."""
    if value is None:
        return None
    text = str(getattr(value, "value", value)).strip().lower()
    if text in {"h", "house", "house of representatives"}:
        return "house"
    if text in {"s", "senate"}:
        return "senate"
    return text or None


_HOUSE_BILL_TYPES = frozenset({"hr", "hjres", "hres", "hconres"})
_SENATE_BILL_TYPES = frozenset({"s", "sjres", "sres", "sconres"})


def chamber_from_bill_type(bill_type: str) -> str | None:
    """Derive chamber from a bill type code (``hr``, ``s``, etc.).

    Cosponsors/sponsors of a bill are, by congressional rule, always members
    of the bill's own chamber. ``bill_type`` is always present and encodes
    chamber unambiguously, unlike the separate ``originChamber`` API field
    (nullable on ``Bill``), so it's a more reliable signal for a member's own
    chamber than ``originChamber`` alone.
    """
    normalized = bill_type.strip().lower()
    if normalized in _HOUSE_BILL_TYPES:
        return "house"
    if normalized in _SENATE_BILL_TYPES:
        return "senate"
    return None


def make_bill_id(congress: int, bill_type: str, bill_number: int) -> str:
    """Build a stable bill identifier."""
    return f"{congress}-{bill_type.lower()}-{bill_number}"


def make_event_id(bill_id: str, sponsor_bioguide_id: str, cosponsor_bioguide_id: str) -> str:
    """Build a stable sponsorship event identifier."""
    return f"{bill_id}|{sponsor_bioguide_id}|{cosponsor_bioguide_id}"


def _coerce_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def _member_label(
    *,
    bioguide_id: str,
    full_name: str | None,
    first_name: str | None,
    last_name: str | None,
    middle_name: str | None = None,
    party: str | None = None,
    state: str | None = None,
    district: int | str | None = None,
    origin_chamber: str | None = None,
) -> str:
    return format_member_label_from_record(
        bioguide_id=bioguide_id,
        full_name=full_name,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        party=party,
        state=state,
        district=district,
        origin_chamber=origin_chamber,
    )


def _bill_type_value(bill: Bill) -> str:
    bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
    if bill_type is None:
        raise ValueError("Bill is missing type")
    if hasattr(bill_type, "value"):
        return str(bill_type.value).lower()
    return str(bill_type).lower()


def _bill_number_value(bill: Bill) -> int:
    number = getattr(bill, "bill_number", getattr(bill, "number", None))
    if number is None:
        raise ValueError("Bill is missing number")
    return int(number)


def _bill_congress_value(bill: Bill) -> int:
    congress = getattr(bill, "congress", None)
    if congress is None:
        raise ValueError("Bill is missing congress")
    return int(congress)


def extract_sponsors(bill: Bill) -> list[Sponsor]:
    """Return primary sponsors from a bill, skipping entries without bioguide IDs."""
    sponsors = bill.sponsors
    if sponsors is None or isinstance(sponsors, CountRef):
        return []
    if not isinstance(sponsors, list):
        return []
    return [sponsor for sponsor in sponsors if sponsor.bioguideId]


def extract_cosponsors(cosponsors: list[Cosponsor] | Cosponsors | CountRef | None) -> list[Cosponsor]:
    """Return cosponsors from a list or Cosponsors wrapper."""
    if cosponsors is None or isinstance(cosponsors, CountRef):
        return []
    if isinstance(cosponsors, Cosponsors):
        items = cosponsors.cosponsors
    else:
        items = cosponsors
    if not items:
        return []
    return [cosponsor for cosponsor in items if cosponsor.bioguideId]


def resolve_cosponsors(bill: Bill, cosponsors: list[Cosponsor] | Cosponsors | CountRef | None = None) -> list[Cosponsor]:
    """Resolve cosponsors from explicit input or bill attribute."""
    if cosponsors is not None:
        return extract_cosponsors(cosponsors)
    return extract_cosponsors(getattr(bill, "cosponsors", None))


def sponsorship_events_from_bill(
    bill: Bill,
    cosponsors: list[Cosponsor] | Cosponsors | CountRef | None = None,
) -> list[SponsorshipEvent]:
    """Expand one bill into sponsor/cosponsor event rows."""
    congress = _bill_congress_value(bill)
    bill_type = _bill_type_value(bill)
    bill_number = _bill_number_value(bill)
    bill_id = make_bill_id(congress, bill_type, bill_number)
    policy_area = normalize_policy_area(getattr(bill, "policyArea", None))
    # originChamber is nullable on Bill; fall back to the (always-present,
    # unambiguous) bill_type prefix so sponsor/cosponsor chamber inference
    # downstream doesn't silently lose the signal on incomplete bill records.
    origin_chamber = normalize_chamber(getattr(bill, "originChamber", None)) or chamber_from_bill_type(
        bill_type
    )
    introduced_date = _coerce_date(getattr(bill, "introducedDate", None))
    latest_action = getattr(bill, "latestAction", None)
    latest_action_date = _coerce_date(getattr(latest_action, "actionDate", None)) if latest_action else None
    latest_action_text = getattr(latest_action, "text", None) if latest_action else None
    title = getattr(bill, "title", None)

    sponsors = extract_sponsors(bill)
    cosponsor_items = resolve_cosponsors(bill, cosponsors)
    events: list[SponsorshipEvent] = []

    for sponsor in sponsors:
        sponsor_id = sponsor.bioguideId
        if not sponsor_id:
            continue
        sponsor_name = _member_label(
            bioguide_id=sponsor_id,
            full_name=sponsor.fullName,
            first_name=sponsor.firstName,
            middle_name=sponsor.middleName,
            last_name=sponsor.lastName,
            party=sponsor.party,
            state=sponsor.state,
            district=sponsor.district,
            origin_chamber=origin_chamber,
        )
        for cosponsor in cosponsor_items:
            cosponsor_id = cosponsor.bioguideId
            if not cosponsor_id or cosponsor_id == sponsor_id:
                continue
            withdrawn_date = _coerce_date(cosponsor.sponsorshipWithdrawnDate)
            events.append(
                SponsorshipEvent(
                    event_id=make_event_id(bill_id, sponsor_id, cosponsor_id),
                    bill_id=bill_id,
                    congress=congress,
                    bill_type=bill_type,
                    bill_number=bill_number,
                    bill_title=title,
                    origin_chamber=origin_chamber,
                    policy_area=policy_area,
                    introduced_date=introduced_date,
                    latest_action_date=latest_action_date,
                    latest_action_text=latest_action_text,
                    sponsor_bioguide_id=sponsor_id,
                    sponsor_name=sponsor_name,
                    sponsor_party=sponsor.party,
                    sponsor_state=sponsor.state,
                    sponsor_district=sponsor.district,
                    cosponsor_bioguide_id=cosponsor_id,
                    cosponsor_name=_member_label(
                        bioguide_id=cosponsor_id,
                        full_name=cosponsor.fullName,
                        first_name=cosponsor.firstName,
                        middle_name=cosponsor.middleName,
                        last_name=cosponsor.lastName,
                        party=cosponsor.party,
                        state=cosponsor.state,
                        district=cosponsor.district,
                        origin_chamber=origin_chamber,
                    ),
                    cosponsor_party=cosponsor.party,
                    cosponsor_state=cosponsor.state,
                    cosponsor_district=cosponsor.district,
                    sponsorship_date=_coerce_date(cosponsor.sponsorshipDate),
                    is_original_cosponsor=cosponsor.isOriginalCosponsor,
                    sponsorship_withdrawn_date=withdrawn_date,
                    is_active=withdrawn_date is None,
                )
            )
    return events


def sponsorship_events_from_bills(
    bills: Iterable[Bill],
    *,
    fetch_cosponsors: CosponsorFetcher | None = None,
) -> list[SponsorshipEvent]:
    """Expand many bills into sponsorship events."""
    events: list[SponsorshipEvent] = []
    for bill in bills:
        cosponsors = fetch_cosponsors(bill) if fetch_cosponsors else None
        events.extend(sponsorship_events_from_bill(bill, cosponsors))
    return events


def iter_sponsorship_events_from_bills(
    bills: Iterable[Bill],
    *,
    fetch_cosponsors: CosponsorFetcher | None = None,
) -> Iterator[SponsorshipEvent]:
    """Yield sponsorship events without building a large intermediate list."""
    for bill in bills:
        cosponsors = fetch_cosponsors(bill) if fetch_cosponsors else None
        yield from sponsorship_events_from_bill(bill, cosponsors)
