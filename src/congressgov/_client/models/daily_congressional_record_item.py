import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DailyCongressionalRecordItem")


@_attrs_define
class DailyCongressionalRecordItem:
    """
    Attributes:
        congress (Union[Unset, str]):  Example: 118.
        issue_date (Union[Unset, datetime.datetime]):  Example: 2023-07-11T04:00:00Z.
        issue_number (Union[Unset, str]):  Example: 118.
        session_number (Union[Unset, str]):  Example: 1.
        update_date (Union[Unset, datetime.datetime]):  Example: 2023-07-12T11:30:30Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/daily-congressional-record/169/118?format=json.
        volume_number (Union[Unset, str]):  Example: 169.
    """

    congress: Union[Unset, str] = UNSET
    issue_date: Union[Unset, datetime.datetime] = UNSET
    issue_number: Union[Unset, str] = UNSET
    session_number: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    volume_number: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

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
        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

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

        daily_congressional_record_item = cls(
            congress=congress,
            issue_date=issue_date,
            issue_number=issue_number,
            session_number=session_number,
            update_date=update_date,
            url=url,
            volume_number=volume_number,
        )

        daily_congressional_record_item.additional_properties = d
        return daily_congressional_record_item

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
