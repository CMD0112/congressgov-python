from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING, Self

from pydantic import Field, model_validator

from ..base.enums import Chamber, SessionType
from ..base.model import Model

# NOTE: Only using Congress class and allowing for partial initialization

_CONGRESS_URL_RE = re.compile(r"/congress/(\d+)(?:/|\?|$)", re.IGNORECASE)
_CONGRESS_NAME_RE = re.compile(r"^(\d+)(?:st|nd|rd|th)?\s+Congress", re.IGNORECASE)


def congress_number_from_url(url: str | None) -> int | None:
    """Extract a session number from a Congress.gov API URL."""
    if not url:
        return None
    match = _CONGRESS_URL_RE.search(url)
    if match is None:
        return None
    return int(match.group(1))


def congress_number_from_name(name: str | None) -> int | None:
    """Extract a session number from labels like ``119th Congress``."""
    if not name:
        return None
    match = _CONGRESS_NAME_RE.match(name.strip())
    if match is None:
        return None
    return int(match.group(1))


def infer_congress_number(
    *,
    number: int | None = None,
    congress: int | None = None,
    name: str | None = None,
    url: str | None = None,
) -> int | None:
    """Resolve a Congress session number from known model fields."""
    if number is not None:
        return number
    if congress is not None:
        return congress
    from_url = congress_number_from_url(url)
    if from_url is not None:
        return from_url
    return congress_number_from_name(name)


class CongressSession(Model):
    chamber: Chamber | None = None
    type: SessionType | None = None
    startDate: date | str | None = None    # TODO: Handle datetime across all classes
    endDate: date | str | None = None    # TODO: Handle datetime across all classes
    number: int | None = None

    @property
    def start_date(self) -> date | str | None:
        return self.startDate
    
    @start_date.setter
    def start_date(self, value: date | str | None) -> None:
        self.startDate = value
    
    @property
    def end_date(self) -> date | str | None:
        return self.endDate
    
    @end_date.setter
    def end_date(self, value: date | str | None) -> None:
        self.endDate = value


# CongressSession.model_rebuild()  # Handled by centralized rebuild system


class CongressSessions(Model):
    """
    === CongressSessions Model ===
    Represents a container for a list of CongressSession objects.
    """
    sessions: list[CongressSession] | None = Field(None, alias="sessions", validation_alias="sessions")


# CongressSessions.model_rebuild()  # Handled by centralized rebuild system


class Congress(Model):
    sessions: list[CongressSession] | None = None
    name: str | None = None
    startYear: int | None = None
    endYear: int | None = None
    updateDate: date | str | None = None    # TODO: Handle datetime across all classes
    number: int | None = None
    url: str | None = None

    @property
    def start_year(self) -> int | None:
        return self.startYear
    
    @start_year.setter
    def start_year(self, value: int | str | None) -> None:
        self.startYear = value
    
    @property
    def end_year(self) -> int | None:
        return self.endYear
    
    @end_year.setter
    def end_year(self, value: int | None) -> None:
        self.endYear = value
    
    @property
    def update_date(self) -> date | str | None:
        return self.updateDate
    
    @update_date.setter
    def update_date(self, value: date | str | None) -> None:
        self.updateDate = value

    @property
    def congress(self) -> int | None:
        """Congress session number (alias for ``number``, matches API path param name)."""
        return self.number

    @congress.setter
    def congress(self, value: int | None) -> None:
        self.number = value

    @model_validator(mode="after")
    def _infer_number_from_url_or_name(self) -> Self:
        """List/detail payloads often omit ``number`` but include ``url`` or ``name``."""
        if self.number is None:
            inferred = infer_congress_number(
                name=self.name,
                url=self.url,
            )
            if inferred is not None:
                self.number = inferred
        return self


# Congress.model_rebuild()  # Handled by centralized rebuild system


class Congresses(Model):
    """
    === Congresses Model ===
    Represents a container for a list of Congress objects.
    """
    congresses: list[Congress] | None = Field(None, alias="congresses")


# Congresses.model_rebuild()  # Handled by centralized rebuild system


if TYPE_CHECKING:
    from congressgov.services.protocols.congress import CongressProtocol
    from congressgov.services.protocols.async_congress import AsyncCongressProtocol

    class Congress(Model, CongressProtocol, AsyncCongressProtocol):
        """Congress model with sync and async extension method type hints."""

        pass


# === Ensure all Pydantic models with forward references are rebuilt for type resolution ===
# All model_rebuild() calls have been moved to right after each model definition
