import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.members_depiction import MembersDepiction
    from ..models.members_terms import MembersTerms


T = TypeVar("T", bound="Members")


@_attrs_define
class Members:
    """
    Attributes:
        bioguide_id (Union[Unset, str]):  Example: N000147.
        depiction (Union[Unset, MembersDepiction]):
        name (Union[Unset, str]):  Example: Norton, Eleanor Holmes.
        party_name (Union[Unset, str]):  Example: Democratic.
        state (Union[Unset, str]):  Example: District of Columbia.
        terms (Union[Unset, MembersTerms]):
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-11-12T08:45:43Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/member/N000147?format=json.
    """

    bioguide_id: Union[Unset, str] = UNSET
    depiction: Union[Unset, "MembersDepiction"] = UNSET
    name: Union[Unset, str] = UNSET
    party_name: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    terms: Union[Unset, "MembersTerms"] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bioguide_id = self.bioguide_id

        depiction: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.depiction, Unset):
            depiction = self.depiction.to_dict()

        name = self.name

        party_name = self.party_name

        state = self.state

        terms: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.terms, Unset):
            terms = self.terms.to_dict()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bioguide_id is not UNSET:
            field_dict["bioguideId"] = bioguide_id
        if depiction is not UNSET:
            field_dict["depiction"] = depiction
        if name is not UNSET:
            field_dict["name"] = name
        if party_name is not UNSET:
            field_dict["partyName"] = party_name
        if state is not UNSET:
            field_dict["state"] = state
        if terms is not UNSET:
            field_dict["terms"] = terms
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.members_depiction import MembersDepiction
        from ..models.members_terms import MembersTerms

        d = dict(src_dict)
        bioguide_id = d.pop("bioguideId", UNSET)

        _depiction = d.pop("depiction", UNSET)
        depiction: Union[Unset, MembersDepiction]
        if isinstance(_depiction, Unset):
            depiction = UNSET
        else:
            depiction = MembersDepiction.from_dict(_depiction)

        name = d.pop("name", UNSET)

        party_name = d.pop("partyName", UNSET)

        state = d.pop("state", UNSET)

        _terms = d.pop("terms", UNSET)
        terms: Union[Unset, MembersTerms]
        if isinstance(_terms, Unset):
            terms = UNSET
        else:
            terms = MembersTerms.from_dict(_terms)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        members = cls(
            bioguide_id=bioguide_id,
            depiction=depiction,
            name=name,
            party_name=party_name,
            state=state,
            terms=terms,
            update_date=update_date,
            url=url,
        )

        members.additional_properties = d
        return members

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
