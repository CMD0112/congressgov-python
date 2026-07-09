import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BoundCongressionalRecordItem")


@_attrs_define
class BoundCongressionalRecordItem:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 101.
        date (Union[Unset, str]):  Example: 1990-05-01.
        session_number (Union[Unset, int]):  Example: 2.
        update_date (Union[Unset, datetime.date]):  Example: 2020-10-20.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bound-congressional-record/1990/5/1?format=json.
        volume_number (Union[Unset, int]):  Example: 136.
    """

    congress: Union[Unset, int] = UNSET
    date: Union[Unset, str] = UNSET
    session_number: Union[Unset, int] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    url: Union[Unset, str] = UNSET
    volume_number: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        date = self.date

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
        if date is not UNSET:
            field_dict["date"] = date
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

        date = d.pop("date", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        volume_number = d.pop("volumeNumber", UNSET)

        bound_congressional_record_item = cls(
            congress=congress,
            date=date,
            session_number=session_number,
            update_date=update_date,
            url=url,
            volume_number=volume_number,
        )

        bound_congressional_record_item.additional_properties = d
        return bound_congressional_record_item

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
