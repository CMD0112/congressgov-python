from __future__ import annotations
from typing import List, Optional
from datetime import datetime, date
from pydantic import Field
from ..base.enums import Chamber, TitleTypeCode, SourceSystemCode
from ..base.types import URL
from ..base.model import Model

# Bill, Bills, and TextVersionItem live in entities.bill; importing them here
# would create a circular dependency, so Bill/Amendment/Treaty references
# elsewhere in this module use string forward references instead.
from ..actions.action import LatestAction

# Law, CBOCostEstimate, and Subject were moved here (from entities.bill) for the same reason.

class Law(Model):
    type: str | None = None
    number: int | str | None = None

    @property
    def law_type(self) -> str | None:
        return self.type

    @law_type.setter
    def law_type(self, value: str | None) -> None:
        self.type = value

    @property
    def law_number(self) -> int | None:
        return self.number

    @law_number.setter
    def law_number(self, value: int | None) -> None:
        self.number = value


class Laws(Model):
    laws: list[Law] | None = Field(None, alias="laws")


class Subject(Model):
    legislativeSubjects: list[str | dict] | None = None  # Can be strings or objects with name/updateDate
    policyArea: str | dict | None = None  # Can be string or object with name/updateDate

    @property
    def legislative_subjects(self) -> list[str | dict] | None:
        return self.legislativeSubjects

    @legislative_subjects.setter
    def legislative_subjects(self, value: list[str | dict] | None) -> None:
        self.legislativeSubjects = value

    @property
    def policy_area(self) -> str | dict | None:
        return self.policyArea

    @policy_area.setter
    def policy_area(self, value: str | dict | None) -> None:
        self.policyArea = value


class Subjects(Model):
    """
    === Subjects Model ===
    Represents a container for a single Subject object (not a list).
    The API returns a single subject object with legislativeSubjects and policyArea fields.
    """
    subjects: Subject | None = Field(None, alias="legislativeSubjects", validation_alias="legislativeSubjects")


class CBOCostEstimate(Model):
    pubDate: Optional[datetime] = None
    title: Optional[str] = None
    url: Optional[URL | str] = None
    description: Optional[str] = None

    @property
    def pub_date(self) -> Optional[datetime]:
        return self.pubDate

    @pub_date.setter
    def pub_date(self, value: Optional[datetime]) -> None:
        self.pubDate = value


class CBOCostEstimates(Model):
    cboCostEstimates: Optional[List[CBOCostEstimate]] = Field(None, alias="cboCostEstimates")


# Model rebuild statements for entity classes
# Law.model_rebuild()  # Handled by centralized rebuild system
# Laws.model_rebuild()  # Handled by centralized rebuild system
# Subject.model_rebuild()  # Handled by centralized rebuild system
# Subjects.model_rebuild()  # Handled by centralized rebuild system
# CBOCostEstimate.model_rebuild()  # Handled by centralized rebuild system
# CBOCostEstimates.model_rebuild()  # Handled by centralized rebuild system


class SourceSystem(Model):
    code: SourceSystemCode | None = None
    name: str | None = None

# Action, Actions, ActionsRef classes moved to actions/action.py to avoid duplication


# AmendmentRef class moved to entities/amendment.py to avoid duplication


class CommitteeBills(Model):
    """
    === CommitteeBills Model ===
    Represents a container for a list of Bill objects, with optional URL and count metadata.
    Provides a custom model_validate method to flexibly accept either a list of bills,
    a dict with 'bills' key, or a single bill dict, for seamless Pydantic parsing.
    """
    url: str | None = None
    count: int | None = None
    bills: list["Bill"] | None = Field(None, alias="committee-bills")

    # @classmethod
    # def _get_container_key(cls) -> str:
    #     return "committee-bills"


# CommitteeBills.model_rebuild()  # Moved to after Bill is defined


class CommitteeNomination(Model):
    congress: int | None = None
    number: str | int | None = None  # Allow both string and int
    partNumber: str | None = None
    citation: str | None = None
    description: str | None = None
    receivedDate: date | str | None = None  # Allow datetime strings
    nominationType: dict[str, bool] | None = None
    updateDate: date | str | None = None  # Allow datetime strings
    latestAction: "LatestAction | None" = None
    
    @property
    def part_number(self) -> str | None:
        return self.partNumber
    
    @part_number.setter
    def part_number(self, value: str | None) -> None:
        self.partNumber = value
    
    @property
    def received_date(self) -> date | None:
        return self.receivedDate
    
    @received_date.setter
    def received_date(self, value: date | None) -> None:
        self.receivedDate = value
    
    @property
    def nomination_type(self) -> dict[str, bool] | None:
        return self.nominationType
    
    @nomination_type.setter
    def nomination_type(self, value: dict[str, bool] | None) -> None:
        self.nominationType = value
    
    @property
    def update_date(self) -> date | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: date | None) -> None:
        self.updateDate = value
    
    @property
    def latest_action(self) -> "LatestAction | None":
        return self.latestAction
    
    @latest_action.setter
    def latest_action(self, value: "LatestAction | None") -> None:
        self.latestAction = value


# CommitteeNomination.model_rebuild()  # Moved to after LatestAction is defined


class CommitteeNominations(Model):
    """
    === CommitteeNominations Model ===
    Represents a container for a list of CommitteeNomination objects.
    """
    nominations: list[CommitteeNomination] | None = Field(None, alias="nominations")

    # @classmethod
    # def _get_container_key(cls) -> str:
    #     return "nominations"


# CommitteeNominations.model_rebuild()  # Moved to after CommitteeNomination is defined


# CalendarNumber class moved to actions/calendar.py to avoid duplication
# LatestAction class moved to actions/action.py to avoid duplication
# AmendmentRef.model_rebuild()  # Moved to entities/amendment.py
# CommitteeNomination.model_rebuild()  # Commented out due to forward reference issues
# CommitteeNominations.model_rebuild()  # Commented out due to forward reference issues


class Note(Model):
    text: str | None = None


# Note.model_rebuild()  # Handled by centralized rebuild system


class Notes(Model):
    """
    === Notes Model ===
    Represents a container for a list of Note objects.
    """
    notes: List[Note] | None = Field(None, alias="notes")

    # @classmethod
    # def _get_container_key(cls) -> str:
    #     return "notes"


# Notes.model_rebuild()  # Handled by centralized rebuild system


# OnBehalfOfSponsor and OnBehalfOfSponsors classes moved to entities/sponsor.py to avoid duplication


# RecordedVote and RecordedVotes classes moved to actions/vote.py to avoid duplication


# Sponsor, Cosponsor, OnBehalfOfSponsor classes moved to entities/sponsor.py to avoid duplication


# TextVersion* classes moved to entities/bill.py to avoid duplication
    

class Title(Model):
    title: str | None = None
    titleType: str | None = None
    chamberCode: Chamber | None = None  # Can be Chamber enum or string like 'J' for Joint
    chamberName: Chamber | None = None  # Can be Chamber enum or string like 'Joint'
    billTextVersionName: str | None = None
    billTextVersionCode: str | None = None
    titleTypeCode: TitleTypeCode | int | None = None  # Can be TitleTypeCode enum or integer
    updateDate: str | None = None

    @property
    def title_type(self) -> str | None:
        return self.titleType

    @title_type.setter
    def title_type(self, value: str | None) -> None:
        self.titleType = value

    @property
    def chamber_code(self) -> Chamber | str | None:
        return self.chamberCode

    @chamber_code.setter
    def chamber_code(self, value: Chamber | str | None) -> None:
        self.chamberCode = value

    @property
    def chamber_name(self) -> Chamber | str | None:
        return self.chamberName

    @chamber_name.setter
    def chamber_name(self, value: Chamber | str | None) -> None:
        self.chamberName = value

    @property
    def bill_text_version_name(self) -> str | None:
        return self.billTextVersionName

    @bill_text_version_name.setter
    def bill_text_version_name(self, value: str | None) -> None:
        self.billTextVersionName = value

    @property
    def bill_text_version_code(self) -> str | None:
        return self.billTextVersionCode

    @bill_text_version_code.setter
    def bill_text_version_code(self, value: str | None) -> None:
        self.billTextVersionCode = value

    @property
    def title_type_code(self) -> TitleTypeCode | int | None:
        return self.titleTypeCode

    @title_type_code.setter
    def title_type_code(self, value: TitleTypeCode | int | None) -> None:
        self.titleTypeCode = value

    @property
    def update_date(self) -> str | None:
        return self.updateDate

    @update_date.setter
    def update_date(self, value: str | None) -> None:
        self.updateDate = value


# Title.model_rebuild()  # Handled by centralized rebuild system


class Titles(Model):
    """
    === Titles Model ===
    Represents a container for a list of Title objects.
    """
    titles: List[Title] | None = Field(None, alias="titles")


# Titles.model_rebuild()  # Handled by centralized rebuild system


# Treaty, Treaties classes moved to entities/treaty.py to avoid duplication
# Amendment, Amendments classes moved to entities/amendment.py to avoid duplication
    

# Bill, Bills classes moved to entities/bill.py to avoid duplication
