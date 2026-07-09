import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.latest_action import LatestAction
    from ..models.nomination_type import NominationType


T = TypeVar("T", bound="CommitteeNominationsItem")


@_attrs_define
class CommitteeNominationsItem:
    """
    Attributes:
        citation (Union[Unset, str]):  Example: PN2477.
        congress (Union[Unset, int]):  Example: 117.
        description (Union[Unset, str]):  Example: Nomination of xyz for the 117th Congress.
        latest_action (Union[Unset, LatestAction]):
        nomination_type (Union[Unset, NominationType]):
        number (Union[Unset, int]):  Example: 2477.
        part_number (Union[Unset, str]):  Example: 00.
        received_date (Union[Unset, datetime.date]):  Example: 2022-08-03.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-09-30 04:40:14+00:00.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/nomination/117/2477?format=json.
    """

    citation: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    latest_action: Union[Unset, "LatestAction"] = UNSET
    nomination_type: Union[Unset, "NominationType"] = UNSET
    number: Union[Unset, int] = UNSET
    part_number: Union[Unset, str] = UNSET
    received_date: Union[Unset, datetime.date] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        citation = self.citation

        congress = self.congress

        description = self.description

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        nomination_type: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.nomination_type, Unset):
            nomination_type = self.nomination_type.to_dict()

        number = self.number

        part_number = self.part_number

        received_date: Union[Unset, str] = UNSET
        if not isinstance(self.received_date, Unset):
            received_date = self.received_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if citation is not UNSET:
            field_dict["citation"] = citation
        if congress is not UNSET:
            field_dict["congress"] = congress
        if description is not UNSET:
            field_dict["description"] = description
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if nomination_type is not UNSET:
            field_dict["nominationType"] = nomination_type
        if number is not UNSET:
            field_dict["number"] = number
        if part_number is not UNSET:
            field_dict["partNumber"] = part_number
        if received_date is not UNSET:
            field_dict["receivedDate"] = received_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.latest_action import LatestAction
        from ..models.nomination_type import NominationType

        d = dict(src_dict)
        citation = d.pop("citation", UNSET)

        congress = d.pop("congress", UNSET)

        description = d.pop("description", UNSET)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, LatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = LatestAction.from_dict(_latest_action)

        _nomination_type = d.pop("nominationType", UNSET)
        nomination_type: Union[Unset, NominationType]
        if isinstance(_nomination_type, Unset):
            nomination_type = UNSET
        else:
            nomination_type = NominationType.from_dict(_nomination_type)

        number = d.pop("number", UNSET)

        part_number = d.pop("partNumber", UNSET)

        _received_date = d.pop("receivedDate", UNSET)
        received_date: Union[Unset, datetime.date]
        if isinstance(_received_date, Unset) or _received_date is None:
            received_date = UNSET
        else:
            received_date = isoparse(_received_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        committee_nominations_item = cls(
            citation=citation,
            congress=congress,
            description=description,
            latest_action=latest_action,
            nomination_type=nomination_type,
            number=number,
            part_number=part_number,
            received_date=received_date,
            update_date=update_date,
            url=url,
        )

        committee_nominations_item.additional_properties = d
        return committee_nominations_item

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
