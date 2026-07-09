from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.communication_type import CommunicationType


T = TypeVar("T", bound="MatchCommunicationsItem")


@_attrs_define
class MatchCommunicationsItem:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        communication_type (Union[Unset, CommunicationType]):
        congress (Union[Unset, int]):  Example: 112.
        number (Union[Unset, int]):  Example: 2.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/house-communication/112/EC/2?format=json.
    """

    chamber: Union[Unset, str] = UNSET
    communication_type: Union[Unset, "CommunicationType"] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        communication_type: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.communication_type, Unset):
            communication_type = self.communication_type.to_dict()

        congress = self.congress

        number = self.number

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if communication_type is not UNSET:
            field_dict["communicationType"] = communication_type
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.communication_type import CommunicationType

        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        _communication_type = d.pop("communicationType", UNSET)
        communication_type: Union[Unset, CommunicationType]
        if isinstance(_communication_type, Unset):
            communication_type = UNSET
        else:
            communication_type = CommunicationType.from_dict(_communication_type)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        url = d.pop("url", UNSET)

        match_communications_item = cls(
            chamber=chamber,
            communication_type=communication_type,
            congress=congress,
            number=number,
            url=url,
        )

        match_communications_item.additional_properties = d
        return match_communications_item

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
