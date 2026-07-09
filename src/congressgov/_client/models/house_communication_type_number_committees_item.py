import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="HouseCommunicationTypeNumberCommitteesItem")


@_attrs_define
class HouseCommunicationTypeNumberCommitteesItem:
    """
    Attributes:
        name (Union[Unset, str]):  Example: Investigations and Oversight Subcommittee.
        system_code (Union[Unset, str]):  Example: hspw01.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee/house/hspw01?format=json.
        referral_date (Union[Unset, datetime.date]):  Example: 2024-03-07.
    """

    name: Union[Unset, str] = UNSET
    system_code: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    referral_date: Union[Unset, datetime.date] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        system_code = self.system_code

        url = self.url

        referral_date: Union[Unset, str] = UNSET
        if not isinstance(self.referral_date, Unset):
            referral_date = self.referral_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if system_code is not UNSET:
            field_dict["systemCode"] = system_code
        if url is not UNSET:
            field_dict["url"] = url
        if referral_date is not UNSET:
            field_dict["referralDate"] = referral_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        system_code = d.pop("systemCode", UNSET)

        url = d.pop("url", UNSET)

        _referral_date = d.pop("referralDate", UNSET)
        referral_date: Union[Unset, datetime.date]
        if isinstance(_referral_date, Unset) or _referral_date is None:
            referral_date = UNSET
        else:
            referral_date = isoparse(_referral_date)

        house_communication_type_number_committees_item = cls(
            name=name,
            system_code=system_code,
            url=url,
            referral_date=referral_date,
        )

        house_communication_type_number_committees_item.additional_properties = d
        return house_communication_type_number_committees_item

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
