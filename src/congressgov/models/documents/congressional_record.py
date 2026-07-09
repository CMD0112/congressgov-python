from __future__ import annotations
from ..base.types import URL, CountRef
from ..base.model import Model
from datetime import date
from pydantic import Field


class PDFLink(Model):
    part: str | None = Field(None, alias="Part")
    url: str | None = Field(None, alias="Url")


# PDFLink.model_rebuild()  # Handled by centralized rebuild system


class LinkSection(Model):
    label: str | None = Field(None, alias="Label")
    ordinal: int | None = Field(None, alias="Ordinal")
    pdf: list[PDFLink] | None = Field(None, alias="PDF")


# LinkSection.model_rebuild()  # Handled by centralized rebuild system


class IssueLinks(Model):
    digest: LinkSection | None = Field(None, alias="Digest")
    full_record: LinkSection | None = Field(None, alias="FullRecord")
    house: LinkSection | None = Field(None, alias="House")
    remarks: LinkSection | None = Field(None, alias="Remarks")
    senate: LinkSection | None = Field(None, alias="Senate")


# IssueLinks.model_rebuild()  # Handled by centralized rebuild system


class DailyCongressionalRecordIssue(Model):
    congress: str | None = Field(None, alias="Congress")
    id: int | None = Field(None, alias="Id")
    issue: str | None = Field(None, alias="Issue")
    links: IssueLinks | None = Field(None, alias="Links")
    publish_date: date | None = Field(None, alias="PublishDate")
    session: str | None = Field(None, alias="Session")
    volume: str | None = Field(None, alias="Volume")


# DailyCongressionalRecordIssue.model_rebuild()  # Handled by centralized rebuild system


class Results(Model):
    index_start: int | None = Field(None, alias="IndexStart")
    issues: list[DailyCongressionalRecordIssue] | None = Field(None, alias="Issues")
    set_size: int | None = Field(None, alias="SetSize")
    total_count: int | None = Field(None, alias="TotalCount")


# Results.model_rebuild()  # Handled by centralized rebuild system


class Status(Model):
    code: str | None = Field(None, alias="Code")
    message: str | None = Field(None, alias="Message")


# Status.model_rebuild()  # Handled by centralized rebuild system


class DailyCongressionalRecord(Model):
    """
    === DailyCongressionalRecord Model ===
    Represents the complete response structure for daily congressional record list API.
    """
    results: Results | None = Field(None, alias="Results")
    status: Status | None = Field(None, alias="Status")


# DailyCongressionalRecord.model_rebuild()  # Handled by centralized rebuild system


class EntireIssue(Model):
    entire_issue: list[dict] | None = Field(None, alias="entireIssue")


# EntireIssue.model_rebuild()  # Handled by centralized rebuild system


class SectionText(Model):
    part: str | None = None
    type: str | None = None
    url: URL | None = None


# SectionText.model_rebuild()  # Handled by centralized rebuild system


class Section(Model):
    name: str | None = None
    start_page: int | None = Field(None, alias="startPage")
    end_page: int | None = Field(None, alias="endPage")
    text: list[SectionText] | None = None


# Section.model_rebuild()  # Handled by centralized rebuild system


class FullIssue(Model):
    entire_issue: list[dict] | None = Field(None, alias="entireIssue")
    sections: list[Section] | None = None
    articles: CountRef | None = None


# FullIssue.model_rebuild()  # Handled by centralized rebuild system


class Issue(Model):
    issue_number: int | None = Field(None, alias="issueNumber")
    volume_number: int | None = Field(None, alias="volumeNumber")
    issue_date: date | None = Field(None, alias="issueDate")
    congress: int | None = None
    session_number: int | None = Field(None, alias="sessionNumber")
    url: URL | None = None
    update_date: date | None = Field(None, alias="updateDate")
    full_issue: EntireIssue | None = Field(None, alias="fullIssue")


# Issue.model_rebuild()  # Handled by centralized rebuild system


# ? Articles?

class DailyCongressionalRecordArticles(Model):
    """Articles for a daily Congressional Record issue."""

    articles: list[dict] | None = None


class CongressionalRecordArticle(Model):
    """Single article entry within a daily Congressional Record issue."""

    name: str | None = None
    section: str | None = None
    start_page: int | None = Field(None, alias="startPage")
    end_page: int | None = Field(None, alias="endPage")
    text: list[SectionText] | None = None


# Model alias for universal search / registry (DailyCongressionalRecord APIs)
CongressionalRecord = DailyCongressionalRecord

# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
