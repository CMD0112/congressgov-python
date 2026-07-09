from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Witness")


@_attrs_define
class Witness:
    """
    Attributes:
        name (Union[Unset, str]):  Example: The Honorable John Williams.
        organization (Union[Unset, str]):  Example: United Auburn Rancheria.
        position (Union[Unset, str]):  Example: Vice Chairman.
    """

    name: Union[Unset, str] = UNSET
    organization: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        organization = self.organization

        position = self.position

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if organization is not UNSET:
            field_dict["organization"] = organization
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        organization = d.pop("organization", UNSET)

        position = d.pop("position", UNSET)

        witness = cls(
            name=name,
            organization=organization,
            position=position,
        )

        witness.additional_properties = d
        return witness

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
