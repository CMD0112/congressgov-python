from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TreatyDetailTreatyTitlesItem")


@_attrs_define
class TreatyDetailTreatyTitlesItem:
    """
    Attributes:
        title (Union[Unset, str]):  Example: PROTOCOL MODIFYING CONVENTION WITH BELGIUM FOR THE AVOIDANCE OF DOUBLE
            TAXATION.
        title_type (Union[Unset, str]):  Example: Treaty - Short Title.
    """

    title: Union[Unset, str] = UNSET
    title_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        title_type = self.title_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if title_type is not UNSET:
            field_dict["titleType"] = title_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        title_type = d.pop("titleType", UNSET)

        treaty_detail_treaty_titles_item = cls(
            title=title,
            title_type=title_type,
        )

        treaty_detail_treaty_titles_item.additional_properties = d
        return treaty_detail_treaty_titles_item

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
