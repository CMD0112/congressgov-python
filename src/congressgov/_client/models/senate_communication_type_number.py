import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.senate_communication_type_number_committees_item import SenateCommunicationTypeNumberCommitteesItem


T = TypeVar("T", bound="SenateCommunicationTypeNumber")


@_attrs_define
class SenateCommunicationTypeNumber:
    """
    Attributes:
        abstract (Union[Unset, str]):  Example: A letter from the Director, Regulatory Management Division,
            Environmental Protection Agency, transmitting the Agency's request for applications - Technical Assistance to
            Brownfields Communities [EPA-I-OLEM-OBLR-22-12] received February 9, 2024, pursuant to 5 U.S.C. 801(a)(1)(A);
            Public Law 104–121, section 251; (110 Stat. 868); to the Committee on Energy and Commerce..
        chamber (Union[Unset, str]):  Example: House.
        committees (Union[Unset, list['SenateCommunicationTypeNumberCommitteesItem']]):
        congress (Union[Unset, int]):  Example: 118.
        congressional_record_date (Union[Unset, datetime.date]):  Example: 2024-03-07.
        number (Union[Unset, int]):  Example: 3324.
        session_number (Union[Unset, int]):  Example: 2.
        update_date (Union[Unset, datetime.date]):  Example: 2024-09-03.
    """

    abstract: Union[Unset, str] = UNSET
    chamber: Union[Unset, str] = UNSET
    committees: Union[Unset, list["SenateCommunicationTypeNumberCommitteesItem"]] = UNSET
    congress: Union[Unset, int] = UNSET
    congressional_record_date: Union[Unset, datetime.date] = UNSET
    number: Union[Unset, int] = UNSET
    session_number: Union[Unset, int] = UNSET
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

        congress = self.congress

        congressional_record_date: Union[Unset, str] = UNSET
        if not isinstance(self.congressional_record_date, Unset):
            congressional_record_date = self.congressional_record_date.isoformat()

        number = self.number

        session_number = self.session_number

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
        if congress is not UNSET:
            field_dict["congress"] = congress
        if congressional_record_date is not UNSET:
            field_dict["congressionalRecordDate"] = congressional_record_date
        if number is not UNSET:
            field_dict["number"] = number
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.senate_communication_type_number_committees_item import (
            SenateCommunicationTypeNumberCommitteesItem,
        )

        d = dict(src_dict)
        abstract = d.pop("abstract", UNSET)

        chamber = d.pop("chamber", UNSET)

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = SenateCommunicationTypeNumberCommitteesItem.from_dict(committees_item_data)

            committees.append(committees_item)

        congress = d.pop("congress", UNSET)

        _congressional_record_date = d.pop("congressionalRecordDate", UNSET)
        congressional_record_date: Union[Unset, datetime.date]
        if isinstance(_congressional_record_date, Unset) or _congressional_record_date is None:
            congressional_record_date = UNSET
        else:
            congressional_record_date = isoparse(_congressional_record_date)

        number = d.pop("number", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        senate_communication_type_number = cls(
            abstract=abstract,
            chamber=chamber,
            committees=committees,
            congress=congress,
            congressional_record_date=congressional_record_date,
            number=number,
            session_number=session_number,
            update_date=update_date,
        )

        senate_communication_type_number.additional_properties = d
        return senate_communication_type_number

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
