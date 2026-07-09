from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Sponsor")


@_attrs_define
class Sponsor:
    """
    Attributes:
        bioguide_id (Union[Unset, str]):  Example: G000555.
        first_name (Union[Unset, str]):  Example: Bill.
        last_name (Union[Unset, str]):  Example: Washington.
        full_name (Union[Unset, str]):  Example: Senator Bill Washington [I-NY].
        is_by_request (Union[Unset, str]):  Example: N.
        middle_name (Union[Unset, str]):  Example: J..
        party (Union[Unset, str]):  Example: I.
        state (Union[Unset, str]):  Example: VA.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/member/G000555?format=json.
    """

    bioguide_id: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    full_name: Union[Unset, str] = UNSET
    is_by_request: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    party: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bioguide_id = self.bioguide_id

        first_name = self.first_name

        last_name = self.last_name

        full_name = self.full_name

        is_by_request = self.is_by_request

        middle_name = self.middle_name

        party = self.party

        state = self.state

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bioguide_id is not UNSET:
            field_dict["bioguideId"] = bioguide_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if full_name is not UNSET:
            field_dict["fullName"] = full_name
        if is_by_request is not UNSET:
            field_dict["isByRequest"] = is_by_request
        if middle_name is not UNSET:
            field_dict["middleName"] = middle_name
        if party is not UNSET:
            field_dict["party"] = party
        if state is not UNSET:
            field_dict["state"] = state
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bioguide_id = d.pop("bioguideId", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        full_name = d.pop("fullName", UNSET)

        is_by_request = d.pop("isByRequest", UNSET)

        middle_name = d.pop("middleName", UNSET)

        party = d.pop("party", UNSET)

        state = d.pop("state", UNSET)

        url = d.pop("url", UNSET)

        sponsor = cls(
            bioguide_id=bioguide_id,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            is_by_request=is_by_request,
            middle_name=middle_name,
            party=party,
            state=state,
            url=url,
        )

        sponsor.additional_properties = d
        return sponsor

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
