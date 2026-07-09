import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.associated_bill import AssociatedBill
    from ..models.committee_print_committees import CommitteePrintCommittees
    from ..models.committee_print_detail_text import CommitteePrintDetailText


T = TypeVar("T", bound="CommitteePrintDetail")


@_attrs_define
class CommitteePrintDetail:
    """
    Attributes:
        associated_bills (Union[Unset, list['AssociatedBill']]):
        chamber (Union[Unset, str]):  Example: House.
        citation (Union[Unset, str]):  Example: 117-62.
        committees (Union[Unset, list['CommitteePrintCommittees']]):
        congress (Union[Unset, int]):  Example: 117.
        jacket_number (Union[Unset, int]):  Example: 48144.
        text (Union[Unset, CommitteePrintDetailText]):
        number (Union[Unset, str]):  Example: 62.
        title (Union[Unset, str]):  Example: RULES COMMITTEE PRINT 117-62 TEXT OF H.R. 5768, VIOLENT INCIDENT CLEAR-
            ANCE AND TECHNOLOGICAL INVESTIGATIVE METHODS ACT OF 2022.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-08-01 21:19:33+00:00.
    """

    associated_bills: Union[Unset, list["AssociatedBill"]] = UNSET
    chamber: Union[Unset, str] = UNSET
    citation: Union[Unset, str] = UNSET
    committees: Union[Unset, list["CommitteePrintCommittees"]] = UNSET
    congress: Union[Unset, int] = UNSET
    jacket_number: Union[Unset, int] = UNSET
    text: Union[Unset, "CommitteePrintDetailText"] = UNSET
    number: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        associated_bills: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.associated_bills, Unset):
            associated_bills = []
            for associated_bills_item_data in self.associated_bills:
                associated_bills_item = associated_bills_item_data.to_dict()
                associated_bills.append(associated_bills_item)

        chamber = self.chamber

        citation = self.citation

        committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = []
            for committees_item_data in self.committees:
                committees_item = committees_item_data.to_dict()
                committees.append(committees_item)

        congress = self.congress

        jacket_number = self.jacket_number

        text: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.text, Unset):
            text = self.text.to_dict()

        number = self.number

        title = self.title

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if associated_bills is not UNSET:
            field_dict["associatedBills"] = associated_bills
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if citation is not UNSET:
            field_dict["citation"] = citation
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if jacket_number is not UNSET:
            field_dict["jacketNumber"] = jacket_number
        if text is not UNSET:
            field_dict["text"] = text
        if number is not UNSET:
            field_dict["number"] = number
        if title is not UNSET:
            field_dict["title"] = title
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.associated_bill import AssociatedBill
        from ..models.committee_print_committees import CommitteePrintCommittees
        from ..models.committee_print_detail_text import CommitteePrintDetailText

        d = dict(src_dict)
        associated_bills = []
        _associated_bills = d.pop("associatedBills", UNSET)
        for associated_bills_item_data in _associated_bills or []:
            associated_bills_item = AssociatedBill.from_dict(associated_bills_item_data)

            associated_bills.append(associated_bills_item)

        chamber = d.pop("chamber", UNSET)

        citation = d.pop("citation", UNSET)

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = CommitteePrintCommittees.from_dict(committees_item_data)

            committees.append(committees_item)

        congress = d.pop("congress", UNSET)

        jacket_number = d.pop("jacketNumber", UNSET)

        _text = d.pop("text", UNSET)
        text: Union[Unset, CommitteePrintDetailText]
        if isinstance(_text, Unset):
            text = UNSET
        else:
            text = CommitteePrintDetailText.from_dict(_text)

        number = d.pop("number", UNSET)

        title = d.pop("title", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        committee_print_detail = cls(
            associated_bills=associated_bills,
            chamber=chamber,
            citation=citation,
            committees=committees,
            congress=congress,
            jacket_number=jacket_number,
            text=text,
            number=number,
            title=title,
            update_date=update_date,
        )

        committee_print_detail.additional_properties = d
        return committee_print_detail

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
