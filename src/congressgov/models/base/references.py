"""
Minimal reference models (`BillRef`, `CommitteeRef`, `MemberRef`, etc.) that carry
just enough identification to link to an entity without importing its full model.
Bill, Committee, Action, and Member all reference each other, so importing the
full models directly would create circular imports; these break that cycle.

    from models.base.references import BillRef

    full_bill = bill_service.get(
        congress=bill_ref.congress,
        bill_type=bill_ref.type,
        bill_number=bill_ref.number,
    )
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import Field

from .model import Model
from .enums import LegislationType, Chamber, CommitteeType


class BillRef(Model):
    """Enough fields to identify a `Bill` and fetch it later, without the full model's
    dependency chain. Used by Committee, Action, and Amendment models.
    """
    congress: int | None = None
    type: LegislationType | str | None = None
    number: int | None = None
    title: str | None = None
    url: str | None = None
    originChamber: Chamber | str | None = None
    originChamberCode: str | None = None
    updateDate: datetime | None = None
    latestActionDate: date | None = None
    latestActionText: str | None = None


class CommitteeRef(Model):
    """Enough fields to identify a `Committee`, for use in Bill, Action, Meeting, and Report models."""
    chamber: Chamber | str | None = None
    code: str | None = Field(None, alias="systemCode")  # API uses "systemCode"
    name: str | None = None
    type: CommitteeType | str | None = None
    url: str | None = None
    updateDate: datetime | None = None


class MemberRef(Model):
    """Enough fields to identify a `Member`, for use in Sponsor, Action, Vote, and Committee models."""
    bioguideId: str | None = None
    name: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    party: str | None = None
    state: str | None = None
    district: int | None = None
    url: str | None = None
    updateDate: datetime | None = None


class AmendmentRef(Model):
    """Enough fields to identify an `Amendment`, for use in Bill and Action models,
    and for self-references between amendments.
    """
    congress: int | None = None
    type: str | None = None  # e.g., "hamdt", "samdt", "suamdt"
    number: int | None = None
    description: str | None = None
    purpose: str | None = None
    chamber: Chamber | str | None = None
    url: str | None = None
    latestActionDate: date | None = None
    latestActionText: str | None = None
    updateDate: datetime | None = None


class TreatyRef(Model):
    """Enough fields to identify a `Treaty`, for use in Action and Committee models."""
    congress: int | None = None
    number: int | None = None
    suffix: str | None = None  # e.g., "A", "B", etc.
    title: str | None = None
    topic: str | None = None
    url: str | None = None
    transmittedDate: date | None = None
    updateDate: datetime | None = None


class NominationRef(Model):
    """Enough fields to identify a `Nomination`, for use in Action and Committee models."""
    congress: int | None = None
    number: int | None = None
    partNumber: int | None = None
    citation: str | None = None  # e.g., "PN100"
    description: str | None = None
    receivedDate: date | None = None
    url: str | None = None
    updateDate: datetime | None = None


def bill_to_ref(bill: Any) -> BillRef:
    """Convert a full `Bill` (model instance or dict) to a `BillRef`."""
    if isinstance(bill, dict):
        return BillRef(**{
            k: v for k, v in bill.items()
            if k in BillRef.model_fields
        })
    
    return BillRef(
        congress=getattr(bill, 'congress', None),
        type=getattr(bill, 'type', None),
        number=getattr(bill, 'number', None),
        title=getattr(bill, 'title', None),
        url=getattr(bill, 'url', None),
        originChamber=getattr(bill, 'originChamber', None),
        originChamberCode=getattr(bill, 'originChamberCode', None),
        updateDate=getattr(bill, 'updateDate', None),
        latestActionDate=getattr(bill, 'latestActionDate', None) if hasattr(bill, 'latestActionDate') else 
                         getattr(bill, 'latestAction', {}).get('actionDate') if hasattr(bill, 'latestAction') else None,
        latestActionText=getattr(bill, 'latestActionText', None) if hasattr(bill, 'latestActionText') else
                         getattr(bill, 'latestAction', {}).get('text') if hasattr(bill, 'latestAction') else None,
    )


def committee_to_ref(committee: Any) -> CommitteeRef:
    """Convert a full `Committee` (model instance or dict) to a `CommitteeRef`."""
    if isinstance(committee, dict):
        return CommitteeRef(**{
            k: v for k, v in committee.items()
            if k in CommitteeRef.model_fields
        })
    
    return CommitteeRef(
        chamber=getattr(committee, 'chamber', None),
        code=getattr(committee, 'systemCode', None) or getattr(committee, 'code', None),
        name=getattr(committee, 'name', None),
        type=getattr(committee, 'type', None),
        url=getattr(committee, 'url', None),
        updateDate=getattr(committee, 'updateDate', None),
    )


def member_to_ref(member: Any) -> MemberRef:
    """Convert a full `Member` (model instance or dict) to a `MemberRef`."""
    if isinstance(member, dict):
        return MemberRef(**{
            k: v for k, v in member.items()
            if k in MemberRef.model_fields
        })
    
    return MemberRef(
        bioguideId=getattr(member, 'bioguideId', None),
        name=getattr(member, 'name', None) or 
             f"{getattr(member, 'firstName', '')} {getattr(member, 'lastName', '')}".strip(),
        firstName=getattr(member, 'firstName', None),
        middleName=getattr(member, 'middleName', None),
        lastName=getattr(member, 'lastName', None),
        party=getattr(member, 'party', None) or getattr(member, 'partyName', None),
        state=getattr(member, 'state', None),
        district=getattr(member, 'district', None),
        url=getattr(member, 'url', None),
        updateDate=getattr(member, 'updateDate', None),
    )


def amendment_to_ref(amendment: Any) -> AmendmentRef:
    """Convert a full `Amendment` (model instance or dict) to an `AmendmentRef`."""
    if isinstance(amendment, dict):
        return AmendmentRef(**{
            k: v for k, v in amendment.items()
            if k in AmendmentRef.model_fields
        })
    
    return AmendmentRef(
        congress=getattr(amendment, 'congress', None),
        type=getattr(amendment, 'type', None),
        number=getattr(amendment, 'number', None),
        description=getattr(amendment, 'description', None),
        purpose=getattr(amendment, 'purpose', None),
        chamber=getattr(amendment, 'chamber', None),
        url=getattr(amendment, 'url', None),
        latestActionDate=getattr(amendment, 'latestActionDate', None) if hasattr(amendment, 'latestActionDate') else
                         getattr(amendment, 'latestAction', {}).get('actionDate') if hasattr(amendment, 'latestAction') else None,
        latestActionText=getattr(amendment, 'latestActionText', None) if hasattr(amendment, 'latestActionText') else
                         getattr(amendment, 'latestAction', {}).get('text') if hasattr(amendment, 'latestAction') else None,
        updateDate=getattr(amendment, 'updateDate', None),
    )


def treaty_to_ref(treaty: Any) -> TreatyRef:
    """Convert a full `Treaty` (model instance or dict) to a `TreatyRef`."""
    if isinstance(treaty, dict):
        return TreatyRef(**{
            k: v for k, v in treaty.items()
            if k in TreatyRef.model_fields
        })
    
    return TreatyRef(
        congress=getattr(treaty, 'congress', None),
        number=getattr(treaty, 'number', None),
        suffix=getattr(treaty, 'suffix', None),
        title=getattr(treaty, 'title', None),
        topic=getattr(treaty, 'topic', None),
        url=getattr(treaty, 'url', None),
        transmittedDate=getattr(treaty, 'transmittedDate', None),
        updateDate=getattr(treaty, 'updateDate', None),
    )


def nomination_to_ref(nomination: Any) -> NominationRef:
    """Convert a full `Nomination` (model instance or dict) to a `NominationRef`."""
    if isinstance(nomination, dict):
        return NominationRef(**{
            k: v for k, v in nomination.items()
            if k in NominationRef.model_fields
        })
    
    return NominationRef(
        congress=getattr(nomination, 'congress', None),
        number=getattr(nomination, 'number', None),
        partNumber=getattr(nomination, 'partNumber', None),
        citation=getattr(nomination, 'citation', None),
        description=getattr(nomination, 'description', None),
        receivedDate=getattr(nomination, 'receivedDate', None),
        url=getattr(nomination, 'url', None),
        updateDate=getattr(nomination, 'updateDate', None),
    )



