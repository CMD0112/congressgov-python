from __future__ import annotations
from typing import List, Literal
from datetime import date
from pydantic import Field
from ..base.model import Model
from ..base.types import URL


class OnBehalfOfSponsor(Model):
    bioguideId: str | None = None
    fullName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    party: str | None = None
    state: str | None = None
    type: Literal["Submitted on behalf of", "Proposed on behalf of"] | None = None
    url: str | None = None

    @property
    def bioguide_id(self) -> str | None:
        return self.bioguideId

    @bioguide_id.setter
    def bioguide_id(self, value: str | None) -> None:
        self.bioguideId = value

    @property
    def full_name(self) -> str | None:
        return self.fullName

    @full_name.setter
    def full_name(self, value: str | None) -> None:
        self.fullName = value

    @property
    def first_name(self) -> str | None:
        return self.firstName

    @first_name.setter
    def first_name(self, value: str | None) -> None:
        self.firstName = value

    @property
    def middle_name(self) -> str | None:
        return self.middleName

    @middle_name.setter
    def middle_name(self, value: str | None) -> None:
        self.middleName = value

    @property
    def last_name(self) -> str | None:
        return self.lastName

    @last_name.setter
    def last_name(self, value: str | None) -> None:
        self.lastName = value


# OnBehalfOfSponsor.model_rebuild()  # Handled by centralized rebuild system


class OnBehalfOfSponsors(Model):
    """
    === OnBehalfOfSponsors Model ===
    Represents a container for a list of OnBehalfOfSponsor objects.
    """
    onBehalfOfSponsors: List[OnBehalfOfSponsor] | None = Field(None, alias="onBehalfOfSponsors")


# OnBehalfOfSponsors.model_rebuild()  # Handled by centralized rebuild system


class Sponsor(Model):
    """
    === Sponsor Model ===
    Represents a sponsor of a bill, with member-related fields grouped into a nested Member object.
    All member-related fields from the JSON are loaded into the `member` attribute as a Member instance.
    Other sponsor-specific fields remain at the top level.
    """

    bioguideId: str | None = None
    fullName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    party: str | None = None
    state: str | None = None    # ?: Enum?
    url: str | URL = None
    district: int | None = None
    # === [SPONSOR-SPECIFIC FIELDS] Only fields unique to sponsors ===
    isByRequest: bool | None = None

    @property
    def bioguide_id(self) -> str | None:
        """Shortcut to member.bioguideId"""
        return self.bioguideId

    @property
    def full_name(self) -> str | None:
        """Shortcut to member.firstName + lastName"""
        first = self.firstName
        middle = self.middleName
        last = self.lastName
        
        if first and last:
            if middle:
                return f"{first} {middle} {last}"
            return f"{first} {last}"
        return None

    @property
    def first_name(self) -> str | None:
        """Shortcut to member.firstName"""
        return self.firstName

    @property
    def middle_name(self) -> str | None:
        """Shortcut to member.middleName"""
        return self.middleName

    @property
    def last_name(self) -> str | None:
        """Shortcut to member.lastName"""
        return self.lastName

    @property
    def is_by_request(self) -> bool | None:
        """Return True if this sponsor is by request."""
        return self.isByRequest

    @is_by_request.setter
    def is_by_request(self, value: bool | None) -> None:
        self.isByRequest = value


# Sponsor.model_rebuild()  # Handled by centralized rebuild system


class Sponsors(Model):
    """
    === Sponsors Model ===
    Represents a container for a list of Sponsor objects.
    When validated, Pydantic will convert a list of dicts to a list of Sponsor instances.
    """
    sponsors: "List[Sponsor] | None" = Field(None, alias="sponsors")


# Sponsors.model_rebuild()  # Handled by centralized rebuild system


class Cosponsor(Model):
    """
    === Cosponsor Model ===
    Represents a cosponsor of a bill, with member-related fields grouped into a nested Member object.
    All member-related fields from the JSON are loaded into the `member` attribute as a Member instance.
    Other cosponsorship-specific fields remain at the top level.
    """

    bioguideId: str | None = None
    fullName: str | None = None
    firstName: str | None = None
    middleName: str | None = None
    lastName: str | None = None
    party: str | None = None
    state: str | None = None    # ?: Enum?
    url: str | URL = None
    district: int | None = None
    sponsorshipDate: date | None = None
    isOriginalCosponsor: bool | None = None
    sponsorshipWithdrawnDate: date | None = None

    @property
    def bioguide_id(self) -> str | None:
        """Shortcut to member.bioguideId"""
        return self.bioguideId

    @property
    def full_name(self) -> str | None:
        """Shortcut to member.firstName + lastName"""
        first = self.firstName
        middle = self.middleName
        last = self.lastName
        
        if first and last:
            if middle:
                return f"{first} {middle} {last}"
            return f"{first} {last}"
        return None

    @property
    def first_name(self) -> str | None:
        """Shortcut to member.firstName"""
        return self.firstName

    @property
    def middle_name(self) -> str | None:
        """Shortcut to member.middleName"""
        return self.middleName

    @property
    def last_name(self) -> str | None:
        """Shortcut to member.lastName"""
        return self.lastName

    @property
    def sponsorship_date(self) -> date | None:
        """Return the date this cosponsorship was made."""
        return self.sponsorshipDate

    @sponsorship_date.setter
    def sponsorship_date(self, value: date | None) -> None:
        self.sponsorshipDate = value

    @property
    def is_original_cosponsor(self) -> bool | None:
        """Return True if this cosponsor is an original cosponsor."""
        return self.isOriginalCosponsor

    @is_original_cosponsor.setter
    def is_original_cosponsor(self, value: bool | None) -> None:
        self.isOriginalCosponsor = value

    @property
    def sponsorship_withdrawn_date(self) -> date | None:
        """Return the date this cosponsorship was withdrawn, if any."""
        return self.sponsorshipWithdrawnDate

    @sponsorship_withdrawn_date.setter
    def sponsorship_withdrawn_date(self, value: date | None) -> None:
        self.sponsorshipWithdrawnDate = value

    @property
    def withdrawal_date(self) -> date | None:
        """Alias for sponsorship_withdrawn_date."""
        return self.sponsorshipWithdrawnDate

    @withdrawal_date.setter
    def withdrawal_date(self, value: date | None) -> None:
        self.sponsorshipWithdrawnDate = value


# Cosponsor.model_rebuild()  # Handled by centralized rebuild system


class Cosponsors(Model):
    cosponsors: "List[Cosponsor] | None" = Field(None, alias="cosponsors")
    pagination: dict | None = None  # ?: Does this need its own class?


# Cosponsors.model_rebuild()  # Handled by centralized rebuild system


class CosponsorsRef(Model):
    countIncludingWithdrawnCosponsors: int | None = None
    count: int | None = None
    url: str | None = None


# CosponsorsRef.model_rebuild()  # Handled by centralized rebuild system
