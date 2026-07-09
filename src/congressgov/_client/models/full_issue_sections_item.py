from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.full_issue_sections_item_text_item import FullIssueSectionsItemTextItem


T = TypeVar("T", bound="FullIssueSectionsItem")


@_attrs_define
class FullIssueSectionsItem:
    """
    Attributes:
        end_page (Union[Unset, str]):  Example: D12.
        name (Union[Unset, str]):  Example: Daily Digest.
        start_page (Union[Unset, str]):  Example: D1.
        text (Union[Unset, list['FullIssueSectionsItemTextItem']]):
    """

    end_page: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    start_page: Union[Unset, str] = UNSET
    text: Union[Unset, list["FullIssueSectionsItemTextItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_page = self.end_page

        name = self.name

        start_page = self.start_page

        text: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.text, Unset):
            text = []
            for text_item_data in self.text:
                text_item = text_item_data.to_dict()
                text.append(text_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if end_page is not UNSET:
            field_dict["endPage"] = end_page
        if name is not UNSET:
            field_dict["name"] = name
        if start_page is not UNSET:
            field_dict["startPage"] = start_page
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.full_issue_sections_item_text_item import FullIssueSectionsItemTextItem

        d = dict(src_dict)
        end_page = d.pop("endPage", UNSET)

        name = d.pop("name", UNSET)

        start_page = d.pop("startPage", UNSET)

        text = []
        _text = d.pop("text", UNSET)
        for text_item_data in _text or []:
            text_item = FullIssueSectionsItemTextItem.from_dict(text_item_data)

            text.append(text_item)

        full_issue_sections_item = cls(
            end_page=end_page,
            name=name,
            start_page=start_page,
            text=text,
        )

        full_issue_sections_item.additional_properties = d
        return full_issue_sections_item

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
