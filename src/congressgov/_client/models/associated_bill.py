from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssociatedBill")


@_attrs_define
class AssociatedBill:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 116.
        number (Union[Unset, str]):  Example: 6395.
        type_ (Union[Unset, str]):  Example: HR.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/116/hr/6395?format=json.
    """

    congress: Union[Unset, int] = UNSET
    number: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        number = self.number

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        associated_bill = cls(
            congress=congress,
            number=number,
            type_=type_,
            url=url,
        )

        associated_bill.additional_properties = d
        return associated_bill

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
