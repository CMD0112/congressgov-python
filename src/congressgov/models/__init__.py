"""
congressgov models package

This package provides comprehensive data models for working with Congressional data,
including bills, members, committees, and various legislative documents.

All classes are designed to work with the Congress.gov API and provide type-safe,
validated data structures with enhanced parsing capabilities.

IMPORT EXAMPLES:
    # Import from the models package
    from congressgov.models import Bill, Member

    # Import from submodules
    from congressgov.models.entities.bill import Bill
    from congressgov.models.base.model import Model, Pagination

STRUCTURE:
    This package is organized into logical groups:
    1. Base Infrastructure (Model, Pagination, Enums, Types)
    2. Core Entities (Bill, Amendment, Member, Committee)
    3. Documents (Congressional Record, Reports, Hearings)
    4. Communications & Votes (House/Senate Communications, Votes)
    5. Supporting Models (Actions, Meetings, Nominations)
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("congressgov")
except PackageNotFoundError:
    __version__ = "0.1.0"

# =============================================================================
# BASE INFRASTRUCTURE (Always imported)
# =============================================================================

# Base models and API infrastructure
from .base import Model, Pagination, ApiEnvelope

# All enums used throughout the package
from .base import (
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

# Generic/common utility models
from .base import CountRef, URL, PolicyArea

# =============================================================================
# CORE ENTITIES (Commonly used - imported directly)
# =============================================================================

from .entities import (
    Bill,
    Bills,
    Law,
    Subject,
    CBOCostEstimate,
    ConstitutionalAuthorityStatement,
    Summary,
    Summaries,
    Member,
    Members,
    Term,
    Depiction,
    # Committee,
    # Committees,
    # CommitteeRef,
    # CommitteeShortRef,
    Amendment,
    Amendments,
    AmendmentRef,
    Treaty,
    Treaties,
    Congress,
    Congresses,
    CongressSession,
    CongressSessions
)

# Communication classes
from .communications import (
    HouseCommunication,
    HouseCommunications,
    SenateCommunication,
    SenateCommunications,
    HouseRequirement,
    HouseRequirements,
    MatchingCommunication,
    HouseVote,
    HouseVotes,
    MemberVotes
)

# Core classes
from .core import (
    Note,
    Notes,
    Title,
    Titles
)

# Action classes
from .actions import (
    Action,
    Actions,
    ActionsRef,
    LatestAction,
    RecordedVote,
    RecordedVotes,
    CalendarNumber
)

# Sponsor classes
from .entities import (
    OnBehalfOfSponsor,
    OnBehalfOfSponsors,
    Sponsor,
    Sponsors,
    Cosponsor,
    Cosponsors,
    CosponsorsRef
)

# Text version classes
from .entities import (
    TextVersionFormat,
    TextVersionFormats,
    TextVersionItem,
    TextVersions
)

# =============================================================================
# LAZY LOADING FOR LESS COMMON CLASSES
# =============================================================================

def get_action():
    """Lazy load Action class to avoid circular imports"""
    from .actions import Action
    return Action

def get_actions():
    """Lazy load Actions class to avoid circular imports"""
    from .actions import Actions
    return Actions

def get_recorded_vote():
    """Lazy load RecordedVote class to avoid circular imports"""
    from .actions import RecordedVote
    return RecordedVote

def get_recorded_votes():
    """Lazy load RecordedVotes class to avoid circular imports"""
    from .actions import RecordedVote
    return RecordedVote

def get_committee_meeting():
    """Lazy load CommitteeMeeting class to avoid circular imports"""
    from .meetings import CommitteeMeeting
    return CommitteeMeeting

def get_committee_meetings():
    """Lazy load CommitteeMeetings class to avoid circular imports"""
    from .meetings import CommitteeMeetings
    return CommitteeMeetings

def get_hearing():
    """Lazy load Hearing class to avoid circular imports"""
    from .documents import Hearing
    return Hearing

def get_hearings():
    """Lazy load Hearings class to avoid circular imports"""
    from .documents import Hearings
    return Hearings

def get_committee_report():
    """Lazy load CommitteeReport class to avoid circular imports"""
    from .documents import CommitteeReport
    return CommitteeReport

def get_committee_reports():
    """Lazy load CommitteeReports class to avoid circular imports"""
    from .documents import CommitteeReports
    return CommitteeReports

def get_crs_report():
    """Lazy load CRSReport class to avoid circular imports"""
    from .documents import CRSReport
    return CRSReport

def get_crs_reports():
    """Lazy load CRSReports class to avoid circular imports"""
    from .documents import CRSReports
    return CRSReports

def get_bound_congressional_record():
    """Lazy load BoundCongressionalRecord class to avoid circular imports"""
    from .documents import BoundCongressionalRecord
    return BoundCongressionalRecord

def get_bound_congressional_records():
    """Lazy load BoundCongressionalRecords class to avoid circular imports"""
    from .documents import BoundCongressionalRecords
    return BoundCongressionalRecords

def get_committee():
    """Lazy load Committee class to avoid circular imports"""
    from .committees import Committee
    return Committee

def get_committees():
    """Lazy load Committees class to avoid circular imports"""
    from .committees import Committees
    return Committees

def get_committee_ref():
    """Lazy load CommitteeRef class to avoid circular imports"""
    from .committees import CommitteeRef
    return CommitteeRef

def get_committee_short_ref():
    """Lazy load CommitteeShortRef class to avoid circular imports"""
    from .committees import CommitteeShortRef
    return CommitteeShortRef

def get_house_communication():
    """Lazy load HouseCommunication class to avoid circular imports"""
    from .communications import HouseCommunication
    return HouseCommunication

def get_house_communications():
    """Lazy load HouseCommunications class to avoid circular imports"""
    from .communications import HouseCommunications
    return HouseCommunications

def get_senate_communication():
    """Lazy load SenateCommunication class to avoid circular imports"""
    from .communications import SenateCommunication
    return SenateCommunication

def get_senate_communications():
    """Lazy load SenateCommunications class to avoid circular imports"""
    from .communications import SenateCommunications
    return SenateCommunications

def get_house_vote():
    """Lazy load HouseVote class to avoid circular imports"""
    from .communications import HouseVote
    return HouseVote

def get_house_votes():
    """Lazy load HouseVotes class to avoid circular imports"""
    from .communications import HouseVotes
    return HouseVotes

def get_nomination():
    """Lazy load Nomination class to avoid circular imports"""
    from .nominations import Nomination
    return Nomination

def get_nominations():
    """Lazy load Nominations class to avoid circular imports"""
    from .nominations import Nominations
    return Nominations

def get_summary():
    """Lazy load Summary class to avoid circular imports"""
    from .summaries import Summary
    return Summary

def get_summaries():
    """Lazy load Summaries class to avoid circular imports"""
    from .summaries import Summaries
    return Summaries

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base infrastructure
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
    
    # Core entities
    "Bill",
    "Bills",
    "Law",
    "Subject", 
    "CBOCostEstimate",
    "ConstitutionalAuthorityStatement",
    "Summary",
    "Summaries",
    "Member",
    "Members",
    "Term",
    "Depiction",
    # "Committee",
    # "Committees", 
    # "CommitteeRef",
    # "CommitteeShortRef",
    "Amendment",
    "Amendments",
    "AmendmentRef",
    "Treaty",
    "Treaties",
    "Congress",
    "Congresses",
    "CongressSession",
    "CongressSessions",
    
    # Communications
    "HouseCommunication",
    "HouseCommunications",
    "SenateCommunication",
    "SenateCommunications",
    "HouseRequirement",
    "HouseRequirements",
    "MatchingCommunication",
    "HouseVote",
    "HouseVotes",
    "MemberVotes",
    
    # Core classes
    "Action",
    "Actions",
    "ActionsRef",
    "LatestAction",
    "RecordedVote",
    "RecordedVotes",
    "CalendarNumber",
    "Note",
    "Notes",
    "OnBehalfOfSponsor",
    "OnBehalfOfSponsors",
    "Sponsor",
    "Sponsors",
    "Cosponsor",
    "Cosponsors",
    "CosponsorsRef",
    "TextVersionFormat",
    "TextVersionFormats",
    "TextVersionItem",
    "TextVersions",
    "Title",
    "Titles",
    
    # Lazy loading functions
    "get_action",
    "get_actions",
    "get_recorded_vote",
    "get_recorded_votes",
    "get_committee_meeting",
    "get_committee_meetings",
    "get_hearing",
    "get_hearings",
    "get_committee_report",
    "get_committee_reports",
    "get_crs_report",
    "get_crs_reports",
    "get_house_communication",
    "get_house_communications",
    "get_senate_communication",
    "get_senate_communications",
    "get_house_vote",
    "get_house_votes",
    "get_nomination",
    "get_nominations",
    "get_summary",
    "get_summaries",
    "get_bound_congressional_record",
    "get_bound_congressional_records",
    "get_committee",
    "get_committees",
    "get_committee_ref",
    "get_committee_short_ref",
]

# =============================================================================
# CENTRALIZED MODEL REBUILD SYSTEM
# =============================================================================

# Import the rebuild system
from .base.rebuild import rebuild_all_models

# Rebuild all models after all imports to resolve forward references
rebuild_all_models()