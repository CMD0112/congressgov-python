from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.house_requirement_item import HouseRequirementItem


T = TypeVar("T", bound="HouseRequirements")


@_attrs_define
class HouseRequirements:
    """
    Attributes:
        house_requirements (Union[Unset, list['HouseRequirementItem']]):
    """

    house_requirements: Union[Unset, list["HouseRequirementItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        house_requirements: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.house_requirements, Unset):
            house_requirements = []
            for house_requirements_item_data in self.house_requirements:
                house_requirements_item = house_requirements_item_data.to_dict()
                house_requirements.append(house_requirements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if house_requirements is not UNSET:
            field_dict["houseRequirements"] = house_requirements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.house_requirement_item import HouseRequirementItem

        d = dict(src_dict)
        house_requirements = []
        _house_requirements = d.pop("houseRequirements", UNSET)
        for house_requirements_item_data in _house_requirements or []:
            house_requirements_item = HouseRequirementItem.from_dict(house_requirements_item_data)

            house_requirements.append(house_requirements_item)

        house_requirements = cls(
            house_requirements=house_requirements,
        )

        house_requirements.additional_properties = d
        return house_requirements

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
