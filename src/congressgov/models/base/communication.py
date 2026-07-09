from __future__ import annotations
from datetime import date
from typing import Any, Dict
from pydantic import Field

from .model import Model
from .enums import Chamber
from ..committees import Committee


class CommunicationType(Model):
    code: str | None = None
    name: str | None = None
    congress: int | None = None
    referralDate: date | None = None
    updateDate: date | None = None
    url: str | None = None
    
    @property
    def referral_date(self) -> date | None:
        return self.referralDate
    
    @referral_date.setter
    def referral_date(self, value: date | None) -> None:
        self.referralDate = value
    
    @property
    def update_date(self) -> date | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: date | None) -> None:
        self.updateDate = value


class BaseCommunication(Model):
    """Base class for all communication types"""
    chamber: Chamber | None = None
    number: str | int | None = None
    communicationType: CommunicationType | None = None


class HouseCommunication(BaseCommunication):
    congress: int | None = None
    updateDate: date | str | None = None
    abstract: str | None = None
    congressionalRecordDate: date | str | None = None
    sessionNumber: int | None = None
    isRulemaking: bool | None = None
    committees: "list[Committee] | None" = None
    matchingRequirements: list[Dict[str, Any]] | None = None
    reportNature: str | None = None
    submittingAgency: str | None = None
    submittingOfficial: str | None = None
    legalAuthority: str | None = None
    houseDocument: Dict[Any, list[Any]] | None = None


class HouseCommunications(Model):
    """
    === HouseCommunications Model ===
    Represents a container for a list of HouseCommunication objects.
    """
    houseCommunications: list[HouseCommunication] | None = Field(None, alias="houseCommunications")


class SenateCommunication(BaseCommunication):
    congress: int | None = None
    abstract: str | None = None
    congressionalRecordDate: date | str | None = None
    committees: "list[Committee] | None" = None


class SenateCommunications(Model):
    """
    === SenateCommunications Model ===
    Represents a container for a list of SenateCommunication objects.
    """
    senateCommunications: list[SenateCommunication | None] | None = Field(None, alias="senateCommunications")


# Model rebuild statements - delay rebuild for classes with forward references
# CommunicationType.model_rebuild()  # Handled by centralized rebuild system
# BaseCommunication.model_rebuild()  # Handled by centralized rebuild system
# HouseCommunications.model_rebuild()  # Handled by centralized rebuild system
# SenateCommunications.model_rebuild()  # Handled by centralized rebuild system
