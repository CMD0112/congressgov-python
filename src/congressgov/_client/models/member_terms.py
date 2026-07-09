from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MemberTerms")


@_attrs_define
class MemberTerms:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House of Representatives.
        start_year (Union[Unset, int]):  Example: 1991.
    """

    chamber: Union[Unset, str] = UNSET
    start_year: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        start_year = self.start_year

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if start_year is not UNSET:
            field_dict["startYear"] = start_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        start_year = d.pop("startYear", UNSET)

        member_terms = cls(
            chamber=chamber,
            start_year=start_year,
        )

        member_terms.additional_properties = d
        return member_terms

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
