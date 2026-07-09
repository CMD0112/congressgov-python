from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nomination_nomination import NominationNomination


T = TypeVar("T", bound="Nomination")


@_attrs_define
class Nomination:
    """
    Attributes:
        nomination (Union[Unset, NominationNomination]):
    """

    nomination: Union[Unset, "NominationNomination"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nomination: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.nomination, Unset):
            nomination = self.nomination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nomination is not UNSET:
            field_dict["nomination"] = nomination

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nomination_nomination import NominationNomination

        d = dict(src_dict)
        _nomination = d.pop("nomination", UNSET)
        nomination: Union[Unset, NominationNomination]
        if isinstance(_nomination, Unset):
            nomination = UNSET
        else:
            nomination = NominationNomination.from_dict(_nomination)

        nomination = cls(
            nomination=nomination,
        )

        nomination.additional_properties = d
        return nomination

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
