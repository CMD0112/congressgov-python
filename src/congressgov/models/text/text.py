from __future__ import annotations
from typing import List
from datetime import datetime
from pydantic import Field
from ..base.model import Model
from ..base.enums import TextVersionType


class TextVersionFormat(Model):
    url: str | None = None
    type: str | None = None  # Accept both enum and string  # TODO: Need to fix this


# TextVersionFormat.model_rebuild()  # Handled by centralized rebuild system


class TextVersionFormats(Model):
    formats: List[TextVersionFormat] | None = None


# TextVersionFormats.model_rebuild()  # Handled by centralized rebuild system


class TextVersionItem(Model):
    type: str | TextVersionType | None = None  # Accept both enum and string
    date: datetime | None = None
    formats: list[TextVersionFormat] | None = None  # Direct list of format objects


# TextVersionItem.model_rebuild()  # Handled by centralized rebuild system


class TextVersions(Model):
    textVersions: List[TextVersionItem] | None = Field(None, alias="textVersions")


# TextVersions.model_rebuild()  # Handled by centralized rebuild system
