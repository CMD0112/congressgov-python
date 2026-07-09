import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteeMeetings")


@_attrs_define
class CommitteeMeetings:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        congress (Union[Unset, int]):  Example: 117.
        eventid (Union[Unset, str]):  Example: 115522.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-08-01 21:19:33+00:00.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee-meeting/118/house/115522?format=json.
    """

    chamber: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    eventid: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        congress = self.congress

        eventid = self.eventid

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if congress is not UNSET:
            field_dict["congress"] = congress
        if eventid is not UNSET:
            field_dict["eventid"] = eventid
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        congress = d.pop("congress", UNSET)

        eventid = d.pop("eventid", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        committee_meetings = cls(
            chamber=chamber,
            congress=congress,
            eventid=eventid,
            update_date=update_date,
            url=url,
        )

        committee_meetings.additional_properties = d
        return committee_meetings

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
