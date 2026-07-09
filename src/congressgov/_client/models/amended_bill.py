import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AmendedBill")


@_attrs_define
class AmendedBill:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 117.
        number (Union[Unset, str]):  Example: 5.
        origin_chamber (Union[Unset, str]):  Example: Senate.
        origin_chamber_code (Union[Unset, str]):  Example: S.
        title (Union[Unset, str]):  Example: A concurrent resolution setting forth the congressional budget for the
            United States Government for fiscal year 2021 and setting forth the appropriate budgetary levels for fiscal
            years 2022 through 2030..
        type_ (Union[Unset, str]):  Example: SCONRES.
        update_date_including_text (Union[Unset, datetime.date]):  Example: 2025-04-07.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/117/sconres/5?format=json.
    """

    congress: Union[Unset, int] = UNSET
    number: Union[Unset, str] = UNSET
    origin_chamber: Union[Unset, str] = UNSET
    origin_chamber_code: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date_including_text: Union[Unset, datetime.date] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        number = self.number

        origin_chamber = self.origin_chamber

        origin_chamber_code = self.origin_chamber_code

        title = self.title

        type_ = self.type_

        update_date_including_text: Union[Unset, str] = UNSET
        if not isinstance(self.update_date_including_text, Unset):
            update_date_including_text = self.update_date_including_text.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if origin_chamber is not UNSET:
            field_dict["originChamber"] = origin_chamber
        if origin_chamber_code is not UNSET:
            field_dict["originChamberCode"] = origin_chamber_code
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date_including_text is not UNSET:
            field_dict["updateDateIncludingText"] = update_date_including_text
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        origin_chamber = d.pop("originChamber", UNSET)

        origin_chamber_code = d.pop("originChamberCode", UNSET)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date_including_text = d.pop("updateDateIncludingText", UNSET)
        update_date_including_text: Union[Unset, datetime.date]
        if isinstance(_update_date_including_text, Unset) or _update_date_including_text is None:
            update_date_including_text = UNSET
        else:
            update_date_including_text = isoparse(_update_date_including_text)

        url = d.pop("url", UNSET)

        amended_bill = cls(
            congress=congress,
            number=number,
            origin_chamber=origin_chamber,
            origin_chamber_code=origin_chamber_code,
            title=title,
            type_=type_,
            update_date_including_text=update_date_including_text,
            url=url,
        )

        amended_bill.additional_properties = d
        return amended_bill

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
