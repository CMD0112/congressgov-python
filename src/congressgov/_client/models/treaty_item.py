import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_item_parts import TreatyItemParts


T = TypeVar("T", bound="TreatyItem")


@_attrs_define
class TreatyItem:
    """
    Attributes:
        congress_received (Union[Unset, int]):  Example: 89.
        congress_considered (Union[Unset, int]):  Example: 89.
        number (Union[Unset, int]):  Example: 3.
        parts (Union[Unset, TreatyItemParts]):
        suffix (Union[Unset, str]):
        topic (Union[Unset, str]):  Example: Dispute Settlement and Arbitration.
        transmitted_date (Union[Unset, datetime.datetime]):  Example: 1965-05-17T00:00:00Z.
        update_date (Union[Unset, datetime.datetime]):  Example: 2024-12-11T00:18:16Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/treaty/89/3?format=json.
    """

    congress_received: Union[Unset, int] = UNSET
    congress_considered: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    parts: Union[Unset, "TreatyItemParts"] = UNSET
    suffix: Union[Unset, str] = UNSET
    topic: Union[Unset, str] = UNSET
    transmitted_date: Union[Unset, datetime.datetime] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress_received = self.congress_received

        congress_considered = self.congress_considered

        number = self.number

        parts: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parts, Unset):
            parts = self.parts.to_dict()

        suffix = self.suffix

        topic = self.topic

        transmitted_date: Union[Unset, str] = UNSET
        if not isinstance(self.transmitted_date, Unset):
            transmitted_date = self.transmitted_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress_received is not UNSET:
            field_dict["congressReceived"] = congress_received
        if congress_considered is not UNSET:
            field_dict["congressConsidered"] = congress_considered
        if number is not UNSET:
            field_dict["number"] = number
        if parts is not UNSET:
            field_dict["parts"] = parts
        if suffix is not UNSET:
            field_dict["suffix"] = suffix
        if topic is not UNSET:
            field_dict["topic"] = topic
        if transmitted_date is not UNSET:
            field_dict["transmittedDate"] = transmitted_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_item_parts import TreatyItemParts

        d = dict(src_dict)
        congress_received = d.pop("congressReceived", UNSET)

        congress_considered = d.pop("congressConsidered", UNSET)

        number = d.pop("number", UNSET)

        _parts = d.pop("parts", UNSET)
        parts: Union[Unset, TreatyItemParts]
        if isinstance(_parts, Unset):
            parts = UNSET
        else:
            parts = TreatyItemParts.from_dict(_parts)

        suffix = d.pop("suffix", UNSET)

        topic = d.pop("topic", UNSET)

        _transmitted_date = d.pop("transmittedDate", UNSET)
        transmitted_date: Union[Unset, datetime.datetime]
        if isinstance(_transmitted_date, Unset) or _transmitted_date is None:
            transmitted_date = UNSET
        else:
            transmitted_date = isoparse(_transmitted_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        treaty_item = cls(
            congress_received=congress_received,
            congress_considered=congress_considered,
            number=number,
            parts=parts,
            suffix=suffix,
            topic=topic,
            transmitted_date=transmitted_date,
            update_date=update_date,
            url=url,
        )

        treaty_item.additional_properties = d
        return treaty_item

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
