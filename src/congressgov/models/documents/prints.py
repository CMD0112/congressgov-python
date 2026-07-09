from __future__ import annotations
from pydantic import Field
from ..base.types import CountRef
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
    """
    === CommitteePrintTexts Model ===
    Represents a container for a list of CommitteePrintText objects from text detail API.
    """
    texts: list[CommitteePrintText] = Field(default_factory=list, alias="text")


# CommitteePrintTexts.model_rebuild()  # Handled by centralized rebuild system


class CommitteePrint(Model):
    jacketNumber: str | int | None = None
    citation: str | None = None
    congress: int | None = None
    number: int | None = None
    title: str | None = None
    chamber: Chamber | None = None
    committees: "list[Committee] | None" = None
    associatedBills: list[Bill] | None = None     # TODO: Re-enable when BillRef is properly imported
    text: CountRef | None = None       # TODO: Need to associated this with CommitteePrintTexts
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict) and 'committeePrint' in obj:
            obj = obj['committeePrint'][0]
        return super().model_validate(obj, **kwargs)


# CommitteePrint.model_rebuild()  # Handled by centralized rebuild system


class CommitteePrints(Model):
    """
    === CommitteePrints Model ===
    Represents a container for a list of CommitteePrint objects from list API.
    """
    committeePrints: list[CommitteePrint] = Field(default_factory=list, alias="committeePrints")


# CommitteePrints.model_rebuild()  # Handled by centralized rebuild system
    

# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
