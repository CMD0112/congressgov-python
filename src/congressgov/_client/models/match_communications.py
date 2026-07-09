from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.match_communications_item import MatchCommunicationsItem


T = TypeVar("T", bound="MatchCommunications")


@_attrs_define
class MatchCommunications:
    """
    Attributes:
        match_communications (Union[Unset, list['MatchCommunicationsItem']]):
    """

    match_communications: Union[Unset, list["MatchCommunicationsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        match_communications: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.match_communications, Unset):
            match_communications = []
            for match_communications_item_data in self.match_communications:
                match_communications_item = match_communications_item_data.to_dict()
                match_communications.append(match_communications_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match_communications is not UNSET:
            field_dict["matchCommunications"] = match_communications

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.match_communications_item import MatchCommunicationsItem

        d = dict(src_dict)
        match_communications = []
        _match_communications = d.pop("matchCommunications", UNSET)
        for match_communications_item_data in _match_communications or []:
            match_communications_item = MatchCommunicationsItem.from_dict(match_communications_item_data)

            match_communications.append(match_communications_item)

        match_communications = cls(
            match_communications=match_communications,
        )

        match_communications.additional_properties = d
        return match_communications

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
