from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING
from pydantic import AliasChoices, Field

from ..base.enums import Chamber, CommitteeType, ReportType
from ..base.model import Model

# Import protocols for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    from congressgov.services.protocols.committee import CommitteeProtocol, CommitteesProtocol
    from congressgov.services.protocols.async_committee import AsyncCommitteeProtocol
from ..base.types import CountRef
from ..base.references import BillRef, NominationRef


class CommitteeActivity(Model):
    name: str | None = None
    date: str | date | None = None


class CommitteeActivities(Model):
    """A container for a list of `CommitteeActivity` objects."""
    activities: list[CommitteeActivity] | None = Field(None, alias="activities")


class CommitteeRef(Model):
    """A minimal committee reference for linking purposes."""
    systemCode: str | None = None
    name: str | None = None
    chamber: Chamber | None = None
    type: CommitteeType | None = None
    url: str | None = None


class CommitteeShortRef(Model):
    """An even more minimal committee reference (no url)."""
    systemCode: str | None = None
    name: str | None = None
    chamber: Chamber | None = None
    type: CommitteeType | None = None


class Committees(Model):
    """A container for a list of `Committee` objects."""
    committees: list["Committee"] | None = Field(None, alias=AliasChoices("committees", "treatyCommittees"))


class Subcommittees(Model):
    """A container for a list of `Committee` objects (as subcommittees)."""
    subcommittees: list["Committee"] | None = Field(None, alias="subcommittees") 


class History(Model):
    endDate: date | str | None = None
    officialName: str | None = None
    libraryOfCongressName: str | None = None
    committeeTypeCode: CommitteeType | None = None
    establishingAuthority: str | None = None
    locLinkedDataId: str | None = None
    superintendentDocumentNumber: str | None = None
    naraId: str | None = None
    
    @property
    def end_date(self) -> date | None:
        return self.endDate
    
    @end_date.setter
    def end_date(self, value: date | None) -> None:
        self.endDate = value
    
    @property
    def official_name(self) -> str | None:
        return self.officialName
    
    @official_name.setter
    def official_name(self, value: str | None) -> None:
        self.officialName = value
    
    @property
    def library_of_congress_name(self) -> str | None:
        return self.libraryOfCongressName
    
    @library_of_congress_name.setter
    def library_of_congress_name(self, value: str | None) -> None:
        self.libraryOfCongressName = value
    
    @property
    def committee_type_code(self) -> CommitteeType | None:
        return self.committeeTypeCode
    
    @committee_type_code.setter
    def committee_type_code(self, value: CommitteeType | None) -> None:
        self.committeeTypeCode = value
    
    @property
    def establishing_authority(self) -> str | None:
        return self.establishingAuthority
    
    @establishing_authority.setter
    def establishing_authority(self, value: str | None) -> None:
        self.establishingAuthority = value
    
    @property
    def loc_linked_data_id(self) -> str | None:
        return self.locLinkedDataId
    
    @loc_linked_data_id.setter
    def loc_linked_data_id(self, value: str | None) -> None:
        self.locLinkedDataId = value
    
    @property
    def superintendent_document_number(self) -> str | None:
        return self.superintendentDocumentNumber
    
    @superintendent_document_number.setter
    def superintendent_document_number(self, value: str | None) -> None:
        self.superintendentDocumentNumber = value
    
    @property
    def nara_id(self) -> str | None:
        return self.naraId
    
    @nara_id.setter
    def nara_id(self, value: str | None) -> None:
        self.naraId = value


class CommitteeHistory(Model):
    history: list[History] | None = None


class CommitteeReport(Model):
    citation: str | None = None
    url: str | None = None
    updateDate: date | str | None = None  # Allow datetime strings
    congress: int | None = None
    chamber: Chamber | None = None
    type: ReportType | None = None
    number: str | int | None = None  # Allow both string and int
    part: str | int | None = None  # Allow both string and int


class CommitteeReports(Model):
    """A container for a list of `CommitteeReport` objects."""
    reports: list[CommitteeReport] | None = Field(None, alias="reports")


class CommitteeBills(Model):
    """A container for a committee's bills, as `BillRef`s (to avoid a circular
    import with the full `Bill` model), with optional url/count metadata.
    """
    url: str | None = None
    count: int | None = None
    bills: list[BillRef] | None = Field(None, alias="committee-bills")


class Committee(Model):
    """A congressional committee or subcommittee: its parent/children, bills,
    reports, communications, and nominations. Bills and nominations use
    lightweight reference models (`BillRef`, `NominationRef`) to avoid
    circular imports with the full `Bill`/`Nomination` models; reports and
    communications are kept as plain dicts for the same reason.
    """
    systemCode: str | None = None
    parent: "Committee | None" = None  # Self-reference is fine
    updateDate: date | str | None = None
    isCurrent: bool | None = None
    subcommittees: list["Committee"] | CountRef | None = None  # Self-reference is fine
    reports: list[dict] | CountRef | None = None
    communications: list[dict] | CountRef | None = None
    bills: CommitteeBills | None = None
    nominations: list[NominationRef] | CountRef | None = None
    history: list["History"] | CountRef | None = None  # Can be list or reference
    url: str | None = None
    name: str | None = None
    chamber: Chamber | None = None
    type: CommitteeType | None = Field(None, alias="committeeTypeCode")
    committeeTypeCode: CommitteeType | None = None
    activities: list[CommitteeActivity] | CountRef | None = None  # Can be list or reference
    
    @property
    def committeeType(self) -> str | None:
        return self.committeeTypeCode or self.type

    @committeeType.setter
    def committeeType(self, value: str | None) -> None:
        if self.committeeTypeCode is not None or 'committeeTypeCode' in self.__dict__:
            self.committeeTypeCode = value
        else:
            self.type = value

    @property
    def committee_type(self) -> str | None:
        return self.committeeType

    @committee_type.setter
    def committee_type(self, value: str | None) -> None:
        self.committeeType = value

    @property
    def system_code(self) -> str | None:
        return self.systemCode

    @system_code.setter
    def system_code(self, value: str | None) -> None:
        self.systemCode = value


# Model rebuild statements
# CommitteeActivity.model_rebuild()  # Handled by centralized rebuild system
# CommitteeActivities.model_rebuild()  # Handled by centralized rebuild system
# CommitteeRef.model_rebuild()  # Handled by centralized rebuild system
# CommitteeShortRef.model_rebuild()  # Handled by centralized rebuild system
# Committees.model_rebuild()  # Handled by centralized rebuild system
# Subcommittees.model_rebuild()  # Handled by centralized rebuild system
# History.model_rebuild()  # Handled by centralized rebuild system
# CommitteeHistory.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReport.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReports.model_rebuild()  # Handled by centralized rebuild system
# CommitteeBills.model_rebuild()  # Handled by centralized rebuild system
# Committee.model_rebuild()  # Handled by centralized rebuild system

# Add Protocol inheritance for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    # Create intersection types for IDE awareness without changing runtime behavior
    class Committee(Model, CommitteeProtocol, AsyncCommitteeProtocol):
        """Committee model with sync and async extension method type hints for IDE support."""
        pass
    
    class Committees(Model, CommitteesProtocol):
        """Committees collection with extension method type hints for IDE support."""
        pass
