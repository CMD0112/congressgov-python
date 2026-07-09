from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NominationType")


@_attrs_define
class NominationType:
    """
    Attributes:
        is_civilian (Union[Unset, bool]):
        is_military (Union[Unset, bool]):  Example: True.
    """

    is_civilian: Union[Unset, bool] = UNSET
    is_military: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_civilian = self.is_civilian

        is_military = self.is_military

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_civilian is not UNSET:
            field_dict["isCivilian"] = is_civilian
        if is_military is not UNSET:
            field_dict["isMilitary"] = is_military

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_civilian = d.pop("isCivilian", UNSET)

        is_military = d.pop("isMilitary", UNSET)

        nomination_type = cls(
            is_civilian=is_civilian,
            is_military=is_military,
        )

        nomination_type.additional_properties = d
        return nomination_type

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
