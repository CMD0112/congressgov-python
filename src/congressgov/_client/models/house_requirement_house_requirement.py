import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.match_communication import MatchCommunication


T = TypeVar("T", bound="HouseRequirementHouseRequirement")


@_attrs_define
class HouseRequirementHouseRequirement:
    """
    Attributes:
        active_record (Union[Unset, bool]):  Example: True.
        frequency (Union[Unset, str]):  Example: [No deadline specified]..
        legal_authority (Union[Unset, str]):  Example: 5 U.S.C. 801(a)(1)(A); Public Law 104–121, section 251; (110
            Stat. 868).
        matching_communications (Union[Unset, MatchCommunication]):
        nature (Union[Unset, str]):  Example: Congressional review of agency rulemaking..
        number (Union[Unset, int]):  Example: 8070.
        parent_agency (Union[Unset, str]):  Example: Multiple Executive Agencies and Departments.
        submitting_agency (Union[Unset, str]):  Example: Multiple Executive Agencies and Departments.
        update_date (Union[Unset, datetime.date]):  Example: 2021-08-13.
    """

    active_record: Union[Unset, bool] = UNSET
    frequency: Union[Unset, str] = UNSET
    legal_authority: Union[Unset, str] = UNSET
    matching_communications: Union[Unset, "MatchCommunication"] = UNSET
    nature: Union[Unset, str] = UNSET
    number: Union[Unset, int] = UNSET
    parent_agency: Union[Unset, str] = UNSET
    submitting_agency: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active_record = self.active_record

        frequency = self.frequency

        legal_authority = self.legal_authority

        matching_communications: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.matching_communications, Unset):
            matching_communications = self.matching_communications.to_dict()

        nature = self.nature

        number = self.number

        parent_agency = self.parent_agency

        submitting_agency = self.submitting_agency

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active_record is not UNSET:
            field_dict["activeRecord"] = active_record
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if legal_authority is not UNSET:
            field_dict["legalAuthority"] = legal_authority
        if matching_communications is not UNSET:
            field_dict["matchingCommunications"] = matching_communications
        if nature is not UNSET:
            field_dict["nature"] = nature
        if number is not UNSET:
            field_dict["number"] = number
        if parent_agency is not UNSET:
            field_dict["parentAgency"] = parent_agency
        if submitting_agency is not UNSET:
            field_dict["submittingAgency"] = submitting_agency
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.match_communication import MatchCommunication

        d = dict(src_dict)
        active_record = d.pop("activeRecord", UNSET)

        frequency = d.pop("frequency", UNSET)

        legal_authority = d.pop("legalAuthority", UNSET)

        _matching_communications = d.pop("matchingCommunications", UNSET)
        matching_communications: Union[Unset, MatchCommunication]
        if isinstance(_matching_communications, Unset):
            matching_communications = UNSET
        else:
            matching_communications = MatchCommunication.from_dict(_matching_communications)

        nature = d.pop("nature", UNSET)

        number = d.pop("number", UNSET)

        parent_agency = d.pop("parentAgency", UNSET)

        submitting_agency = d.pop("submittingAgency", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        house_requirement_house_requirement = cls(
            active_record=active_record,
            frequency=frequency,
            legal_authority=legal_authority,
            matching_communications=matching_communications,
            nature=nature,
            number=number,
            parent_agency=parent_agency,
            submitting_agency=submitting_agency,
            update_date=update_date,
        )

        house_requirement_house_requirement.additional_properties = d
        return house_requirement_house_requirement

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
