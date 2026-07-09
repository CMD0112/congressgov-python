from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_detail_treaty import TreatyDetailTreaty


T = TypeVar("T", bound="TreatyDetail")


@_attrs_define
class TreatyDetail:
    """
    Attributes:
        treaty (Union[Unset, TreatyDetailTreaty]):
    """

    treaty: Union[Unset, "TreatyDetailTreaty"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        treaty: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.treaty, Unset):
            treaty = self.treaty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if treaty is not UNSET:
            field_dict["treaty"] = treaty

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_detail_treaty import TreatyDetailTreaty

        d = dict(src_dict)
        _treaty = d.pop("treaty", UNSET)
        treaty: Union[Unset, TreatyDetailTreaty]
        if isinstance(_treaty, Unset):
            treaty = UNSET
        else:
            treaty = TreatyDetailTreaty.from_dict(_treaty)

        treaty_detail = cls(
            treaty=treaty,
        )

        treaty_detail.additional_properties = d
        return treaty_detail

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
