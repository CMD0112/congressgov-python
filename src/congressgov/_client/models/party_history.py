from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartyHistory")


@_attrs_define
class PartyHistory:
    """
    Attributes:
        party_abbreviation (Union[Unset, str]):  Example: D.
        party_name (Union[Unset, str]):  Example: Democrat.
        start_year (Union[Unset, int]):  Example: 1975.
    """

    party_abbreviation: Union[Unset, str] = UNSET
    party_name: Union[Unset, str] = UNSET
    start_year: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        party_abbreviation = self.party_abbreviation

        party_name = self.party_name

        start_year = self.start_year

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if party_abbreviation is not UNSET:
            field_dict["partyAbbreviation"] = party_abbreviation
        if party_name is not UNSET:
            field_dict["partyName"] = party_name
        if start_year is not UNSET:
            field_dict["startYear"] = start_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        party_abbreviation = d.pop("partyAbbreviation", UNSET)

        party_name = d.pop("partyName", UNSET)

        start_year = d.pop("startYear", UNSET)

        party_history = cls(
            party_abbreviation=party_abbreviation,
            party_name=party_name,
            start_year=start_year,
        )

        party_history.additional_properties = d
        return party_history

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
