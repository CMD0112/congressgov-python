from __future__ import annotations
from typing import Literal
from datetime import datetime
from pydantic import Field
from ..base.model import Model
from ..base.enums import LegislationType, LawType


class CRSReportRef(Model):
    status: Literal["Active", "Archived"] | None = None
    id: str | None = None
    publishedDate: datetime | str | None = None
    version: int | None = None
    contentType: str | None = None
    updateDate: datetime | str | None = None
    title: str | None = None
    url: str | None = None
    
    @property
    def published_date(self) -> datetime | str | None:
        return self.publishedDate
    
    @published_date.setter
    def published_date(self, value: datetime | str | None) -> None:
        self.publishedDate = value
    
    @property
    def content_type(self) -> str | None:
        return self.contentType
    
    @content_type.setter
    def content_type(self, value: str | None) -> None:
        self.contentType = value
    
    @property
    def update_date(self) -> datetime | str | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: datetime | str | None) -> None:
        self.updateDate = value


# CRSReportRef.model_rebuild()  # Handled by centralized rebuild system


class CRSFormat(Model):
    """
    === CRSFormat Model ===
    Represents a format for CRS reports.
    """
    url: str | None = None
    type: str | None = None


# CRSFormat.model_rebuild()  # Handled by centralized rebuild system


class CRSFormats(Model):
    """
    === CRSFormats Model ===
    Represents available formats for CRS reports.
    """
    formats: list[CRSFormat] | None = None


# CRSFormats.model_rebuild()  # Handled by centralized rebuild system


class CRSRelatedMaterial(Model):
    """
    === CRSRelatedMaterial Model ===
    Represents related material for CRS reports.
    """
    title: str | None = None
    url: str | None = None


# CRSRelatedMaterial.model_rebuild()  # Handled by centralized rebuild system


class CRSRelatedMaterials(Model):
    """
    === CRSRelatedMaterials Model ===
    Represents a container for related materials.
    """
    relatedMaterials: list[CRSRelatedMaterial] | None = Field(None, alias="relatedMaterials")


# CRSRelatedMaterials.model_rebuild()  # Handled by centralized rebuild system


class CRSTopic(Model):
    """
    === CRSTopic Model ===
    Represents a topic for CRS reports.
    """
    name: str | None = None
    id: str | None = None


# CRSTopic.model_rebuild()  # Handled by centralized rebuild system


class CRSTopics(Model):
    """
    === CRSTopics Model ===
    Represents a container for CRS topics.
    """
    topics: list[CRSTopic] | None = Field(None, alias="topics")


# CRSTopics.model_rebuild()  # Handled by centralized rebuild system


class CRSAuthor(Model):
    """
    === CRSAuthor Model ===
    Represents an author of CRS reports.
    """
    name: str | None = None
    id: str | None = None


# CRSAuthor.model_rebuild()  # Handled by centralized rebuild system


class CRSAuthors(Model):
    """
    === CRSAuthors Model ===
    Represents a container for CRS authors.
    """
    authors: list[CRSAuthor] | None = Field(None, alias="authors")


# CRSAuthors.model_rebuild()  # Handled by centralized rebuild system


class CRSReport(Model):
    """
    === CRSReport Model ===
    Represents a Congressional Research Service report.
    """
    status: Literal["Active", "Archived"] | None = None
    id: str | None = None
    publishedDate: datetime | str | None = None
    version: int | None = None
    contentType: str | None = None
    updateDate: datetime | str | None = None
    title: str | None = None
    url: str | None = None
    summary: str | None = None
    formats: list[CRSFormat] | None = None
    relatedMaterials: list[CRSRelatedMaterial] | None = None
    topics: list[CRSTopic] | None = None
    authors: list[CRSAuthor] | None = None
    LegislationTypes: list[LegislationType] | None = None
    lawTypes: list[LawType] | None = None
    
    @property
    def published_date(self) -> datetime | str | None:
        return self.publishedDate
    
    @published_date.setter
    def published_date(self, value: datetime | str | None) -> None:
        self.publishedDate = value
    
    @property
    def content_type(self) -> str | None:
        return self.contentType
    
    @content_type.setter
    def content_type(self, value: str | None) -> None:
        self.contentType = value
    
    @property
    def update_date(self) -> datetime | str | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: datetime | str | None) -> None:
        self.updateDate = value


# CRSReport.model_rebuild()  # Handled by centralized rebuild system


class CRSReports(Model):
    """
    === CRSReports Model ===
    Represents a container for CRS reports.
    """
    crsReports: list[CRSReport] | None = Field(None, alias="CRSReports")


# CRSReports.model_rebuild()  # Handled by centralized rebuild system


# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
