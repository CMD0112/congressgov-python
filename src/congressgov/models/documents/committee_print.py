from __future__ import annotations
from pydantic import Field
from ..base.model import Model
from typing import Literal
from datetime import date
from ..base.enums import Chamber
from ..entities.bill import Bill

class CommitteePrintRef(Model):
    jacketNumber: str | None = None
    url: str | None = None
    updateDate: date | None = None
    congress: int | None = None
    chamber: Chamber | None = None


# CommitteePrintRef.model_rebuild()  # Handled by centralized rebuild system


class CommitteePrintText(Model):
    url: str | None = None
    type: Literal["PDF", "Formatted Text", "Formatted XML", "Generated HTML"] | None = None


# CommitteePrintText.model_rebuild()  # Handled by centralized rebuild system


class CommitteePrintTexts(Model):
    text: list[CommitteePrintText] | None = None


# CommitteePrintTexts.model_rebuild()  # Handled by centralized rebuild system


class CommitteePrint(Model):
    jacketNumber: str | None = None
    url: str | None = None
    updateDate: date | None = None
    congress: int | None = None
    chamber: Chamber | None = None
    title: str | None = None
    text: list[CommitteePrintText] | None = None
    committee: "Committee | None" = None
    bills: list[Bill] | None = None


# CommitteePrint.model_rebuild()  # Moved to after Committee is defined


class CommitteePrints(Model):
    """
    === CommitteePrints Model ===
    Represents a container for a list of CommitteePrint objects.
    """
    committeePrints: list[CommitteePrint] | None = Field(None, alias="committeePrints")


# CommitteePrints.model_rebuild()  # Moved to after Committee is defined


# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
