from __future__ import annotations
from typing import List
from datetime import date
from pydantic import Field
from ..base.model import Model
from ..base.enums import Chamber


class RecordedVote(Model):
    rollNumber: int | None = None
    url: str | None = None
    chamber: Chamber | None = None
    congress: int | None = None
    date: str | date | None = None
    sessionNumber: int | None = None

    @property
    def roll_number(self) -> int | None:
        return self.rollNumber

    @roll_number.setter
    def roll_number(self, value: int | None) -> None:
        self.rollNumber = value

    @property
    def session_number(self) -> int | None:
        return self.sessionNumber

    @session_number.setter
    def session_number(self, value: int | None) -> None:
        self.sessionNumber = value


# RecordedVote.model_rebuild()  # Handled by centralized rebuild system


class RecordedVotes(Model):
    """
    === RecordedVotes Model ===
    Represents a container for a list of RecordedVote objects.
    """
    votes: List["RecordedVote"] | None = Field(None, alias="votes")


# RecordedVotes.model_rebuild()  # Handled by centralized rebuild system
