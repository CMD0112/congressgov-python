import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteePrints")


@_attrs_define
class CommitteePrints:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        congress (Union[Unset, int]):  Example: 117.
        jacket_number (Union[Unset, int]):  Example: 48144.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-08-01 21:19:33+00:00.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee-print/117/house/48144?format=json.
    """

    chamber: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    jacket_number: Union[Unset, int] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        congress = self.congress

        jacket_number = self.jacket_number

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if congress is not UNSET:
            field_dict["congress"] = congress
        if jacket_number is not UNSET:
            field_dict["jacketNumber"] = jacket_number
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        congress = d.pop("congress", UNSET)

        jacket_number = d.pop("jacketNumber", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        committee_prints = cls(
            chamber=chamber,
            congress=congress,
            jacket_number=jacket_number,
            update_date=update_date,
            url=url,
        )

        committee_prints.additional_properties = d
        return committee_prints

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
