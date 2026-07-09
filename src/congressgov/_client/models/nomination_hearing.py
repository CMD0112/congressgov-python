from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nomination_hearing_item import NominationHearingItem


T = TypeVar("T", bound="NominationHearing")


@_attrs_define
class NominationHearing:
    """
    Attributes:
        hearings (Union[Unset, list['NominationHearingItem']]):
    """

    hearings: Union[Unset, list["NominationHearingItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hearings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.hearings, Unset):
            hearings = []
            for hearings_item_data in self.hearings:
                hearings_item = hearings_item_data.to_dict()
                hearings.append(hearings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hearings is not UNSET:
            field_dict["hearings"] = hearings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nomination_hearing_item import NominationHearingItem

        d = dict(src_dict)
        hearings = []
        _hearings = d.pop("hearings", UNSET)
        for hearings_item_data in _hearings or []:
            hearings_item = NominationHearingItem.from_dict(hearings_item_data)

            hearings.append(hearings_item)

        nomination_hearing = cls(
            hearings=hearings,
        )

        nomination_hearing.additional_properties = d
        return nomination_hearing

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
