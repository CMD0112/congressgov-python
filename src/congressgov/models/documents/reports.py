from __future__ import annotations
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import Field
from ..base.model import Model
from ..base.enums import ReportType, Chamber, LegislationType, LawType
from ..base.types import CountRef

from ..entities.treaty import Treaty
from ..entities.bill import Bill


class Report(Model):
    citation: Optional[str] = None
    url: Optional[str] = None
    updateDate: Optional[datetime | str] = None    # FIXED: API returns datetime with time components
    congress: Optional[int] = None
    chamber: Optional[Chamber] = None
    type: Optional[ReportType] = None
    number: Optional[int] = None
    part: Optional[int] = None


# Report.model_rebuild()  # Handled by centralized rebuild system


class Reports(Model):
    reports: Optional[List["Report"]] = Field(None, alias="reports")


# Reports.model_rebuild()  # Handled by centralized rebuild system


class CommitteeReportRef(Model):
    citation: str | None = None
    url: str | None = None
    updateDate: datetime | str | None = None    # FIXED: API returns datetime with time components
    congress: int | None = None
    chamber: Chamber | None = None
    type: ReportType | None = None
    number: int | None = None
    part: int | None = None


# CommitteeReportRef.model_rebuild()  # Handled by centralized rebuild system


class CommitteeReportText(Model):
    url: str | None = None
    type: Literal["Formatted Text", "PDF"] | None = None
    isErrata: bool | None = None


# CommitteeReportText.model_rebuild()  # Handled by centralized rebuild system


class CommitteeReportTexts(Model):
    """
    === CommitteeReportTexts Model ===
    Represents a container for a list of CommitteeReportText objects from text detail API.
    Expects input like:
    {
        'pagination': {...},
        'request': {...},
        'text': [
            {'formats': [ ... ]},
            ...
        ]
    }
    """
    texts: list[CommitteeReportText] = Field(default_factory=list, alias="text")

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # If obj is a dict with a "text" key, and "text" is a list of dicts with "formats"
        if isinstance(obj, dict) and "text" in obj:
            # Use a list comprehension to flatten all formats from all text entries
            formats = [
                {
                    **fmt,
                    "isErrata": (
                        fmt["isErrata"].upper() == "Y"
                        if isinstance(fmt.get("isErrata"), str)
                        else fmt.get("isErrata")
                    ),
                }
                if "isErrata" in fmt else fmt
                for text_entry in obj["text"]
                for fmt in text_entry.get("formats", [])
            ]
            obj = {"texts": formats}
        return super().model_validate(obj, **kwargs)


# CommitteeReportTexts.model_rebuild()  # Handled by centralized rebuild system


class CommitteeReport(Model):
    committees: "list[Committee] | None" = None
    congress: int | None = None
    chamber: Chamber | None = None
    sessionNumber: int | None = None
    citation: str | None = None
    number: int | None = None
    part: int | None = None
    type: ReportType | None = None
    updateDate: datetime | str | None = None    # FIXED: API returns datetime with time components
    isConferenceReport: bool | None = None
    title: str | None = None
    issuedDate: datetime | str | None = None    # FIXED: API returns datetime with time components
    reportType: Literal["H.Rept", "S.Rept", "Ex.Rept", "H.Rept.", "S.Rept.", "Ex.Rept."] | None = None     # TODO: Reconcile this with type
    text: CountRef | None = None
    associatedTreaties: list[Treaty] | None = None     # HACK: Use of Any here defeats the purpose of type hinting
    associatedBill: list[Bill] | None = None     # HACK: Use of Any here defeats the purpose of type hinting

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # If obj is a dict with a "committeeReports" key, extract the first item
        if isinstance(obj, dict) and "committeeReports" in obj and isinstance(obj["committeeReports"], list):
            if obj["committeeReports"]:
                obj = obj["committeeReports"][0]
            else:
                obj = {}
        return super().model_validate(obj, **kwargs)


# CommitteeReport.model_rebuild()  # Handled by centralized rebuild system


class CommitteeReports(Model):
    reports: list[CommitteeReport] | None = Field(None, alias="reports")


# CommitteeReports.model_rebuild()  # Handled by centralized rebuild system


# CRS Reports
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


class CRSFormats(Model):
    format: list[str] | None = None
    URL: str | None = None
    
    @property
    def url(self) -> str | None:
        return self.URL
    
    @url.setter
    def url(self, value: str | None) -> None:
        self.URL = value


# CRSFormats.model_rebuild()  # Handled by centralized rebuild system


class CRSRelatedMaterial(Model):
    title: str | None = None
    congress: int | None = None
    number: int | str | None = None  # Allow both int and string for cases like '93-344'
    type: LegislationType | LawType | str | None = None  # Allow string for cases like 'PUB'   # TODO: Take a closer look at this
    url: str | None = None


# CRSRelatedMaterial.model_rebuild()  # Handled by centralized rebuild system


class CRSRelatedMaterials(Model):
    """
    === CRSRelatedMaterials Model ===
    Represents a container for a list of CRSRelatedMaterial objects.
    """
    relatedMaterials: list[CRSRelatedMaterial] | None = Field(None, alias="relatedMaterials")


# CRSRelatedMaterials.model_rebuild()  # Handled by centralized rebuild system


class CRSTopic(Model):
    topic: str | None = None


# CRSTopic.model_rebuild()  # Handled by centralized rebuild system


class CRSTopics(Model):
    """
    === CRSTopics Model ===
    Represents a container for a list of CRSTopic objects.
    """
    topics: list[CRSTopic] | None = Field(None, alias="topics")


# CRSTopics.model_rebuild()  # Handled by centralized rebuild system


class CRSAuthor(Model):
    author: str | None = None


# CRSAuthor.model_rebuild()  # Handled by centralized rebuild system


class CRSAuthors(Model):
    """
    === CRSAuthors Model ===
    Represents a container for a list of CRSAuthor objects.
    """
    authors: list[CRSAuthor] | None = Field(None, alias="authors")


# CRSAuthors.model_rebuild()  # Handled by centralized rebuild system


class CRSReport(Model):
    status: Literal["Active", "Archived"] | None = None
    id: str | None = None
    publishedDate: datetime | str | None = None
    version: int | None = None
    contentType: str | None = None
    updateDate: datetime | str | None = None
    title: str | None = None
    url: str | None = None
    authors: CRSAuthors | None = None
    relatedMaterials: CRSRelatedMaterials | None = None
    topics: CRSTopics | None = None
    summary: str | None = None


# CRSReport.model_rebuild()  # Handled by centralized rebuild system


class CRSReports(Model):
    """
    === CRSReports Model ===
    Represents a container for a list of CRSReport objects.
    """
    crsReports: list[CRSReport] | None = Field(None, alias="crsReports")


# CRSReports.model_rebuild()  # Handled by centralized rebuild system
