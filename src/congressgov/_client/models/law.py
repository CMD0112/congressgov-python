import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.law_latest_action import LawLatestAction
    from ..models.laws import Laws


T = TypeVar("T", bound="Law")


@_attrs_define
class Law:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 119.
        latest_action (Union[Unset, LawLatestAction]):
        laws (Union[Unset, list['Laws']]):
        number (Union[Unset, str]):  Example: 2808.
        origin_chamber (Union[Unset, str]):  Example: House.
        origin_chamber_code (Union[Unset, str]):  Example: H.
        title (Union[Unset, str]):  Example: Homebuyers Privacy Protection Act.
        type_ (Union[Unset, str]):  Example: HR.
        update_date (Union[Unset, datetime.date]):  Example: 2025-11-21.
        update_date_including_text (Union[Unset, datetime.datetime]):  Example: 2025-11-21.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/119/hr/2808?format=json.
    """

    congress: Union[Unset, int] = UNSET
    latest_action: Union[Unset, "LawLatestAction"] = UNSET
    laws: Union[Unset, list["Laws"]] = UNSET
    number: Union[Unset, str] = UNSET
    origin_chamber: Union[Unset, str] = UNSET
    origin_chamber_code: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    update_date_including_text: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        laws: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.laws, Unset):
            laws = []
            for laws_item_data in self.laws:
                laws_item = laws_item_data.to_dict()
                laws.append(laws_item)

        number = self.number

        origin_chamber = self.origin_chamber

        origin_chamber_code = self.origin_chamber_code

        title = self.title

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        update_date_including_text: Union[Unset, str] = UNSET
        if not isinstance(self.update_date_including_text, Unset):
            update_date_including_text = self.update_date_including_text.isoformat()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if laws is not UNSET:
            field_dict["laws"] = laws
        if number is not UNSET:
            field_dict["number"] = number
        if origin_chamber is not UNSET:
            field_dict["originChamber"] = origin_chamber
        if origin_chamber_code is not UNSET:
            field_dict["originChamberCode"] = origin_chamber_code
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if update_date_including_text is not UNSET:
            field_dict["updateDateIncludingText"] = update_date_including_text
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.law_latest_action import LawLatestAction
        from ..models.laws import Laws

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, LawLatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = LawLatestAction.from_dict(_latest_action)

        laws = []
        _laws = d.pop("laws", UNSET)
        for laws_item_data in _laws or []:
            laws_item = Laws.from_dict(laws_item_data)

            laws.append(laws_item)

        number = d.pop("number", UNSET)

        origin_chamber = d.pop("originChamber", UNSET)

        origin_chamber_code = d.pop("originChamberCode", UNSET)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        _update_date_including_text = d.pop("updateDateIncludingText", UNSET)
        update_date_including_text: Union[Unset, datetime.datetime]
        if isinstance(_update_date_including_text, Unset) or _update_date_including_text is None:
            update_date_including_text = UNSET
        else:
            update_date_including_text = isoparse(_update_date_including_text)

        url = d.pop("url", UNSET)

        law = cls(
            congress=congress,
            latest_action=latest_action,
            laws=laws,
            number=number,
            origin_chamber=origin_chamber,
            origin_chamber_code=origin_chamber_code,
            title=title,
            type_=type_,
            update_date=update_date,
            update_date_including_text=update_date_including_text,
            url=url,
        )

        law.additional_properties = d
        return law

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
