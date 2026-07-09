from __future__ import annotations
from typing import Dict, Any
from datetime import date
from pydantic import Field
from ..base.model import Model
from ..committees import Committees
from ..base.enums import Chamber


class Hearing(Model):
    jacketNumber: str | int | None = None
    libraryOfCongressIdentifier: str | None = None
    number: int | None = None
    part: int | None = None
    updateDate: date | str | None = None
    congress: int | None = None
    title: str | None = None
    citation: str | None = None
    chamber: Chamber | None = None
    committees: "Committees | None" = None
    dates: list[Dict[str, date | str]] | None = None
    formats: list[Dict[str, Any]] | None = None
    associatedMeeting: Dict[Any, Any] | None = Field(None, alias="associatedMeeting")


# Hearing.model_rebuild()  # Handled by centralized rebuild system


class Hearings(Model):
    hearings: list[Hearing] | None = Field(None, alias="hearings")


# Hearings.model_rebuild()  # Handled by centralized rebuild system


