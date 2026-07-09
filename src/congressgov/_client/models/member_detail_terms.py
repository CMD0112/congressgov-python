from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MemberDetailTerms")


@_attrs_define
class MemberDetailTerms:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: Senate.
        congress (Union[Unset, int]):  Example: 116.
        end_year (Union[Unset, int]):  Example: 2021.
        member_type (Union[Unset, str]):  Example: Senator.
        start_year (Union[Unset, int]):  Example: 2019.
        state_code (Union[Unset, str]):  Example: VT.
        state_name (Union[Unset, str]):  Example: Vermont.
    """

    chamber: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    end_year: Union[Unset, int] = UNSET
    member_type: Union[Unset, str] = UNSET
    start_year: Union[Unset, int] = UNSET
    state_code: Union[Unset, str] = UNSET
    state_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        congress = self.congress

        end_year = self.end_year

        member_type = self.member_type

        start_year = self.start_year

        state_code = self.state_code

        state_name = self.state_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if congress is not UNSET:
            field_dict["congress"] = congress
        if end_year is not UNSET:
            field_dict["endYear"] = end_year
        if member_type is not UNSET:
            field_dict["memberType"] = member_type
        if start_year is not UNSET:
            field_dict["startYear"] = start_year
        if state_code is not UNSET:
            field_dict["stateCode"] = state_code
        if state_name is not UNSET:
            field_dict["stateName"] = state_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        congress = d.pop("congress", UNSET)

        end_year = d.pop("endYear", UNSET)

        member_type = d.pop("memberType", UNSET)

        start_year = d.pop("startYear", UNSET)

        state_code = d.pop("stateCode", UNSET)

        state_name = d.pop("stateName", UNSET)

        member_detail_terms = cls(
            chamber=chamber,
            congress=congress,
            end_year=end_year,
            member_type=member_type,
            start_year=start_year,
            state_code=state_code,
            state_name=state_name,
        )

        member_detail_terms.additional_properties = d
        return member_detail_terms

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
