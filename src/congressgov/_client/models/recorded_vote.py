import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RecordedVote")


@_attrs_define
class RecordedVote:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: Senate.
        congress (Union[Unset, int]):  Example: 117.
        date (Union[Unset, datetime.datetime]):  Example: 2021-08-08T12:00:00Z.
        roll_number (Union[Unset, int]):  Example: 312.
        session_number (Union[Unset, int]):  Example: 1.
        url (Union[Unset, str]):  Example:
            https://www.senate.gov/legislative/LIS/roll_call_votes/vote1171/vote_117_1_00312.xml.
    """

    chamber: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET
    roll_number: Union[Unset, int] = UNSET
    session_number: Union[Unset, int] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        congress = self.congress

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        roll_number = self.roll_number

        session_number = self.session_number

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if congress is not UNSET:
            field_dict["congress"] = congress
        if date is not UNSET:
            field_dict["date"] = date
        if roll_number is not UNSET:
            field_dict["rollNumber"] = roll_number
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        congress = d.pop("congress", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset) or _date is None:
            date = UNSET
        else:
            date = isoparse(_date)

        roll_number = d.pop("rollNumber", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        url = d.pop("url", UNSET)

        recorded_vote = cls(
            chamber=chamber,
            congress=congress,
            date=date,
            roll_number=roll_number,
            session_number=session_number,
            url=url,
        )

        recorded_vote.additional_properties = d
        return recorded_vote

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
