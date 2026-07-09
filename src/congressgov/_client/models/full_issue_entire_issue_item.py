from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FullIssueEntireIssueItem")


@_attrs_define
class FullIssueEntireIssueItem:
    """
    Attributes:
        part (Union[Unset, str]):  Example: 1.
        type_ (Union[Unset, str]):  Example: PDF.
        url (Union[Unset, str]):  Example: https://www.congress.gov/119/crec/2025/01/03/171/1/CREC-2025-01-03-v171.pdf.
    """

    part: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        part = self.part

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if part is not UNSET:
            field_dict["part"] = part
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        part = d.pop("part", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        full_issue_entire_issue_item = cls(
            part=part,
            type_=type_,
            url=url,
        )

        full_issue_entire_issue_item.additional_properties = d
        return full_issue_entire_issue_item

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
