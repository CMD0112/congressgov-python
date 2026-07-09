import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="NominationHearingItem")


@_attrs_define
class NominationHearingItem:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: Senate.
        citation (Union[Unset, str]):  Example: S.Hrg.118-694.
        date (Union[Unset, datetime.date]):  Example: 2024-02-28.
        jacke_number (Union[Unset, int]):  Example: 61203.
        number (Union[Unset, int]):  Example: 694.
    """

    chamber: Union[Unset, str] = UNSET
    citation: Union[Unset, str] = UNSET
    date: Union[Unset, datetime.date] = UNSET
    jacke_number: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        citation = self.citation

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        jacke_number = self.jacke_number

        number = self.number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if citation is not UNSET:
            field_dict["citation"] = citation
        if date is not UNSET:
            field_dict["date"] = date
        if jacke_number is not UNSET:
            field_dict["jackeNumber"] = jacke_number
        if number is not UNSET:
            field_dict["number"] = number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        citation = d.pop("citation", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.date]
        if isinstance(_date, Unset) or _date is None:
            date = UNSET
        else:
            date = isoparse(_date)

        jacke_number = d.pop("jackeNumber", UNSET)

        number = d.pop("number", UNSET)

        nomination_hearing_item = cls(
            chamber=chamber,
            citation=citation,
            date=date,
            jacke_number=jacke_number,
            number=number,
        )

        nomination_hearing_item.additional_properties = d
        return nomination_hearing_item

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
