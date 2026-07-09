import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.associated_bill import AssociatedBill
    from ..models.committee_reports_number_item_text import CommitteeReportsNumberItemText


T = TypeVar("T", bound="CommitteeReportsNumberItem")


@_attrs_define
class CommitteeReportsNumberItem:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        citation (Union[Unset, str]):  Example: H. Rept. 109-570.
        congress (Union[Unset, int]):  Example: 117.
        number (Union[Unset, int]):  Example: 570.
        part (Union[Unset, int]):  Example: 1.
        type_ (Union[Unset, str]):  Example: HRPT.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-02-18T16:38:41Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/117hr570?format=json.
        associated_bill (Union[Unset, list['AssociatedBill']]):
        is_conference_report (Union[Unset, bool]):  Example: True.
        issue_date (Union[Unset, datetime.datetime]):  Example: 2020-12-03T05:00:00Z.
        report_type (Union[Unset, str]):  Example: H.Rept..
        session_number (Union[Unset, int]):  Example: 2.
        text (Union[Unset, CommitteeReportsNumberItemText]):
        title (Union[Unset, str]):  Example: WILLIAM M. (MAC) THORNBERRY NATIONAL DEFENSE AUTHORIZATION ACT FOR FISCAL
            YEAR 2021.
    """

    chamber: Union[Unset, str] = UNSET
    citation: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    part: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    associated_bill: Union[Unset, list["AssociatedBill"]] = UNSET
    is_conference_report: Union[Unset, bool] = UNSET
    issue_date: Union[Unset, datetime.datetime] = UNSET
    report_type: Union[Unset, str] = UNSET
    session_number: Union[Unset, int] = UNSET
    text: Union[Unset, "CommitteeReportsNumberItemText"] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        citation = self.citation

        congress = self.congress

        number = self.number

        part = self.part

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        associated_bill: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.associated_bill, Unset):
            associated_bill = []
            for associated_bill_item_data in self.associated_bill:
                associated_bill_item = associated_bill_item_data.to_dict()
                associated_bill.append(associated_bill_item)

        is_conference_report = self.is_conference_report

        issue_date: Union[Unset, str] = UNSET
        if not isinstance(self.issue_date, Unset):
            issue_date = self.issue_date.isoformat()

        report_type = self.report_type

        session_number = self.session_number

        text: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.text, Unset):
            text = self.text.to_dict()

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if citation is not UNSET:
            field_dict["citation"] = citation
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if part is not UNSET:
            field_dict["part"] = part
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url
        if associated_bill is not UNSET:
            field_dict["associatedBill"] = associated_bill
        if is_conference_report is not UNSET:
            field_dict["isConferenceReport"] = is_conference_report
        if issue_date is not UNSET:
            field_dict["issueDate"] = issue_date
        if report_type is not UNSET:
            field_dict["reportType"] = report_type
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if text is not UNSET:
            field_dict["text"] = text
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.associated_bill import AssociatedBill
        from ..models.committee_reports_number_item_text import CommitteeReportsNumberItemText

        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        citation = d.pop("citation", UNSET)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        part = d.pop("part", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        associated_bill = []
        _associated_bill = d.pop("associatedBill", UNSET)
        for associated_bill_item_data in _associated_bill or []:
            associated_bill_item = AssociatedBill.from_dict(associated_bill_item_data)

            associated_bill.append(associated_bill_item)

        is_conference_report = d.pop("isConferenceReport", UNSET)

        _issue_date = d.pop("issueDate", UNSET)
        issue_date: Union[Unset, datetime.datetime]
        if isinstance(_issue_date, Unset) or _issue_date is None:
            issue_date = UNSET
        else:
            issue_date = isoparse(_issue_date)

        report_type = d.pop("reportType", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        _text = d.pop("text", UNSET)
        text: Union[Unset, CommitteeReportsNumberItemText]
        if isinstance(_text, Unset):
            text = UNSET
        else:
            text = CommitteeReportsNumberItemText.from_dict(_text)

        title = d.pop("title", UNSET)

        committee_reports_number_item = cls(
            chamber=chamber,
            citation=citation,
            congress=congress,
            number=number,
            part=part,
            type_=type_,
            update_date=update_date,
            url=url,
            associated_bill=associated_bill,
            is_conference_report=is_conference_report,
            issue_date=issue_date,
            report_type=report_type,
            session_number=session_number,
            text=text,
            title=title,
        )

        committee_reports_number_item.additional_properties = d
        return committee_reports_number_item

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
