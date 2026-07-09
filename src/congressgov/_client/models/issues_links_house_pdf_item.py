from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IssuesLinksHousePDFItem")


@_attrs_define
class IssuesLinksHousePDFItem:
    """
    Attributes:
        part (Union[Unset, str]):  Example: 1.
        url (Union[Unset, str]):  Example:
            https://www.congress.gov/117/crec/2022/06/28/168/109/CREC-2022-06-28-house.pdf.
    """

    part: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        part = self.part

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if part is not UNSET:
            field_dict["Part"] = part
        if url is not UNSET:
            field_dict["Url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        part = d.pop("Part", UNSET)

        url = d.pop("Url", UNSET)

        issues_links_house_pdf_item = cls(
            part=part,
            url=url,
        )

        issues_links_house_pdf_item.additional_properties = d
        return issues_links_house_pdf_item

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
