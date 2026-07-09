import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BillSummariesArray")


@_attrs_define
class BillSummariesArray:
    """
    Attributes:
        action_date (Union[Unset, datetime.date]):  Example: 2022-02-18T16:38:41Z.
        action_desc (Union[Unset, str]):  Example: Passed Senate.
        text (Union[Unset, str]):  Example: <p><strong>COVID-19 Medical Production Act</strong></p> <p>This bill
            provides additional funding for FY2021 to acquire medical supplies, vaccines, and other equipment to combat
            COVID-19 (i.e., coronavirus disease 2019) using authorities under the Defense Production Act of 1950. That act
            confers on the President a broad set of authorities to influence domestic industry to provide essential
            materials and goods for the national defense.</p> <p>This funding is available through FY2025. Beginning in
            FY2023, it may be used to meet public health needs to address any pathogen determined by the President to have
            the potential to create a public health emergency.</p>.
        update_date (Union[Unset, datetime.date]):  Example: 2022-02-18T16:38:41Z.
        version_code (Union[Unset, str]):  Example: 173.
    """

    action_date: Union[Unset, datetime.date] = UNSET
    action_desc: Union[Unset, str] = UNSET
    text: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    version_code: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        action_desc = self.action_desc

        text = self.text

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        version_code = self.version_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if action_desc is not UNSET:
            field_dict["actionDesc"] = action_desc
        if text is not UNSET:
            field_dict["text"] = text
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if version_code is not UNSET:
            field_dict["versionCode"] = version_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _action_date = d.pop("actionDate", UNSET)
        action_date: Union[Unset, datetime.date]
        if isinstance(_action_date, Unset) or _action_date is None:
            action_date = UNSET
        else:
            action_date = isoparse(_action_date)

        action_desc = d.pop("actionDesc", UNSET)

        text = d.pop("text", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        version_code = d.pop("versionCode", UNSET)

        bill_summaries_array = cls(
            action_date=action_date,
            action_desc=action_desc,
            text=text,
            update_date=update_date,
            version_code=version_code,
        )

        bill_summaries_array.additional_properties = d
        return bill_summaries_array

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
