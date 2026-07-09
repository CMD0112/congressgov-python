import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.amendment_latest_action import AmendmentLatestAction


T = TypeVar("T", bound="Amendment")


@_attrs_define
class Amendment:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 117.
        description (Union[Unset, str]):  Example: Amendment changes the effective date of the bill to the date of
            enactment..
        latest_action (Union[Unset, AmendmentLatestAction]):
        number (Union[Unset, str]):  Example: 2137.
        purpose (Union[Unset, str]):  Example: In the nature of a substitute..
        type_ (Union[Unset, str]):
        update_date (Union[Unset, datetime.datetime]):  Example: 2021-08-08T12:00:00Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/amendment/117/samdt/2137?format=json.
    """

    congress: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    latest_action: Union[Unset, "AmendmentLatestAction"] = UNSET
    number: Union[Unset, str] = UNSET
    purpose: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        description = self.description

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        number = self.number

        purpose = self.purpose

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if description is not UNSET:
            field_dict["description"] = description
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if number is not UNSET:
            field_dict["number"] = number
        if purpose is not UNSET:
            field_dict["purpose"] = purpose
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.amendment_latest_action import AmendmentLatestAction

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        description = d.pop("description", UNSET)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, AmendmentLatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = AmendmentLatestAction.from_dict(_latest_action)

        number = d.pop("number", UNSET)

        purpose = d.pop("purpose", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        amendment = cls(
            congress=congress,
            description=description,
            latest_action=latest_action,
            number=number,
            purpose=purpose,
            type_=type_,
            update_date=update_date,
            url=url,
        )

        amendment.additional_properties = d
        return amendment

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
