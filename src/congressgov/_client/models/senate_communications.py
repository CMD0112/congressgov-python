from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.senate_communication import SenateCommunication


T = TypeVar("T", bound="SenateCommunications")


@_attrs_define
class SenateCommunications:
    """
    Attributes:
        senate_coummunications (Union[Unset, list['SenateCommunication']]):
    """

    senate_coummunications: Union[Unset, list["SenateCommunication"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        senate_coummunications: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.senate_coummunications, Unset):
            senate_coummunications = []
            for senate_coummunications_item_data in self.senate_coummunications:
                senate_coummunications_item = senate_coummunications_item_data.to_dict()
                senate_coummunications.append(senate_coummunications_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if senate_coummunications is not UNSET:
            field_dict["senateCoummunications"] = senate_coummunications

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.senate_communication import SenateCommunication

        d = dict(src_dict)
        senate_coummunications = []
        _senate_coummunications = d.pop("senateCoummunications", UNSET)
        for senate_coummunications_item_data in _senate_coummunications or []:
            senate_coummunications_item = SenateCommunication.from_dict(senate_coummunications_item_data)

            senate_coummunications.append(senate_coummunications_item)

        senate_communications = cls(
            senate_coummunications=senate_coummunications,
        )

        senate_communications.additional_properties = d
        return senate_communications

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
