from __future__ import annotations
from pydantic import Field
from ..base.model import Model
from typing import Literal
from datetime import date
from ..base.enums import Chamber, ReportType
from ..entities.treaty import Treaty
from ..entities.bill import Bill

class CommitteeReportRef(Model):
    citation: str | None = None
    url: str | None = None
    updateDate: date | None = None    # TODO: Handle datetime across all classes
    congress: int | None = None
    chamber: Chamber | None = None
    type: ReportType | None = None
    number: int | None = None
    part: int | None = None


class CommitteeReportText(Model):
    url: str | None = None
    type: Literal["Formatted Text", "PDF"] | None = None
    isErrata: bool | None = None


class CommitteeReportTexts(Model):
    text: list[CommitteeReportText] | None = None


class CommitteeReport(Model):
    citation: str | None = None
    url: str | None = None
    updateDate: date | None = None    # TODO: Handle datetime across all classes
    congress: int | None = None
    chamber: Chamber | None = None
    type: ReportType | None = None
    number: int | None = None
    part: int | None = None
    title: str | None = None
    text: list[CommitteeReportText] | None = None
    committee: "CommitteeShortRef | None" = None
    bills: list[Bill] | None = None
    treaties: list[Treaty] | None = None


class CommitteeReports(Model):
    """
    === CommitteeReports Model ===
    Represents a container for a list of CommitteeReport objects.
    """
    committeeReports: list[CommitteeReport] | None = Field(None, alias="committeeReports")


# CommitteeReportRef.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReportText.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReportTexts.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReport.model_rebuild()  # Handled by centralized rebuild system
# CommitteeReports.model_rebuild()  # Handled by centralized rebuild system
