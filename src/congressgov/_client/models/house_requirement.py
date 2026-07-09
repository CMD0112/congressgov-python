from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.house_requirement_house_requirement import HouseRequirementHouseRequirement


T = TypeVar("T", bound="HouseRequirement")


@_attrs_define
class HouseRequirement:
    """
    Attributes:
        house_requirement (Union[Unset, HouseRequirementHouseRequirement]):
    """

    house_requirement: Union[Unset, "HouseRequirementHouseRequirement"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        house_requirement: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.house_requirement, Unset):
            house_requirement = self.house_requirement.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if house_requirement is not UNSET:
            field_dict["houseRequirement"] = house_requirement

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.house_requirement_house_requirement import HouseRequirementHouseRequirement

        d = dict(src_dict)
        _house_requirement = d.pop("houseRequirement", UNSET)
        house_requirement: Union[Unset, HouseRequirementHouseRequirement]
        if isinstance(_house_requirement, Unset):
            house_requirement = UNSET
        else:
            house_requirement = HouseRequirementHouseRequirement.from_dict(_house_requirement)

        house_requirement = cls(
            house_requirement=house_requirement,
        )

        house_requirement.additional_properties = d
        return house_requirement

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
