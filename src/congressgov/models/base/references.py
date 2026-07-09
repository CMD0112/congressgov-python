"""
Lightweight reference models for breaking circular dependencies.

This module provides minimal reference models that contain only essential
identification information, avoiding the need for full model imports and
breaking circular dependency chains.

Architecture Benefits:
- Eliminates circular imports between Bill ↔ Committee ↔ Action ↔ Member
- Maintains type safety without full model coupling
- Enables IntelliSense support without TYPE_CHECKING guards
- Provides clear separation between references and full entities

Usage Pattern:
    # Instead of importing full models (causes circular imports):
    from models.entities.bill import Bill  # ❌ Circular dependency
    
    # Use lightweight references:
    from models.base.references import BillRef  # ✅ No circular dependency
    
    # Expand to full model when needed:
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


# ============================================================================
# CORE ENTITY REFERENCES
# ============================================================================


class BillRef(Model):
    """
    Lightweight reference to a Bill entity.
    
    Contains only essential identification information for referencing
    a bill without requiring the full Bill model (which has many dependencies).
    
    Use Cases:
    - In Committee models to reference bills without importing Bill
    - In Action models to reference related bills
    - In Amendment models to reference amended bills
    - In any model that needs to reference but not fully load a bill
    
    Example:
        # Create reference from full bill
        bill_ref = BillRef(
            congress=118,
            type=LegislationType.HR,
            number=1,
            title="Example Bill Title",
            url="https://api.congress.gov/v3/bill/118/hr/1"
        )
        
        # Use reference to fetch full bill later
        full_bill = bill_service.get(
            congress=bill_ref.congress,
            bill_type=bill_ref.type,
            bill_number=bill_ref.number
        )
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
    """
    Lightweight reference to a Committee entity.
    
    Contains only essential identification information for referencing
    a committee without requiring the full Committee model.
    
    Use Cases:
    - In Bill models to reference committees
    - In Action models to reference committees that took action
    - In Meeting models to reference parent committee
    - In Report models to reference issuing committee
    
    Example:
        committee_ref = CommitteeRef(
            chamber=Chamber.HOUSE,
            code="hspw00",
            name="Committee on Transportation and Infrastructure",
            url="https://api.congress.gov/v3/committee/house/hspw00"
        )
    """
    chamber: Chamber | str | None = None
    code: str | None = Field(None, alias="systemCode")  # API uses "systemCode"
    name: str | None = None
    type: CommitteeType | str | None = None
    url: str | None = None
    updateDate: datetime | None = None


class MemberRef(Model):
    """
    Lightweight reference to a Member entity.
    
    Contains only essential identification information for referencing
    a congressional member without requiring the full Member model.
    
    Use Cases:
    - In Sponsor/Cosponsor models instead of full Member
    - In Action models to reference members who took action
    - In Vote models to reference voting members
    - In Committee models to reference committee members
    
    Example:
        member_ref = MemberRef(
            bioguideId="A000374",
            name="Ralph Abraham",
            party="R",
            state="LA",
            district=5,
            url="https://api.congress.gov/v3/member/A000374"
        )
    """
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
    """
    Lightweight reference to an Amendment entity.
    
    Contains only essential identification information for referencing
    an amendment without requiring the full Amendment model.
    
    Use Cases:
    - In Bill models to reference amendments
    - In Action models to reference amendments being acted upon
    - In Amendment models to reference parent/related amendments
    
    Example:
        amendment_ref = AmendmentRef(
            congress=118,
            type="hamdt",
            number=100,
            description="Amendment to add section on infrastructure",
            url="https://api.congress.gov/v3/amendment/118/hamdt/100"
        )
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
    """
    Lightweight reference to a Treaty entity.
    
    Contains only essential identification information for referencing
    a treaty without requiring the full Treaty model.
    
    Use Cases:
    - In action models to reference treaties
    - In committee models to reference treaties under consideration
    
    Example:
        treaty_ref = TreatyRef(
            congress=118,
            number=1,
            suffix="A",
            title="Treaty on Nuclear Non-Proliferation",
            url="https://api.congress.gov/v3/treaty/118/1"
        )
    """
    congress: int | None = None
    number: int | None = None
    suffix: str | None = None  # e.g., "A", "B", etc.
    title: str | None = None
    topic: str | None = None
    url: str | None = None
    transmittedDate: date | None = None
    updateDate: datetime | None = None


class NominationRef(Model):
    """
    Lightweight reference to a Nomination entity.
    
    Contains only essential identification information for referencing
    a nomination without requiring the full Nomination model.
    
    Use Cases:
    - In action models to reference nominations
    - In committee models to reference nominations under consideration
    
    Example:
        nomination_ref = NominationRef(
            congress=118,
            number=100,
            partNumber=1,
            citation="PN100",
            description="John Doe to be Secretary of State"
        )
    """
    congress: int | None = None
    number: int | None = None
    partNumber: int | None = None
    citation: str | None = None  # e.g., "PN100"
    description: str | None = None
    receivedDate: date | None = None
    url: str | None = None
    updateDate: datetime | None = None


# ============================================================================
# HELPER FUNCTIONS FOR REFERENCE CONVERSION
# ============================================================================


def bill_to_ref(bill: Any) -> BillRef:
    """
    Convert a full Bill model to a lightweight BillRef.
    
    Args:
        bill: Full Bill model instance (or dict-like object)
        
    Returns:
        BillRef with essential identification info
        
    Example:
        full_bill = bill_service.get(congress=118, type="hr", number=1)
        bill_ref = bill_to_ref(full_bill)
    """
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
    """
    Convert a full Committee model to a lightweight CommitteeRef.
    
    Args:
        committee: Full Committee model instance (or dict-like object)
        
    Returns:
        CommitteeRef with essential identification info
        
    Example:
        full_committee = committee_service.get(chamber="house", committee_code="hspw00")
        committee_ref = committee_to_ref(full_committee)
    """
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
    """
    Convert a full Member model to a lightweight MemberRef.
    
    Args:
        member: Full Member model instance (or dict-like object)
        
    Returns:
        MemberRef with essential identification info
        
    Example:
        full_member = member_service.get(bioguide_id="A000374")
        member_ref = member_to_ref(full_member)
    """
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
    """
    Convert a full Amendment model to a lightweight AmendmentRef.
    
    Args:
        amendment: Full Amendment model instance (or dict-like object)
        
    Returns:
        AmendmentRef with essential identification info
        
    Example:
        full_amendment = amendment_service.get(congress=118, type="hamdt", number=100)
        amendment_ref = amendment_to_ref(full_amendment)
    """
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
    """
    Convert a full Treaty model to a lightweight TreatyRef.
    
    Args:
        treaty: Full Treaty model instance (or dict-like object)
        
    Returns:
        TreatyRef with essential identification info
    """
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
    """
    Convert a full Nomination model to a lightweight NominationRef.
    
    Args:
        nomination: Full Nomination model instance (or dict-like object)
        
    Returns:
        NominationRef with essential identification info
    """
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



