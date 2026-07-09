import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.communication_type import CommunicationType
    from ..models.house_communication_type_number_committees_item import HouseCommunicationTypeNumberCommitteesItem
    from ..models.house_communication_type_number_matching_requirements_item import (
        HouseCommunicationTypeNumberMatchingRequirementsItem,
    )


T = TypeVar("T", bound="HouseCommunicationTypeNumber")


@_attrs_define
class HouseCommunicationTypeNumber:
    """
    Attributes:
        abstract (Union[Unset, str]):  Example: A letter from the Director, Regulatory Management Division,
            Environmental Protection Agency, transmitting the Agency's request for applications - Technical Assistance to
            Brownfields Communities [EPA-I-OLEM-OBLR-22-12] received February 9, 2024, pursuant to 5 U.S.C. 801(a)(1)(A);
            Public Law 104–121, section 251; (110 Stat. 868); to the Committee on Energy and Commerce..
        chamber (Union[Unset, str]):  Example: House.
        committees (Union[Unset, list['HouseCommunicationTypeNumberCommitteesItem']]):
        communication_type (Union[Unset, CommunicationType]):
        congress (Union[Unset, int]):  Example: 118.
        congressional_record_date (Union[Unset, datetime.date]):  Example: 2024-03-07.
        is_rulemaking (Union[Unset, str]):  Example: True.
        legal_authority (Union[Unset, str]):  Example: 5 U.S.C. 801(a)(1)(A); Public Law 104–121, section 251; (110
            Stat. 868).
        matching_requirements (Union[Unset, list['HouseCommunicationTypeNumberMatchingRequirementsItem']]):
        number (Union[Unset, int]):  Example: 3324.
        report_nature (Union[Unset, str]):  Example: The Agency's request for applications - Technical Assistance to
            Brownfields Communities [EPA-I-OLEM-OBLR-22-12] received February 9, 2024..
        session_number (Union[Unset, int]):  Example: 2.
        submitting_agency (Union[Unset, str]):  Example: Environmental Protection Agency.
        submitting_official (Union[Unset, str]):  Example: Director, Regulatory Management Division.
        update_date (Union[Unset, datetime.date]):  Example: 2024-09-03.
    """

    abstract: Union[Unset, str] = UNSET
    chamber: Union[Unset, str] = UNSET
    committees: Union[Unset, list["HouseCommunicationTypeNumberCommitteesItem"]] = UNSET
    communication_type: Union[Unset, "CommunicationType"] = UNSET
    congress: Union[Unset, int] = UNSET
    congressional_record_date: Union[Unset, datetime.date] = UNSET
    is_rulemaking: Union[Unset, str] = UNSET
    legal_authority: Union[Unset, str] = UNSET
    matching_requirements: Union[Unset, list["HouseCommunicationTypeNumberMatchingRequirementsItem"]] = UNSET
    number: Union[Unset, int] = UNSET
    report_nature: Union[Unset, str] = UNSET
    session_number: Union[Unset, int] = UNSET
    submitting_agency: Union[Unset, str] = UNSET
    submitting_official: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        abstract = self.abstract

        chamber = self.chamber

        committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = []
            for committees_item_data in self.committees:
                committees_item = committees_item_data.to_dict()
                committees.append(committees_item)

        communication_type: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.communication_type, Unset):
            communication_type = self.communication_type.to_dict()

        congress = self.congress

        congressional_record_date: Union[Unset, str] = UNSET
        if not isinstance(self.congressional_record_date, Unset):
            congressional_record_date = self.congressional_record_date.isoformat()

        is_rulemaking = self.is_rulemaking

        legal_authority = self.legal_authority

        matching_requirements: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.matching_requirements, Unset):
            matching_requirements = []
            for matching_requirements_item_data in self.matching_requirements:
                matching_requirements_item = matching_requirements_item_data.to_dict()
                matching_requirements.append(matching_requirements_item)

        number = self.number

        report_nature = self.report_nature

        session_number = self.session_number

        submitting_agency = self.submitting_agency

        submitting_official = self.submitting_official

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abstract is not UNSET:
            field_dict["abstract"] = abstract
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if committees is not UNSET:
            field_dict["committees"] = committees
        if communication_type is not UNSET:
            field_dict["communicationType"] = communication_type
        if congress is not UNSET:
            field_dict["congress"] = congress
        if congressional_record_date is not UNSET:
            field_dict["congressionalRecordDate"] = congressional_record_date
        if is_rulemaking is not UNSET:
            field_dict["isRulemaking"] = is_rulemaking
        if legal_authority is not UNSET:
            field_dict["legalAuthority"] = legal_authority
        if matching_requirements is not UNSET:
            field_dict["matchingRequirements"] = matching_requirements
        if number is not UNSET:
            field_dict["number"] = number
        if report_nature is not UNSET:
            field_dict["reportNature"] = report_nature
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if submitting_agency is not UNSET:
            field_dict["submittingAgency"] = submitting_agency
        if submitting_official is not UNSET:
            field_dict["submittingOfficial"] = submitting_official
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.communication_type import CommunicationType
        from ..models.house_communication_type_number_committees_item import HouseCommunicationTypeNumberCommitteesItem
        from ..models.house_communication_type_number_matching_requirements_item import (
            HouseCommunicationTypeNumberMatchingRequirementsItem,
        )

        d = dict(src_dict)
        abstract = d.pop("abstract", UNSET)

        chamber = d.pop("chamber", UNSET)

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = HouseCommunicationTypeNumberCommitteesItem.from_dict(committees_item_data)

            committees.append(committees_item)

        _communication_type = d.pop("communicationType", UNSET)
        communication_type: Union[Unset, CommunicationType]
        if isinstance(_communication_type, Unset):
            communication_type = UNSET
        else:
            communication_type = CommunicationType.from_dict(_communication_type)

        congress = d.pop("congress", UNSET)

        _congressional_record_date = d.pop("congressionalRecordDate", UNSET)
        congressional_record_date: Union[Unset, datetime.date]
        if isinstance(_congressional_record_date, Unset) or _congressional_record_date is None:
            congressional_record_date = UNSET
        else:
            congressional_record_date = isoparse(_congressional_record_date)

        is_rulemaking = d.pop("isRulemaking", UNSET)

        legal_authority = d.pop("legalAuthority", UNSET)

        matching_requirements = []
        _matching_requirements = d.pop("matchingRequirements", UNSET)
        for matching_requirements_item_data in _matching_requirements or []:
            matching_requirements_item = HouseCommunicationTypeNumberMatchingRequirementsItem.from_dict(
                matching_requirements_item_data
            )

            matching_requirements.append(matching_requirements_item)

        number = d.pop("number", UNSET)

        report_nature = d.pop("reportNature", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        submitting_agency = d.pop("submittingAgency", UNSET)

        submitting_official = d.pop("submittingOfficial", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        house_communication_type_number = cls(
            abstract=abstract,
            chamber=chamber,
            committees=committees,
            communication_type=communication_type,
            congress=congress,
            congressional_record_date=congressional_record_date,
            is_rulemaking=is_rulemaking,
            legal_authority=legal_authority,
            matching_requirements=matching_requirements,
            number=number,
            report_nature=report_nature,
            session_number=session_number,
            submitting_agency=submitting_agency,
            submitting_official=submitting_official,
            update_date=update_date,
        )

        house_communication_type_number.additional_properties = d
        return house_communication_type_number

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
