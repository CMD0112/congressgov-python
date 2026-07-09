from __future__ import annotations
from datetime import date
from pydantic import Field
from ..base.model import Model
from ..base.enums import Chamber, CommunicationCode
from ..base.types import URL, CountRef


class CommunicationType(Model):
    code: str | None = None
    name: CommunicationCode | None = None


class MatchingCommunication(Model):
    chamber: Chamber | None = None
    number: int | str | None = None
    communicationType: CommunicationType | None = None
    congress: int | None = None
    # URL class now handles string conversion automatically via __get_pydantic_core_schema__
    url: URL | None = None


# MatchingCommunication.model_rebuild()  # Handled by centralized rebuild system


class MatchingCommunications(Model):
    matchingCommunications: list[MatchingCommunication] | None = None


# MatchingCommunications.model_rebuild()  # Handled by centralized rebuild system


class HouseRequirement(Model):
    number: int | str | None = None
    updateDate: date | str | None = None
    parentAgency: str | None = None
    frequency: str | None = None
    nature: str | None = None
    legalAuthority: str | None = None
    activeRecord: bool | None = None
    submittingAgency: str | None = None
    submittingOfficial: str | None = None
    matchingCommunications: list[MatchingCommunication] | CountRef | None = None


# HouseRequirement.model_rebuild()  # Handled by centralized rebuild system
    

class HouseRequirements(Model):
    houseRequirements: list[HouseRequirement] | None = Field(None, alias="houseRequirements")


# HouseRequirements.model_rebuild()  # Handled by centralized rebuild system
