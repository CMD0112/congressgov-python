from __future__ import annotations
from typing import Optional, List
from pydantic import Field
from ..base.model import Model
from ..base.enums import Chamber, CommitteeType
from ..base.types import URL, CountRef
from ..actions.action import Action
from ..core.core import Title

class IndexTerm(Model):
    name: Optional[str] = None


# IndexTerm.model_rebuild()  # Handled by centralized rebuild system


class IndexTerms(Model):
    indexTerms: Optional[List[IndexTerm]] = Field(None, alias="indexTerms")


# IndexTerms.model_rebuild()  # Handled by centralized rebuild system


class Country(Model):
    name: Optional[str] = None


# Country.model_rebuild()  # Handled by centralized rebuild system


class Countries(Model):
    countries: Optional[List[Country]] = Field(None, alias="countries")


# Countries.model_rebuild()  # Handled by centralized rebuild system


class RelatedDoc(Model):
    name: Optional[str] = None
    url: Optional[str] = None


# RelatedDoc.model_rebuild()  # Handled by centralized rebuild system


class RelatedDocs(Model):
    relatedDocs: Optional[List[RelatedDoc]] = Field(None, alias="relatedDocs")


# RelatedDocs.model_rebuild()  # Handled by centralized rebuild system


class PartUrl(Model):
    url: Optional[str] = None


# PartUrl.model_rebuild()  # Handled by centralized rebuild system


class Urls(Model):
    urls: Optional[List[PartUrl]] = Field(None, alias="urls")


# Urls.model_rebuild()  # Handled by centralized rebuild system


class Part(Model):
    count: Optional[int] = None
    urls: Optional[Urls] = None


# Part.model_rebuild()  # Handled by centralized rebuild system


class Parts(Model):
    parts: Optional[List[Part]] = Field(None, alias="parts")


# Parts.model_rebuild()  # Handled by centralized rebuild system


class TreatyCommittee(Model):
    # URL class now handles string conversion automatically via __get_pydantic_core_schema__
    url: URL | None = None
    systemCode: str | None = None
    name: str | None = None
    chamber: Chamber | None = None
    type: CommitteeType | None = None
    subcommittees: "list[Committee] | None" = None
    activities: "list[dict] | None" = None  # TODO: Define CommitteeActivity class


# TreatyCommittee.model_rebuild()  # Handled by centralized rebuild system


class TreatyCommittees(Model):
    treatyCommittees: list[TreatyCommittee] | None = Field(None, alias="treatyCommittees")  # Can be list or reference


# TreatyCommittees.model_rebuild()  # Handled by centralized rebuild system


class Treaty(Model):
    """A treaty submitted to the Senate: parties, committee referrals, actions, and text."""

    congressReceived: int | None = None
    congressConsidered: int | None = None
    number: int | None = None
    suffix: str | None = None
    countriesParties: list[Country] | None = None
    oldNumber: str | None = None
    oldNumberDisplayName: str | None = None
    transmittedDate: str | None = None
    inForceDate: str | None = None
    indexTerms: list[IndexTerm] | None = None
    relatedDocs: list[RelatedDoc] | None = None
    resolutionText: str | None = None    # TODO: Consider using different typing since this is a large text field using HTML
    topic: str | None = None
    updateDate: str | None = None
    parts: Parts | None = None
    titles: "list[Title] | None" = None
    actions: list[Action] | CountRef | None = None


# Treaty.model_rebuild()  # Handled by centralized rebuild system


class Treaties(Model):
    treaties: List[Treaty] | None = Field(None, alias="treaties")


# Treaties.model_rebuild()  # Handled by centralized rebuild system
