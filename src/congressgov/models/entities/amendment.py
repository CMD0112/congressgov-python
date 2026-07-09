from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, AliasChoices
from ..base.model import Model

# Import protocols for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    from congressgov.services.protocols.amendment import AmendmentProtocol, AmendmentsProtocol
    from congressgov.services.protocols.async_amendment import AsyncAmendmentProtocol
from ..base.enums import AmendmentType, Chamber
from ..base.types import CountRef, URL
from ..base.references import BillRef, TreatyRef, AmendmentRef  # noqa: F401 — re-export
from ..actions.action import Action, LatestAction
from .sponsor import Sponsor, Cosponsor, OnBehalfOfSponsor
from .bill import TextVersionItem
from .treaty import Treaty


class Amendment(Model):
    # === [CORE FIELDS] Basic amendment information ===
    number: str | None = None
    description: str | None = None
    purpose: str | None = None
    congress: int | None = None
    type: AmendmentType | None = None

    # === [ACTION & TIMING FIELDS] ===
    latestAction: "LatestAction | None" = None
    proposedDate: datetime | None = None
    submittedDate: datetime | None = None

    # === [CHAMBER & SPONSORSHIP] ===
    chamber: Chamber | None = None

    # === [COMPOSITION APPROACH] Use Member class instead of duplicating fields ===
    sponsors: list[Sponsor] | None = None  # ✅ Direct import (no circular dependency)
    # API may return a single object or a list of on-behalf sponsors.
    onBehalfOfSponsor: OnBehalfOfSponsor | list[OnBehalfOfSponsor] | None = None
    cosponsors: list[Cosponsor] | CountRef | None = None  # ✅ Direct import

    # === [RELATED OBJECTS] ===
    # NOTE: ✅ Sprint 2 improvement - Using reference models to avoid circular imports
    amendedBill: BillRef | None = None  # ✅ Using BillRef instead of Bill
    amendedAmendment: "Amendment | None" = None  # Self-reference is fine
    amendmentsToAmendment: list["Amendment"] | CountRef | None = None  # Self-reference is fine
    amendedTreaty: TreatyRef | None = None  # ✅ Using TreatyRef instead of Treaty

    # === [ACTIONS & TEXT] ===
    actions: list[Action] | CountRef | None = None  # ✅ Direct import (no circular dependency)
    amendmentActions: list[Action] | CountRef | None = None  # ✅ Direct import
    textVersions: list[TextVersionItem] | CountRef | None = None  # ✅ Direct import

    # === [URL] ===
    # URL class now handles string conversion automatically via __get_pydantic_core_schema__
    url: URL | None = None

    @property
    def latest_action(self) -> "LatestAction | None":
        return self.latestAction

    @latest_action.setter
    def latest_action(self, value: "LatestAction | None") -> None:
        self.latestAction = value

    @property
    def amended_bill(self) -> "Bill | None":
        return self.amendedBill

    @amended_bill.setter
    def amended_bill(self, value: "Bill | None") -> None:
        self.amendedBill = value

    @property
    def amended_amendment(self) -> "Amendment | None":
        return self.amendedAmendment

    @amended_amendment.setter
    def amended_amendment(self, value: "Amendment | None") -> None:
        self.amendedAmendment = value

    @property
    def amendments_to_amendment(self) -> list["Amendment"] | CountRef | None:
        return self.amendmentsToAmendment

    @amendments_to_amendment.setter
    def amendments_to_amendment(self, value: list["Amendment"] | CountRef | None) -> None:
        self.amendmentsToAmendment = value

    @property
    def amended_treaty(self) -> "Treaty | None":
        return self.amendedTreaty

    @amended_treaty.setter
    def amended_treaty(self, value: "Treaty | None") -> None:
        self.amendedTreaty = value

    @property
    def amendment_actions(self) -> list["Action"] | CountRef | None:
        return self.amendmentActions

    @amendment_actions.setter
    def amendment_actions(self, value: list["Action"] | CountRef | None) -> None:
        self.amendmentActions = value

    @property
    def text_versions(self) -> list["TextVersionItem"] | CountRef | None:
        return self.textVersions

    @text_versions.setter
    def text_versions(self, value: list["TextVersionItem"] | CountRef | None) -> None:
        self.textVersions = value


# Amendment.model_rebuild()  # Handled by centralized rebuild system


class Amendments(Model):
    amendments: List["Amendment"] | None = Field(None, validation_alias=AliasChoices("amendments", "amendmentsToAmendment"))


# Amendments.model_rebuild()  # Handled by centralized rebuild system

# Add Protocol inheritance for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    # Create intersection types for IDE awareness without changing runtime behavior
    class Amendment(Model, AmendmentProtocol, AsyncAmendmentProtocol):
        """Amendment model with sync and async extension method type hints for IDE support."""
        pass
    
    class Amendments(Model, AmendmentsProtocol):
        """Amendments collection with extension method type hints for IDE support."""
        pass
