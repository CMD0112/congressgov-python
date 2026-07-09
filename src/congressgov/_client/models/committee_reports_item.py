import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteeReportsItem")


@_attrs_define
class CommitteeReportsItem:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        citation (Union[Unset, str]):  Example: H. Rept. 109-570.
        congress (Union[Unset, int]):  Example: 117.
        number (Union[Unset, int]):  Example: 570.
        part (Union[Unset, int]):  Example: 1.
        type_ (Union[Unset, str]):  Example: HRPT.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-02-18T16:38:41Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/117hr570?format=json.
    """

    chamber: Union[Unset, str] = UNSET
    citation: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    part: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        citation = self.citation

        congress = self.congress

        number = self.number

        part = self.part

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if citation is not UNSET:
            field_dict["citation"] = citation
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if part is not UNSET:
            field_dict["part"] = part
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        citation = d.pop("citation", UNSET)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        part = d.pop("part", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        committee_reports_item = cls(
            chamber=chamber,
            citation=citation,
            congress=congress,
            number=number,
            part=part,
            type_=type_,
            update_date=update_date,
            url=url,
        )

        committee_reports_item.additional_properties = d
        return committee_reports_item

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
