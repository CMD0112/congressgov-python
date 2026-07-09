from __future__ import annotations
from datetime import date
from pydantic import Field
from ..base.model import Model
# from ..entities.committee import Committees  # Temporarily disabled due to circular import
from ..actions.action import Actions, LatestAction


class Nominee(Model):      # ?: Should this use the base Nominees class?
    ordinal: int | None = None
    lastName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    state: str | None = None     # ?: Enum?
    effectiveDate: date | str | None = None
    predecessorName: str | None = None
    corpsCode: str | int | None = None    # ?: Enum? Would need to find values.


# Nominee.model_rebuild()  # Handled by centralized rebuild system


class Nominees(Model):
    nominees: list[Nominee] | None = Field(None, alias="nominees")


# Nominees.model_rebuild()  # Handled by centralized rebuild system


class Nomination(Model):
    congress: int | None = None
    number: str | int | None = None  # Allow both string and int for flexibility
    partNumber: str | None = None    # Allow string for flexibility
    citation: str | None = None
    isPrivileged: bool | None = None
    isList: bool | None = None
    receivedDate: date | str | None = None
    description: str | None = None
    executiveCalenderNumber: int | None = None
    authorityDate: date | str | None = None
    nominees: list[Nominee] | None = None
    committees: "Committee | None" = None
    latestAction: LatestAction | None = None
    nominationType: dict[str, bool] | None = None
    actions: Actions | None = None
    hearings: "list[CommitteeMeeting] | None" = None
    updateDate: date | str | None = None


# Nomination.model_rebuild()  # Handled by centralized rebuild system


class Nominations(Model):
    nominations: list[Nomination] | None = Field(None, alias="nominations")


# Nominations.model_rebuild()  # Handled by centralized rebuild system


