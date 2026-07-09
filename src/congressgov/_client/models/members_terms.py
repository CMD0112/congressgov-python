from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.member_terms import MemberTerms


T = TypeVar("T", bound="MembersTerms")


@_attrs_define
class MembersTerms:
    """
    Attributes:
        item (Union[Unset, list['MemberTerms']]):
    """

    item: Union[Unset, list["MemberTerms"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        item: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.item, Unset):
            item = []
            for item_item_data in self.item:
                item_item = item_item_data.to_dict()
                item.append(item_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if item is not UNSET:
            field_dict["item"] = item

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_terms import MemberTerms

        d = dict(src_dict)
        item = []
        _item = d.pop("item", UNSET)
        for item_item_data in _item or []:
            item_item = MemberTerms.from_dict(item_item_data)

            item.append(item_item)

        members_terms = cls(
            item=item,
        )

        members_terms.additional_properties = d
        return members_terms

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
