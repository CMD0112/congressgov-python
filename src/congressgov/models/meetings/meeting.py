from __future__ import annotations
from pydantic import Field, AliasChoices
from ..base.enums import DocumentTypes, WitnessDocumentTypes, MeetingType, MeetingStatus
from datetime import date, datetime
from ..base.enums import Chamber
from ..base.types import URL
from ..base.model import Model
# from ..entities.committee import Committees  # Temporarily disabled due to circular import
# === [FORWARD REFERENCES] Use string references to avoid circular imports ===
# from .core import Bill
# from .treaty import Treaty
# from .nomination import Nomination


class CommitteeMeetingRef(Model):
    eventId: str | None = None
    url: str | URL | None = None
    updateDate: date | str | None = None
    congress: int | None = None
    chamber: Chamber | None = None
    
    @property
    def event_id(self) -> str | None:
        return self.eventId
    
    @event_id.setter
    def event_id(self, value: str | None) -> None:
        self.eventId = value
    
    @property
    def update_date(self) -> date | str | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: date | str | None) -> None:
        self.updateDate = value


# CommitteeMeetingRef.model_rebuild()  # Handled by centralized rebuild system
    
    
class CommitteeMeetings(Model):
    """
    === CommitteeMeetings Model ===
    Represents a container for a list of CommitteeMeetingRef objects.
    """
    meetings: list[CommitteeMeetingRef] | None = Field(None, alias="committeeMeetings")


# CommitteeMeetings.model_rebuild()  # Handled by centralized rebuild system

    # @classmethod
    # def model_validate(cls, obj, **kwargs):
    #     # If a list is passed directly, wrap it in a dict under the correct alias
    #     if isinstance(obj, list):
    #         obj = {"committeeMeetings": obj}
    #     # If it's already a dict with the correct key, do not wrap again
    #     elif isinstance(obj, dict) and set(obj.keys()) == {"committeeMeetings"}:
    #         pass  # Use as-is
    #     return super().model_validate(obj, **kwargs)


class CommitteeLocation(Model):
    room: str | None = None
    building: str | None = None
    address: str | None = None


# CommitteeLocation.model_rebuild()  # Handled by centralized rebuild system


class CommitteeLocations(Model):
    """
    === CommitteeLocations Model ===
    Represents a container for a list of CommitteeLocation objects.
    """
    locations: list[CommitteeLocation] | None = Field(None, alias="locations")


# CommitteeLocations.model_rebuild()  # Handled by centralized rebuild system


class CommitteeVideo(Model):
    name: str | None = None
    url: str | URL | None = None


# CommitteeVideo.model_rebuild()  # Handled by centralized rebuild system


class CommitteeVideos(Model):
    """
    === CommitteeVideos Model ===
    Represents a container for a list of CommitteeVideo objects.
    """
    videos: list[CommitteeVideo] | None = Field(None, alias="videos")


# CommitteeVideos.model_rebuild()  # Handled by centralized rebuild system


class CommitteeWitness(Model):
    name: str | None = None
    position: str | None = None
    organization: str | None = None


# CommitteeWitness.model_rebuild()  # Handled by centralized rebuild system


class CommitteeWitnesses(Model):
    """
    === CommitteeWitnesses Model ===
    Represents a container for a list of CommitteeWitness objects.
    """
    witnesses: list[CommitteeWitness] | None = Field(None, alias="witnesses")


# CommitteeWitnesses.model_rebuild()  # Handled by centralized rebuild system


class CommitteeWitnessDocument(Model):
    documentType: WitnessDocumentTypes | None = None
    format: str | None = None
    url: str | URL | None = None
    
    @property
    def document_type(self) -> WitnessDocumentTypes | None:
        return self.documentType
    
    @document_type.setter
    def document_type(self, value: WitnessDocumentTypes | None) -> None:
        self.documentType = value


# CommitteeWitnessDocument.model_rebuild()  # Handled by centralized rebuild system
    

class CommitteeWitnessDocuments(Model):
    """
    === CommitteeWitnessDocuments Model ===
    Represents a container for a list of CommitteeWitnessDocument objects.
    """
    documents: list[CommitteeWitnessDocument] | None = Field(None, alias="documents")


# CommitteeWitnessDocuments.model_rebuild()  # Handled by centralized rebuild system


class CommitteeMeetingDocument(Model):
    name: str | None = None
    description: str | None = None
    documentType: DocumentTypes | None = None
    url: str | URL | None = None
    
    @property
    def document_type(self) -> DocumentTypes | None:
        return self.documentType
    
    @document_type.setter
    def document_type(self, value: DocumentTypes | None) -> None:
        self.documentType = value


# CommitteeMeetingDocument.model_rebuild()  # Handled by centralized rebuild system


class CommitteeHearingTranscript(Model):
    jacketNumber: str | None = None
    url: str | URL | None = None
    
    @property
    def jacket_number(self) -> str | None:
        return self.jacketNumber
    
    @jacket_number.setter
    def jacket_number(self, value: str | None) -> None:
        self.jacketNumber = value


# CommitteeHearingTranscript.model_rebuild()  # Handled by centralized rebuild system


class RelatedItems(Model):
    bills: "list[Bill] | None" = None
    treaties: "list[Treaty] | None" = None
    nominations: "list[Nomination] | None" = None


# RelatedItems.model_rebuild()  # Handled by centralized rebuild system


class CommitteeMeeting(Model):      # TODO: Needs work
    eventId: str | None = None
    updateDate: date | str | None = None
    congress: int | None = None
    type: MeetingType | None = None
    title: str | None = None
    meetingStatus: MeetingStatus | None = None
    date: date | str | None = None
    chamber: Chamber | None = None
    committees: "list[Committee] | Committee | None" = None
    continuations: list[datetime] | None = None
    location: list[CommitteeLocation] | CommitteeLocation | None = Field(None, alias=AliasChoices("locations", "location"))
    videos: list[CommitteeVideo] | CommitteeVideo | None = None
    relatedItems: RelatedItems | None = None
    
    # Field to handle the JSON key for auto-unwrapping prevention
    committeeMeeting: dict | None = None
    
    @property
    def event_id(self) -> str | None:
        return self.eventId
    
    @event_id.setter
    def event_id(self, value: str | None) -> None:
        self.eventId = value
    
    @property
    def update_date(self) -> date | str | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: date | str | None) -> None:
        self.updateDate = value
    
    @property
    def meeting_status(self) -> MeetingStatus | None:
        return self.meetingStatus
    
    @meeting_status.setter
    def meeting_status(self, value: MeetingStatus | None) -> None:
        self.meetingStatus = value
    
    @property
    def related_items(self) -> RelatedItems | None:
        return self.relatedItems
    
    @related_items.setter
    def related_items(self, value: RelatedItems | None) -> None:
        self.relatedItems = value


# CommitteeMeeting.model_rebuild()  # Handled by centralized rebuild system


# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
