import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BillDetailLatestAction")


@_attrs_define
class BillDetailLatestAction:
    """
    Attributes:
        action_date (Union[Unset, datetime.date]):  Example: 2019-01-01.
        text (Union[Unset, str]):
    """

    action_date: Union[Unset, datetime.date] = UNSET
    text: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if text is not UNSET:
            field_dict["text"] = text

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

        text = d.pop("text", UNSET)

        bill_detail_latest_action = cls(
            action_date=action_date,
            text=text,
        )

        bill_detail_latest_action.additional_properties = d
        return bill_detail_latest_action

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
