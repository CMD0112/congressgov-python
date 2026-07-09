from __future__ import annotations
from typing import List
from datetime import date, time
from pydantic import Field
from ..base.model import Model
from ..base.references import CommitteeRef
from .vote import RecordedVote, RecordedVotes
from .calendar import CalendarNumber


# Action class definition

class Action(Model):
    """
    Action model with properly typed references.
    
    NOTE: Uses CommitteeRef instead of full Committee model to avoid circular imports.
    This maintains full type safety and IntelliSense support.
    """
    actionDate: date | str | None = None
    actionTime: time | None = None
    text: str | None = None
    type: str | None = None  # ActionType enum
    actionCode: str | None = None  # ActionCode enum
    sourceSystem: dict | None = None
    committees: list[CommitteeRef] | None = None  # ✅ Now fully typed with CommitteeRef
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
    """
    === Actions Model ===
    Represents a container for a list of Action objects, as well as pagination and request metadata.
    This structure matches the JSON payload returned by the API, which includes 'actions', 'pagination', and 'request' keys.
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
