from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nomination_item import NominationItem


T = TypeVar("T", bound="Nominations")


@_attrs_define
class Nominations:
    """
    Attributes:
        nominations (Union[Unset, list['NominationItem']]):
    """

    nominations: Union[Unset, list["NominationItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nominations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nominations, Unset):
            nominations = []
            for nominations_item_data in self.nominations:
                nominations_item = nominations_item_data.to_dict()
                nominations.append(nominations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nominations is not UNSET:
            field_dict["nominations"] = nominations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nomination_item import NominationItem

        d = dict(src_dict)
        nominations = []
        _nominations = d.pop("nominations", UNSET)
        for nominations_item_data in _nominations or []:
            nominations_item = NominationItem.from_dict(nominations_item_data)

            nominations.append(nominations_item)

        nominations = cls(
            nominations=nominations,
        )

        nominations.additional_properties = d
        return nominations

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
