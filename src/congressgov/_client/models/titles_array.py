import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TitlesArray")


@_attrs_define
class TitlesArray:
    """
    Attributes:
        title (Union[Unset, str]):  Example: A bill to amend the Health and Human Services Act of 1968 to provide for
            the establishment of a national health care system..
        update_date (Union[Unset, datetime.date]):  Example: 2022-02-18T16:38:41Z.
        title_type (Union[Unset, str]):  Example: Display Title.
        title_type_code (Union[Unset, int]):  Example: 45.
        bill_text_version_code (Union[Unset, str]):  Example: RH.
        bill_text_version_name (Union[Unset, str]):  Example: Reported in House.
    """

    title: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    title_type: Union[Unset, str] = UNSET
    title_type_code: Union[Unset, int] = UNSET
    bill_text_version_code: Union[Unset, str] = UNSET
    bill_text_version_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        title_type = self.title_type

        title_type_code = self.title_type_code

        bill_text_version_code = self.bill_text_version_code

        bill_text_version_name = self.bill_text_version_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if title_type is not UNSET:
            field_dict["titleType"] = title_type
        if title_type_code is not UNSET:
            field_dict["titleTypeCode"] = title_type_code
        if bill_text_version_code is not UNSET:
            field_dict["billTextVersionCode"] = bill_text_version_code
        if bill_text_version_name is not UNSET:
            field_dict["billTextVersionName"] = bill_text_version_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        title_type = d.pop("titleType", UNSET)

        title_type_code = d.pop("titleTypeCode", UNSET)

        bill_text_version_code = d.pop("billTextVersionCode", UNSET)

        bill_text_version_name = d.pop("billTextVersionName", UNSET)

        titles_array = cls(
            title=title,
            update_date=update_date,
            title_type=title_type,
            title_type_code=title_type_code,
            bill_text_version_code=bill_text_version_code,
            bill_text_version_name=bill_text_version_name,
        )

        titles_array.additional_properties = d
        return titles_array

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
