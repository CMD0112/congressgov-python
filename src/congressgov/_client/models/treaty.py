from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_item import TreatyItem


T = TypeVar("T", bound="Treaty")


@_attrs_define
class Treaty:
    """
    Attributes:
        treaties (Union[Unset, list['TreatyItem']]):
    """

    treaties: Union[Unset, list["TreatyItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        treaties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.treaties, Unset):
            treaties = []
            for treaties_item_data in self.treaties:
                treaties_item = treaties_item_data.to_dict()
                treaties.append(treaties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if treaties is not UNSET:
            field_dict["treaties"] = treaties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_item import TreatyItem

        d = dict(src_dict)
        treaties = []
        _treaties = d.pop("treaties", UNSET)
        for treaties_item_data in _treaties or []:
            treaties_item = TreatyItem.from_dict(treaties_item_data)

            treaties.append(treaties_item)

        treaty = cls(
            treaties=treaties,
        )

        treaty.additional_properties = d
        return treaty

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
