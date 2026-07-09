import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CoSponsor")


@_attrs_define
class CoSponsor:
    """
    Attributes:
        bioguid_id (Union[Unset, str]):  Example: F000450.
        district (Union[Unset, int]):  Example: 5.
        first_name (Union[Unset, str]):  Example: Virginia.
        full_name (Union[Unset, str]):  Example: Rep. Foxx, Virginia [R-NC-5].
        is_original_cosponsor (Union[Unset, bool]):  Example: True.
        last_name (Union[Unset, str]):  Example: Foxx.
        party (Union[Unset, str]):  Example: R.
        sponsorship_date (Union[Unset, datetime.date]):  Example: 2021-05-11.
        state (Union[Unset, str]):  Example: NC.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/member/F000450?format=json.
    """

    bioguid_id: Union[Unset, str] = UNSET
    district: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    full_name: Union[Unset, str] = UNSET
    is_original_cosponsor: Union[Unset, bool] = UNSET
    last_name: Union[Unset, str] = UNSET
    party: Union[Unset, str] = UNSET
    sponsorship_date: Union[Unset, datetime.date] = UNSET
    state: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bioguid_id = self.bioguid_id

        district = self.district

        first_name = self.first_name

        full_name = self.full_name

        is_original_cosponsor = self.is_original_cosponsor

        last_name = self.last_name

        party = self.party

        sponsorship_date: Union[Unset, str] = UNSET
        if not isinstance(self.sponsorship_date, Unset):
            sponsorship_date = self.sponsorship_date.isoformat()

        state = self.state

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bioguid_id is not UNSET:
            field_dict["bioguidId"] = bioguid_id
        if district is not UNSET:
            field_dict["district"] = district
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if full_name is not UNSET:
            field_dict["fullName"] = full_name
        if is_original_cosponsor is not UNSET:
            field_dict["isOriginalCosponsor"] = is_original_cosponsor
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if party is not UNSET:
            field_dict["party"] = party
        if sponsorship_date is not UNSET:
            field_dict["sponsorshipDate"] = sponsorship_date
        if state is not UNSET:
            field_dict["state"] = state
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bioguid_id = d.pop("bioguidId", UNSET)

        district = d.pop("district", UNSET)

        first_name = d.pop("firstName", UNSET)

        full_name = d.pop("fullName", UNSET)

        is_original_cosponsor = d.pop("isOriginalCosponsor", UNSET)

        last_name = d.pop("lastName", UNSET)

        party = d.pop("party", UNSET)

        _sponsorship_date = d.pop("sponsorshipDate", UNSET)
        sponsorship_date: Union[Unset, datetime.date]
        if isinstance(_sponsorship_date, Unset) or _sponsorship_date is None:
            sponsorship_date = UNSET
        else:
            sponsorship_date = isoparse(_sponsorship_date)

        state = d.pop("state", UNSET)

        url = d.pop("url", UNSET)

        co_sponsor = cls(
            bioguid_id=bioguid_id,
            district=district,
            first_name=first_name,
            full_name=full_name,
            is_original_cosponsor=is_original_cosponsor,
            last_name=last_name,
            party=party,
            sponsorship_date=sponsorship_date,
            state=state,
            url=url,
        )

        co_sponsor.additional_properties = d
        return co_sponsor

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
