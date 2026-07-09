import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteeHistory")


@_attrs_define
class CommitteeHistory:
    """
    Attributes:
        library_of_congress_name (Union[Unset, str]):  Example: Transportation and Infrastructure.
        official_name (Union[Unset, str]):  Example: Committee on Transportation and Infrastructure.
        start_date (Union[Unset, datetime.datetime]):  Example: 1995-01-04T05:00:00Z.
        update_date (Union[Unset, datetime.datetime]):  Example: 2020-02-04T00:07:37Z.
        end_date (Union[Unset, datetime.datetime]):  Example: 2020-03-04T05:00:00Z.
    """

    library_of_congress_name: Union[Unset, str] = UNSET
    official_name: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        library_of_congress_name = self.library_of_congress_name

        official_name = self.official_name

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if library_of_congress_name is not UNSET:
            field_dict["libraryOfCongressName"] = library_of_congress_name
        if official_name is not UNSET:
            field_dict["officialName"] = official_name
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        library_of_congress_name = d.pop("libraryOfCongressName", UNSET)

        official_name = d.pop("officialName", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset) or _start_date is None:
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset) or _end_date is None:
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        committee_history = cls(
            library_of_congress_name=library_of_congress_name,
            official_name=official_name,
            start_date=start_date,
            update_date=update_date,
            end_date=end_date,
        )

        committee_history.additional_properties = d
        return committee_history

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
