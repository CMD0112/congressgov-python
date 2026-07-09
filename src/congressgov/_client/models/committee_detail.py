import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.committee_detail_bills import CommitteeDetailBills
    from ..models.committee_detail_communications import CommitteeDetailCommunications
    from ..models.committee_detail_reports import CommitteeDetailReports
    from ..models.committee_history import CommitteeHistory
    from ..models.subcommittees import Subcommittees


T = TypeVar("T", bound="CommitteeDetail")


@_attrs_define
class CommitteeDetail:
    """
    Attributes:
        bills (Union[Unset, CommitteeDetailBills]):
        communications (Union[Unset, CommitteeDetailCommunications]):
        history (Union[Unset, list['CommitteeHistory']]):
        is_current (Union[Unset, bool]):  Example: True.
        reports (Union[Unset, CommitteeDetailReports]):
        subcommittees (Union[Unset, list['Subcommittees']]):
        system_code (Union[Unset, str]):  Example: hspw00.
        type_ (Union[Unset, str]):  Example: Standing.
        update_date (Union[Unset, datetime.datetime]):  Example: 2020-02-04T00:07:37Z.
    """

    bills: Union[Unset, "CommitteeDetailBills"] = UNSET
    communications: Union[Unset, "CommitteeDetailCommunications"] = UNSET
    history: Union[Unset, list["CommitteeHistory"]] = UNSET
    is_current: Union[Unset, bool] = UNSET
    reports: Union[Unset, "CommitteeDetailReports"] = UNSET
    subcommittees: Union[Unset, list["Subcommittees"]] = UNSET
    system_code: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bills: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.bills, Unset):
            bills = self.bills.to_dict()

        communications: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.communications, Unset):
            communications = self.communications.to_dict()

        history: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.history, Unset):
            history = []
            for history_item_data in self.history:
                history_item = history_item_data.to_dict()
                history.append(history_item)

        is_current = self.is_current

        reports: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.reports, Unset):
            reports = self.reports.to_dict()

        subcommittees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subcommittees, Unset):
            subcommittees = []
            for subcommittees_item_data in self.subcommittees:
                subcommittees_item = subcommittees_item_data.to_dict()
                subcommittees.append(subcommittees_item)

        system_code = self.system_code

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bills is not UNSET:
            field_dict["bills"] = bills
        if communications is not UNSET:
            field_dict["communications"] = communications
        if history is not UNSET:
            field_dict["history"] = history
        if is_current is not UNSET:
            field_dict["isCurrent"] = is_current
        if reports is not UNSET:
            field_dict["reports"] = reports
        if subcommittees is not UNSET:
            field_dict["subcommittees"] = subcommittees
        if system_code is not UNSET:
            field_dict["systemCode"] = system_code
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.committee_detail_bills import CommitteeDetailBills
        from ..models.committee_detail_communications import CommitteeDetailCommunications
        from ..models.committee_detail_reports import CommitteeDetailReports
        from ..models.committee_history import CommitteeHistory
        from ..models.subcommittees import Subcommittees

        d = dict(src_dict)
        _bills = d.pop("bills", UNSET)
        bills: Union[Unset, CommitteeDetailBills]
        if isinstance(_bills, Unset):
            bills = UNSET
        else:
            bills = CommitteeDetailBills.from_dict(_bills)

        _communications = d.pop("communications", UNSET)
        communications: Union[Unset, CommitteeDetailCommunications]
        if isinstance(_communications, Unset):
            communications = UNSET
        else:
            communications = CommitteeDetailCommunications.from_dict(_communications)

        history = []
        _history = d.pop("history", UNSET)
        for history_item_data in _history or []:
            history_item = CommitteeHistory.from_dict(history_item_data)

            history.append(history_item)

        is_current = d.pop("isCurrent", UNSET)

        _reports = d.pop("reports", UNSET)
        reports: Union[Unset, CommitteeDetailReports]
        if isinstance(_reports, Unset):
            reports = UNSET
        else:
            reports = CommitteeDetailReports.from_dict(_reports)

        subcommittees = []
        _subcommittees = d.pop("subcommittees", UNSET)
        for subcommittees_item_data in _subcommittees or []:
            subcommittees_item = Subcommittees.from_dict(subcommittees_item_data)

            subcommittees.append(subcommittees_item)

        system_code = d.pop("systemCode", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        committee_detail = cls(
            bills=bills,
            communications=communications,
            history=history,
            is_current=is_current,
            reports=reports,
            subcommittees=subcommittees,
            system_code=system_code,
            type_=type_,
            update_date=update_date,
        )

        committee_detail.additional_properties = d
        return committee_detail

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
