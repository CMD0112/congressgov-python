from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MembersDepiction")


@_attrs_define
class MembersDepiction:
    """
    Attributes:
        attribution (Union[Unset, str]):  Example: Congressional Pictorial Directory.
        image_url (Union[Unset, str]):  Example: https://www.congress.gov/img/member/116_dg_dc_norton_eleanor_200.jpg.
    """

    attribution: Union[Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attribution = self.attribution

        image_url = self.image_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attribution is not UNSET:
            field_dict["attribution"] = attribution
        if image_url is not UNSET:
            field_dict["imageUrl"] = image_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attribution = d.pop("attribution", UNSET)

        image_url = d.pop("imageUrl", UNSET)

        members_depiction = cls(
            attribution=attribution,
            image_url=image_url,
        )

        members_depiction.additional_properties = d
        return members_depiction

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
