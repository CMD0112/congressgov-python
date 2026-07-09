import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteeBill")


@_attrs_define
class CommitteeBill:
    """
    Attributes:
        action_date (Union[Unset, datetime.datetime]):  Example: 2022-02-18T16:38:41Z.
        congress (Union[Unset, int]):  Example: 117.
        number (Union[Unset, str]):  Example: 117.
        relationship_type (Union[Unset, str]):  Example: Referred to.
        type_ (Union[Unset, str]):  Example: HCONRES.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-02-18T16:38:41Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/112/hconres/117?format=json.
    """

    action_date: Union[Unset, datetime.datetime] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, str] = UNSET
    relationship_type: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_date: Union[Unset, str] = UNSET
        if not isinstance(self.action_date, Unset):
            action_date = self.action_date.isoformat()

        congress = self.congress

        number = self.number

        relationship_type = self.relationship_type

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_date is not UNSET:
            field_dict["actionDate"] = action_date
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if relationship_type is not UNSET:
            field_dict["relationshipType"] = relationship_type
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _action_date = d.pop("actionDate", UNSET)
        action_date: Union[Unset, datetime.datetime]
        if isinstance(_action_date, Unset) or _action_date is None:
            action_date = UNSET
        else:
            action_date = isoparse(_action_date)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        relationship_type = d.pop("relationshipType", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        committee_bill = cls(
            action_date=action_date,
            congress=congress,
            number=number,
            relationship_type=relationship_type,
            type_=type_,
            update_date=update_date,
            url=url,
        )

        committee_bill.additional_properties = d
        return committee_bill

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
