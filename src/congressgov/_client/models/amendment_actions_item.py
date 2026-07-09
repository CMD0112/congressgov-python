import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.recorded_vote import RecordedVote
    from ..models.source_system import SourceSystem


T = TypeVar("T", bound="AmendmentActionsItem")


@_attrs_define
class AmendmentActionsItem:
    """
    Attributes:
        action_date (Union[Unset, datetime.date]):  Example: 2021-08-08.
        recorded_votes (Union[Unset, list['RecordedVote']]):
        source_system (Union[Unset, SourceSystem]):
        text (Union[Unset, str]):  Example: Amendment SA 2137 agreed to in Senate by Yea-Nay Vote. 69 - 28. Record Vote
            Number: 312..
        type_ (Union[Unset, str]):  Example: Floor.
    """

    action_date: Union[Unset, datetime.date] = UNSET
    recorded_votes: Union[Unset, list["RecordedVote"]] = UNSET
    source_system: Union[Unset, "SourceSystem"] = UNSET
    text: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        recorded_votes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.recorded_votes, Unset):
            recorded_votes = []
            for recorded_votes_item_data in self.recorded_votes:
                recorded_votes_item = recorded_votes_item_data.to_dict()
                recorded_votes.append(recorded_votes_item)

        source_system: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.source_system, Unset):
            source_system = self.source_system.to_dict()

        text = self.text

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if recorded_votes is not UNSET:
            field_dict["recordedVotes"] = recorded_votes
        if source_system is not UNSET:
            field_dict["sourceSystem"] = source_system
        if text is not UNSET:
            field_dict["text"] = text
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recorded_vote import RecordedVote
        from ..models.source_system import SourceSystem

        d = dict(src_dict)
        _action_date = d.pop("actionDate", UNSET)
        action_date: Union[Unset, datetime.date]
        if isinstance(_action_date, Unset) or _action_date is None:
            action_date = UNSET
        else:
            action_date = isoparse(_action_date)

        recorded_votes = []
        _recorded_votes = d.pop("recordedVotes", UNSET)
        for recorded_votes_item_data in _recorded_votes or []:
            recorded_votes_item = RecordedVote.from_dict(recorded_votes_item_data)

            recorded_votes.append(recorded_votes_item)

        _source_system = d.pop("sourceSystem", UNSET)
        source_system: Union[Unset, SourceSystem]
        if isinstance(_source_system, Unset):
            source_system = UNSET
        else:
            source_system = SourceSystem.from_dict(_source_system)

        text = d.pop("text", UNSET)

        type_ = d.pop("type", UNSET)

        amendment_actions_item = cls(
            action_date=action_date,
            recorded_votes=recorded_votes,
            source_system=source_system,
            text=text,
            type_=type_,
        )

        amendment_actions_item.additional_properties = d
        return amendment_actions_item

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
