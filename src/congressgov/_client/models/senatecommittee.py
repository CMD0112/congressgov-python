from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Senatecommittee")


@_attrs_define
class Senatecommittee:
    """
    Attributes:
        name (Union[Unset, str]):  Example: Armed Services Committee.
        system_code (Union[Unset, str]):  Example: ssas00.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee/senate/ssas00?format=json.
    """

    name: Union[Unset, str] = UNSET
    system_code: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        system_code = self.system_code

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if system_code is not UNSET:
            field_dict["systemCode"] = system_code
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        system_code = d.pop("systemCode", UNSET)

        url = d.pop("url", UNSET)

        senatecommittee = cls(
            name=name,
            system_code=system_code,
            url=url,
        )

        senatecommittee.additional_properties = d
        return senatecommittee

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
