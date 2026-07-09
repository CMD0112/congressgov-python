"""
Base classes and types for congressgov models

This module contains the foundational classes that all other modules depend on:
- Model: Base Pydantic model class
- Enums: All enumeration types
- Types: Generic types like CountRef, URL, PolicyArea
"""

from .model import Model, Pagination, ApiEnvelope
from .enums import (
    AmendmentType,
    LegislationType,
    Chamber,
    CommitteeType,
    CommunicationCode,
    DocumentTypes,
    LawType,
    MeetingStatus,
    MeetingType,
    ReportType,
    SessionType,
    StateCode,
    TextFormatType,
    TextVersionType,
    TitleTypeCode,
    WitnessDocumentTypes,
    ActionType,
    ActionCode,
    VersionCode
)
from .types import CountRef, URL, PolicyArea
from .utility import pretty_print_json
from .references import (
    BillRef,
    CommitteeRef,
    MemberRef,
    AmendmentRef,
    TreatyRef,
    NominationRef,
    bill_to_ref,
    committee_to_ref,
    member_to_ref,
    amendment_to_ref,
    treaty_to_ref,
    nomination_to_ref,
)

__all__ = [
    # Base models
    "Model",
    "Pagination", 
    "ApiEnvelope",
    
    # Enums
    "AmendmentType",
    "LegislationType",
    "Chamber",
    "CommitteeType",
    "CommunicationCode",
    "DocumentTypes",
    "LawType",
    "MeetingStatus",
    "MeetingType",
    "ReportType",
    "SessionType",
    "StateCode",
    "TextFormatType",
    "TextVersionType",
    "TitleTypeCode",
    "WitnessDocumentTypes",
    "ActionType",
    "ActionCode",
    "VersionCode",
    
    # Types
    "CountRef",
    "URL",
    "PolicyArea",
    
    # Reference Models
    "BillRef",
    "CommitteeRef",
    "MemberRef",
    "AmendmentRef",
    "TreatyRef",
    "NominationRef",
    
    # Reference Converters
    "bill_to_ref",
    "committee_to_ref",
    "member_to_ref",
    "amendment_to_ref",
    "treaty_to_ref",
    "nomination_to_ref",
    
    # Utilities
    "pretty_print_json",
]
