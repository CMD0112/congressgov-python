from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Nominee")


@_attrs_define
class Nominee:
    """
    Attributes:
        nominee_count (Union[Unset, int]):  Example: 1.
        ordinal (Union[Unset, int]):  Example: 1.
        organization (Union[Unset, str]):  Example: Federal Maritime Commission.
        position_title (Union[Unset, str]):  Example: Federal Maritime Commissioner.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/nomination/118/16/1?format=json.
    """

    nominee_count: Union[Unset, int] = UNSET
    ordinal: Union[Unset, int] = UNSET
    organization: Union[Unset, str] = UNSET
    position_title: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nominee_count = self.nominee_count

        ordinal = self.ordinal

        organization = self.organization

        position_title = self.position_title

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nominee_count is not UNSET:
            field_dict["nomineeCount"] = nominee_count
        if ordinal is not UNSET:
            field_dict["ordinal"] = ordinal
        if organization is not UNSET:
            field_dict["organization"] = organization
        if position_title is not UNSET:
            field_dict["positionTitle"] = position_title
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        nominee_count = d.pop("nomineeCount", UNSET)

        ordinal = d.pop("ordinal", UNSET)

        organization = d.pop("organization", UNSET)

        position_title = d.pop("positionTitle", UNSET)

        url = d.pop("url", UNSET)

        nominee = cls(
            nominee_count=nominee_count,
            ordinal=ordinal,
            organization=organization,
            position_title=position_title,
            url=url,
        )

        nominee.additional_properties = d
        return nominee

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
