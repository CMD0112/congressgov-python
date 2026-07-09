import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.full_issue import FullIssue


T = TypeVar("T", bound="DailyCongressionalRecordIssueIssue")


@_attrs_define
class DailyCongressionalRecordIssueIssue:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 119.
        full_issue (Union[Unset, FullIssue]):
        issue_date (Union[Unset, datetime.datetime]):  Example: 2025-01-03T05:00:00Z.
        issue_number (Union[Unset, str]):  Example: 1.
        session_number (Union[Unset, int]):  Example: 1.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-01-04T16:59:21Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/daily-congressional-record/171/1?format=json.
        volume_number (Union[Unset, int]):  Example: 171.
    """

    congress: Union[Unset, int] = UNSET
    full_issue: Union[Unset, "FullIssue"] = UNSET
    issue_date: Union[Unset, datetime.datetime] = UNSET
    issue_number: Union[Unset, str] = UNSET
    session_number: Union[Unset, int] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    volume_number: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        full_issue: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.full_issue, Unset):
            full_issue = self.full_issue.to_dict()

        issue_date: Union[Unset, str] = UNSET
        if not isinstance(self.issue_date, Unset):
            issue_date = self.issue_date.isoformat()

        issue_number = self.issue_number

        session_number = self.session_number

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        volume_number = self.volume_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if full_issue is not UNSET:
            field_dict["fullIssue"] = full_issue
        if issue_date is not UNSET:
            field_dict["issueDate"] = issue_date
        if issue_number is not UNSET:
            field_dict["issueNumber"] = issue_number
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url
        if volume_number is not UNSET:
            field_dict["volumeNumber"] = volume_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.full_issue import FullIssue

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        _full_issue = d.pop("fullIssue", UNSET)
        full_issue: Union[Unset, FullIssue]
        if isinstance(_full_issue, Unset):
            full_issue = UNSET
        else:
            full_issue = FullIssue.from_dict(_full_issue)

        _issue_date = d.pop("issueDate", UNSET)
        issue_date: Union[Unset, datetime.datetime]
        if isinstance(_issue_date, Unset) or _issue_date is None:
            issue_date = UNSET
        else:
            issue_date = isoparse(_issue_date)

        issue_number = d.pop("issueNumber", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        volume_number = d.pop("volumeNumber", UNSET)

        daily_congressional_record_issue_issue = cls(
            congress=congress,
            full_issue=full_issue,
            issue_date=issue_date,
            issue_number=issue_number,
            session_number=session_number,
            update_date=update_date,
            url=url,
            volume_number=volume_number,
        )

        daily_congressional_record_issue_issue.additional_properties = d
        return daily_congressional_record_issue_issue

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
