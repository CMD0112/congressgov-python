from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_committee import TreatyCommittee


T = TypeVar("T", bound="TreatyCommittees")


@_attrs_define
class TreatyCommittees:
    """
    Attributes:
        treaty_committees (Union[Unset, list['TreatyCommittee']]):
    """

    treaty_committees: Union[Unset, list["TreatyCommittee"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        treaty_committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.treaty_committees, Unset):
            treaty_committees = []
            for treaty_committees_item_data in self.treaty_committees:
                treaty_committees_item = treaty_committees_item_data.to_dict()
                treaty_committees.append(treaty_committees_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if treaty_committees is not UNSET:
            field_dict["treatyCommittees"] = treaty_committees

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_committee import TreatyCommittee

        d = dict(src_dict)
        treaty_committees = []
        _treaty_committees = d.pop("treatyCommittees", UNSET)
        for treaty_committees_item_data in _treaty_committees or []:
            treaty_committees_item = TreatyCommittee.from_dict(treaty_committees_item_data)

            treaty_committees.append(treaty_committees_item)

        treaty_committees = cls(
            treaty_committees=treaty_committees,
        )

        treaty_committees.additional_properties = d
        return treaty_committees

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
