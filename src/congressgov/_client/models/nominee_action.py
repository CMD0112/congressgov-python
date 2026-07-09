import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.senatecommittee import Senatecommittee


T = TypeVar("T", bound="NomineeAction")


@_attrs_define
class NomineeAction:
    """
    Attributes:
        action_code (Union[Unset, str]):  Example: S05120.
        action_date (Union[Unset, datetime.date]):  Example: 2022-08-03.
        committees (Union[Unset, list['Senatecommittee']]):
        text (Union[Unset, str]):  Example: Received in the Senate and referred to the Committee on Armed Services.
        type_ (Union[Unset, str]):  Example: IntroReferral.
    """

    action_code: Union[Unset, str] = UNSET
    action_date: Union[Unset, datetime.date] = UNSET
    committees: Union[Unset, list["Senatecommittee"]] = UNSET
    text: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_code = self.action_code

        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = []
            for committees_item_data in self.committees:
                committees_item = committees_item_data.to_dict()
                committees.append(committees_item)

        text = self.text

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_code is not UNSET:
            field_dict["actionCode"] = action_code
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if committees is not UNSET:
            field_dict["committees"] = committees
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

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = Senatecommittee.from_dict(committees_item_data)

            committees.append(committees_item)

        text = d.pop("text", UNSET)

        type_ = d.pop("type", UNSET)

        nominee_action = cls(
            action_code=action_code,
            action_date=action_date,
            committees=committees,
            text=text,
            type_=type_,
        )

        nominee_action.additional_properties = d
        return nominee_action

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
