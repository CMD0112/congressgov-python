from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nominee import Nominee


T = TypeVar("T", bound="NominationNominee")


@_attrs_define
class NominationNominee:
    """
    Attributes:
        nominees (Union[Unset, list['Nominee']]):
    """

    nominees: Union[Unset, list["Nominee"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nominees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nominees, Unset):
            nominees = []
            for nominees_item_data in self.nominees:
                nominees_item = nominees_item_data.to_dict()
                nominees.append(nominees_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nominees is not UNSET:
            field_dict["nominees"] = nominees

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nominee import Nominee

        d = dict(src_dict)
        nominees = []
        _nominees = d.pop("nominees", UNSET)
        for nominees_item_data in _nominees or []:
            nominees_item = Nominee.from_dict(nominees_item_data)

            nominees.append(nominees_item)

        nomination_nominee = cls(
            nominees=nominees,
        )

        nomination_nominee.additional_properties = d
        return nomination_nominee

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
