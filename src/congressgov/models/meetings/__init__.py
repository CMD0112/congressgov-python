"""
Meeting-related classes for congressgov models

This module contains classes for committee meetings, witnesses, and related documents.
"""

from .meeting import CommitteeMeeting, CommitteeMeetingRef, CommitteeMeetings
from .meeting import CommitteeWitness, CommitteeWitnesses, CommitteeWitnessDocument

__all__ = [
    # Meetings
    "CommitteeMeeting",
    "CommitteeMeetingRef", 
    "CommitteeMeetings",
    
    # Witnesses
    "CommitteeWitness",
    "CommitteeWitnesses",
    "CommitteeWitnessDocument",
]
