from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RelatedMaterial")


@_attrs_define
class RelatedMaterial:
    """
    Attributes:
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/law/93/pub/344.
        congress (Union[Unset, int]):  Example: 93.
        number (Union[Unset, str]):  Example: 93-344.
        title (Union[Unset, str]):  Example: Providing for budget allocations, and for other purposes..
        type_ (Union[Unset, str]):  Example: PUB.
    """

    url: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        congress = self.congress

        number = self.number

        title = self.title

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["URL"] = url
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("URL", UNSET)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        related_material = cls(
            url=url,
            congress=congress,
            number=number,
            title=title,
            type_=type_,
        )

        related_material.additional_properties = d
        return related_material

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
