from __future__ import annotations
from datetime import datetime
from pydantic import Field
from ..base.model import Model
from ..base.types import URL

# ISSUE: These definitions need to be reworked


class BoundCongressionalRecord(Model):
    date: datetime | str | None = None
    volumeNumber: int | None = None
    congress: int | None = None
    sessionNumber: int | None = None
    updateDate: datetime | str | None = None
    url: str | URL | None = None
    
    
    @property
    def session_number(self) -> int | None:
        return self.sessionNumber
    
    @session_number.setter
    def session_number(self, value: int | None) -> None:
        self.sessionNumber = value
        
    @property
    def update_date(self) -> datetime | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: datetime | None) -> None:
        self.updateDate = value


# BoundCongressionalRecord.model_rebuild()  # Handled by centralized rebuild system


class BoundCongressionalRecords(Model):
    boundCongressionalRecord: list[BoundCongressionalRecord] | None = Field(None, alias="boundCongressionalRecord")


# BoundCongressionalRecords.model_rebuild()  # Handled by centralized rebuild system


class DailyDigestText(Model):
    type: str | None = None
    url: str | None = None


# DailyDigestText.model_rebuild()  # Handled by centralized rebuild system


class DailyDigest(Model):
    startPage: int | None = None
    endPage: int | None = None
    text: DailyDigestText | None = None
    
    @property
    def start_page(self) -> int | None:
        return self.startPage
    
    @start_page.setter
    def start_page(self, value: int | None) -> None:
        self.startPage = value
        
    @property
    def end_page(self) -> int | None:
        return self.endPage
    
    @end_page.setter
    def end_page(self, value: int | None) -> None:
        self.endPage = value


# DailyDigest.model_rebuild()  # Handled by centralized rebuild system


class Section(Model):
    name: str | None = None
    startPage: int | None = None
    endPage: int | None = None
    
    @property
    def start_page(self) -> int | None:
        return self.startPage
    
    @start_page.setter
    def start_page(self, value: int | None) -> None:
        self.startPage = value
        
    @property
    def end_page(self) -> int | None:
        return self.endPage
    
    @end_page.setter
    def end_page(self, value: int | None) -> None:
        self.endPage = value


# Section.model_rebuild()  # Handled by centralized rebuild system


class Sections(Model):
    """
    === Sections Model ===
    Represents a container for a list of Section objects.
    """
    sections: list[Section] | None = Field(None, alias="sections")


# Sections.model_rebuild()  # Handled by centralized rebuild system

    # @classmethod
    # def _get_field_mappings(cls):
    #     """
    #     Define field parsing rules for Sections class.
    #     This replaces the custom model_validate method with a clean, declarative approach.
    #     """
    #     return {
    #         "sections": (Section, "sections", None),
    #     }


# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
