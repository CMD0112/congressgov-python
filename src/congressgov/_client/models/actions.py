import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actions_source_system import ActionsSourceSystem


T = TypeVar("T", bound="Actions")


@_attrs_define
class Actions:
    """
    Attributes:
        action_code (Union[Unset, str]):  Example: 36000.
        action_date (Union[Unset, datetime.date]):  Example: 2019-01-01.
        source_system (Union[Unset, ActionsSourceSystem]):
        text (Union[Unset, str]):  Example: Became Public Law No: 117-108..
        type_ (Union[Unset, str]):  Example: BecameLaw.
    """

    action_code: Union[Unset, str] = UNSET
    action_date: Union[Unset, datetime.date] = UNSET
    source_system: Union[Unset, "ActionsSourceSystem"] = UNSET
    text: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_code = self.action_code

        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        source_system: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.source_system, Unset):
            source_system = self.source_system.to_dict()

        text = self.text

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_code is not UNSET:
            field_dict["actionCode"] = action_code
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if source_system is not UNSET:
            field_dict["sourceSystem"] = source_system
        if text is not UNSET:
            field_dict["text"] = text
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actions_source_system import ActionsSourceSystem

        d = dict(src_dict)
        action_code = d.pop("actionCode", UNSET)

        _action_date = d.pop("actionDate", UNSET)
        action_date: Union[Unset, datetime.date]
        if isinstance(_action_date, Unset) or _action_date is None:
            action_date = UNSET
        else:
            action_date = isoparse(_action_date)

        _source_system = d.pop("sourceSystem", UNSET)
        source_system: Union[Unset, ActionsSourceSystem]
        if isinstance(_source_system, Unset):
            source_system = UNSET
        else:
            source_system = ActionsSourceSystem.from_dict(_source_system)

        text = d.pop("text", UNSET)

        type_ = d.pop("type", UNSET)

        actions = cls(
            action_code=action_code,
            action_date=action_date,
            source_system=source_system,
            text=text,
            type_=type_,
        )

        actions.additional_properties = d
        return actions

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
