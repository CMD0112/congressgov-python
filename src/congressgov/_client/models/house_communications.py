from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.house_communication import HouseCommunication


T = TypeVar("T", bound="HouseCommunications")


@_attrs_define
class HouseCommunications:
    """
    Attributes:
        house_coummunications (Union[Unset, list['HouseCommunication']]):
    """

    house_coummunications: Union[Unset, list["HouseCommunication"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        house_coummunications: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.house_coummunications, Unset):
            house_coummunications = []
            for house_coummunications_item_data in self.house_coummunications:
                house_coummunications_item = house_coummunications_item_data.to_dict()
                house_coummunications.append(house_coummunications_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if house_coummunications is not UNSET:
            field_dict["houseCoummunications"] = house_coummunications

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.house_communication import HouseCommunication

        d = dict(src_dict)
        house_coummunications = []
        _house_coummunications = d.pop("houseCoummunications", UNSET)
        for house_coummunications_item_data in _house_coummunications or []:
            house_coummunications_item = HouseCommunication.from_dict(house_coummunications_item_data)

            house_coummunications.append(house_coummunications_item)

        house_communications = cls(
            house_coummunications=house_coummunications,
        )

        house_communications.additional_properties = d
        return house_communications

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
