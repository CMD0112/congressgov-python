import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.senatecommittee import Senatecommittee


T = TypeVar("T", bound="TreatyAction")


@_attrs_define
class TreatyAction:
    """
    Attributes:
        action_code (Union[Unset, str]):  Example: S05291.
        action_date (Union[Unset, datetime.date]):  Example: 2022-08-03.
        committee (Union[Unset, Senatecommittee]):
        text (Union[Unset, str]):  Example: Resolution of advice and consent to ratification agreed to as amended in
            Senate by Yea-Nay Vote. 95 - 1. Record Vote Number: 282..
        type_ (Union[Unset, str]):  Example: Floor.
    """

    action_code: Union[Unset, str] = UNSET
    action_date: Union[Unset, datetime.date] = UNSET
    committee: Union[Unset, "Senatecommittee"] = UNSET
    text: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_code = self.action_code

        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        committee: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.committee, Unset):
            committee = self.committee.to_dict()

        text = self.text

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_code is not UNSET:
            field_dict["actionCode"] = action_code
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if committee is not UNSET:
            field_dict["committee"] = committee
        if text is not UNSET:
            field_dict["text"] = text
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.senatecommittee import Senatecommittee

        d = dict(src_dict)
        action_code = d.pop("actionCode", UNSET)

        _action_date = d.pop("actionDate", UNSET)
        action_date: Union[Unset, datetime.date]
        if isinstance(_action_date, Unset) or _action_date is None:
            action_date = UNSET
        else:
            action_date = isoparse(_action_date)

        _committee = d.pop("committee", UNSET)
        committee: Union[Unset, Senatecommittee]
        if isinstance(_committee, Unset):
            committee = UNSET
        else:
            committee = Senatecommittee.from_dict(_committee)

        text = d.pop("text", UNSET)

        type_ = d.pop("type", UNSET)

        treaty_action = cls(
            action_code=action_code,
            action_date=action_date,
            committee=committee,
            text=text,
            type_=type_,
        )

        treaty_action.additional_properties = d
        return treaty_action

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
