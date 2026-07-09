from __future__ import annotations
from typing import List
from datetime import date, time
from pydantic import Field
from ..base.model import Model
from ..base.references import CommitteeRef
from .vote import RecordedVote, RecordedVotes
from .calendar import CalendarNumber

class Action(Model):
    """A single action taken on a bill, amendment, or nomination (e.g. introduced,
    referred to committee, passed). Uses `CommitteeRef` rather than the full
    `Committee` model to avoid a circular import.
    """
    actionDate: date | str | None = None
    actionTime: time | None = None
    text: str | None = None
    type: str | None = None  # ActionType enum
    actionCode: str | None = None  # ActionCode enum
    sourceSystem: dict | None = None
    committees: list[CommitteeRef] | None = None
    recordedVotes: list[RecordedVote] | None = None
    calendarNumber: list[CalendarNumber] | None = None

    @property
    def action_date(self) -> date | str | None:
        return self.actionDate

    @action_date.setter
    def action_date(self, value: date | str | None) -> None:
        self.actionDate = value

    @property
    def action_time(self) -> time | None:
        return self.actionTime

    @action_time.setter
    def action_time(self, value: time | None) -> None:
        self.actionTime = value

    @property
    def action_type(self) -> str | None:
        return self.type

    @action_type.setter
    def action_type(self, value: str | None) -> None:
        self.type = value

    @property
    def action_code(self) -> str | None:
        return self.actionCode

    @action_code.setter
    def action_code(self, value: str | None) -> None:
        self.actionCode = value

    @property
    def source_system(self) -> dict | None:
        return self.sourceSystem

    @source_system.setter
    def source_system(self, value: dict | None) -> None:
        self.sourceSystem = value

    @property
    def recorded_votes(self) -> "RecordedVotes | None":
        return self.recordedVotes

    @recorded_votes.setter
    def recorded_votes(self, value: "RecordedVotes | None") -> None:
        self.recordedVotes = value

    @property
    def calendar_number(self) -> "CalendarNumber | None":
        return self.calendarNumber

    @calendar_number.setter
    def calendar_number(self, value: "CalendarNumber | None") -> None:
        self.calendarNumber = value


class Actions(Model):
    """A container for a list of `Action` objects, matching the API's
    `actions`/`pagination`/`request` response shape.
    """
    actions: List[Action] | None = Field(None, alias="actions")

 
# Actions.model_rebuild()  # Commented out due to forward reference issues


class ActionsRef(Model):
    count: int | None = None
    url: str | None = None


# ActionsRef.model_rebuild()  # Handled by centralized rebuild system


class LatestAction(Model):
    actionDate: date | str | None = None
    text: str | None = None
    actionTime: time | None = None

    @property
    def action_date(self) -> date | str | None:
        return self.actionDate

    @action_date.setter
    def action_date(self, value: date | str | None) -> None:
        self.actionDate = value

    @property
    def action_time(self) -> time | None:
        return self.actionTime

    @action_time.setter
    def action_time(self, value: time | None) -> None:
        self.actionTime = value


# LatestAction.model_rebuild()  # Handled by centralized rebuild system
