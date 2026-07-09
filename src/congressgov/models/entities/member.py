from __future__ import annotations
from typing import Any, TYPE_CHECKING
from pydantic import Field, model_validator
from ..base.enums import LegislationType
from ..base.types import URL, CountRef, PolicyArea
from ..base.model import Model

# Import protocols for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    from congressgov.services.protocols.member import MemberProtocol, MembersProtocol
    from congressgov.services.protocols.async_member import AsyncMemberProtocol
from ..actions.action import LatestAction
from datetime import date


class Depiction(Model):
    imageUrl: URL | str | None = None
    attribution: str | None = None


# Depiction.model_rebuild()  # Handled by centralized rebuild system


class Term(Model):
    memberType: str | None = None
    congress: int | None = None
    chamber: str | None = None
    stateCode: str | None = None
    stateName: str | None = None
    partyName: str | None = None
    partyCode: str | None = None
    startYear: int | None = None
    endYear: int | None = None
    district: str | int | None = None


# Term.model_rebuild()  # Handled by centralized rebuild system


class Terms(Model):
    """
    Wrapper model for the terms field which comes from the API as {'item': [...]}.
    This is pure Pydantic - no custom validation needed.
    """
    item: list[Term] | None = None


# Terms.model_rebuild()  # Handled by centralized rebuild system


class AddressInformation(Model):
    officeAddress: str | None = None
    city: str | None = None
    district: str | None = None
    zipCode: str | None = None
    phoneNumber: str | None = None


# AddressInformation.model_rebuild()  # Handled by centralized rebuild system


class LeadershipRole(Model):
    type: str | None = None
    congress: int | None = None
    current: bool | None = None


# LeadershipRole.model_rebuild()  # Handled by centralized rebuild system


class Leadership(Model):
    roles: list[LeadershipRole] | None = None


# Leadership.model_rebuild()  # Handled by centralized rebuild system


class PreviousName(Model):
    honorificName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    suffixName: str | None = None
    directOrderName: str | None = None
    invertedOrderName: str | None = None
    startDate: date | str | None = None
    endDate: date | str | None = None


# PreviousName.model_rebuild()  # Handled by centralized rebuild system


class PreviousNames(Model):
    previousNames: list[PreviousName] | None = Field(None, alias="previousNames")
    updateDate: date | str | None = None
    
    @classmethod
    def _get_item_wrapped_fields(cls) -> set[str]:
        return {'previousNames'}


# PreviousNames.model_rebuild()  # Handled by centralized rebuild system


class Member(Model):
    """A member of Congress: identity, current term info, leadership roles, and
    counts of sponsored/cosponsored legislation.
    """

    currentMember: bool | None = None
    birthYear: int | None = None
    deathYear: int | None = None
    updateDate: date | str | None = None
    depiction: Depiction | None = None
    terms: Terms | None = None
    bioguideId: str | None = None
    partyName: str | None = None
    state: str | None = None
    district: str | int | None = None  # Allow both string and int for district
    officialUrl: URL | str | None = None
    honorificName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    suffixName: str | None = None
    nickName: str | None = None
    directOrderName: str | None = None
    invertedOrderName: str | None = None
    addressInformation: AddressInformation | None = None
    leadership: Leadership | None = None
    sponsoredLegislation: CountRef | None = None
    cosponsoredLegislation: CountRef | None = None
    previousNames: PreviousNames | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_detail_payload(cls, values: Any) -> Any:
        """Coerce member detail shapes that differ from list endpoints."""
        if not isinstance(values, dict):
            return values
        terms = values.get("terms")
        if isinstance(terms, list):
            values["terms"] = {"item": terms}
        previous_names = values.get("previousNames")
        if isinstance(previous_names, list):
            values["previousNames"] = {"previousNames": previous_names}
        address = values.get("addressInformation")
        if isinstance(address, dict):
            zip_code = address.get("zipCode")
            if isinstance(zip_code, int):
                values["addressInformation"] = {**address, "zipCode": str(zip_code)}
        leadership = values.get("leadership")
        if isinstance(leadership, list):
            values["leadership"] = {"roles": leadership}
        return values


# Member.model_rebuild()  # Handled by centralized rebuild system

# Set by congressgov.services.extensions.members, which builds the query class
# via the generic query builder in congressgov.services.extensions._query_builder.
MembersQuery = None

class Members(Model):
    """
    Collection of Member objects.
    
    Query methods are dynamically registered from congressgov.services.extensions.members.
    Import that module to enable query functionality:
        from congressgov.services import extensions  # Registers methods on import
    
    Example usage:
        members.filter(state="CA")
        members.by_party("Democratic")
        members.current()
    """
    members: list[Member] | None = Field(None, alias="members")


# Members.model_rebuild()  # Handled by centralized rebuild system

# Add Protocol inheritance for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    # Create intersection types for IDE awareness without changing runtime behavior
    class Member(Model, MemberProtocol, AsyncMemberProtocol):
        """Member model with sync and async extension method type hints for IDE support."""
        pass
    
    class Members(Model, MembersProtocol):
        """Members collection with extension method type hints for IDE support."""
        pass


class SponsoredLegislationItem(Model):
    introducedDate: date | str | None = None
    type: LegislationType | str | None = None  # amendments use HAMDT, SAMDT, etc.
    congress: int | None = None
    latestTitle: str | None = None
    title: str | None = None  # For amendments
    number: str | None = None
    amendmentNumber: str | None = None  # For amendments
    policyArea: Any | None = None  # Optional - amendments don't have policy areas
    latestAction: "LatestAction | None" = None
    # URL class now handles string conversion automatically via __get_pydantic_core_schema__
    url: URL | None = None


# SponsoredLegislationItem.model_rebuild()  # Handled by centralized rebuild system


class SponsoredLegislation(Model):
    sponsoredLegislation: list[SponsoredLegislationItem] | None = Field(None, alias="sponsoredLegislation")
    
    @classmethod
    def _get_item_wrapped_fields(cls) -> set[str]:
        return {'sponsoredLegislation'}


# SponsoredLegislation.model_rebuild()  # Handled by centralized rebuild system


class CosponsoredLegislationItem(Model):
    introducedDate: date | str | None = None
    type: LegislationType | str | None = None  # amendments use HAMDT, SAMDT, etc.
    congress: int | None = None
    latestTitle: str | None = None
    number: str | None = None
    policyArea: PolicyArea | Any | None = None
    latestAction: "LatestAction | None" = None
    # URL class now handles string conversion automatically via __get_pydantic_core_schema__
    url: URL | None = None


# CosponsoredLegislationItem.model_rebuild()  # Handled by centralized rebuild system


class CosponsoredLegislation(Model):
    cosponsoredLegislation: list[CosponsoredLegislationItem] | None = Field(None, alias="cosponsoredLegislation")
    
    @classmethod
    def _get_item_wrapped_fields(cls) -> set[str]:
        return {'cosponsoredLegislation'}


# CosponsoredLegislation.model_rebuild()  # Handled by centralized rebuild system


def _ensure_member_instance_extensions() -> None:
    """Register ``get_sponsored_legislation`` / ``get_cosponsored_legislation`` on ``Member``."""
    if hasattr(Member, "get_cosponsored_legislation"):
        return
    import importlib

    importlib.import_module("congressgov.services.extensions.members")


_ensure_member_instance_extensions()
