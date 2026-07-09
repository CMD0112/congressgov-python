import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.latest_action import LatestAction
    from ..models.policy_area import PolicyArea


T = TypeVar("T", bound="SponsoredLegislation")


@_attrs_define
class SponsoredLegislation:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 117.
        introduced_date (Union[Unset, datetime.date]):  Example: 2022-06-16.
        latest_action (Union[Unset, LatestAction]):
        number (Union[Unset, str]):  Example: 4417.
        policy_area (Union[Unset, PolicyArea]):
        title (Union[Unset, str]):  Example: Patent Trial and Appeal Board Reform Act of 2022.
        type_ (Union[Unset, str]):  Example: S.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/bill/117/s/4417?format=json.
    """

    congress: Union[Unset, int] = UNSET
    introduced_date: Union[Unset, datetime.date] = UNSET
    latest_action: Union[Unset, "LatestAction"] = UNSET
    number: Union[Unset, str] = UNSET
    policy_area: Union[Unset, "PolicyArea"] = UNSET
    title: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        introduced_date: Union[Unset, str] = UNSET
        if not isinstance(self.introduced_date, Unset):
            introduced_date = self.introduced_date.isoformat()

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        number = self.number

        policy_area: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_area, Unset):
            policy_area = self.policy_area.to_dict()

        title = self.title

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if introduced_date is not UNSET:
            field_dict["introducedDate"] = introduced_date
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if number is not UNSET:
            field_dict["number"] = number
        if policy_area is not UNSET:
            field_dict["policyArea"] = policy_area
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.latest_action import LatestAction
        from ..models.policy_area import PolicyArea

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        _introduced_date = d.pop("introducedDate", UNSET)
        introduced_date: Union[Unset, datetime.date]
        if isinstance(_introduced_date, Unset) or _introduced_date is None:
            introduced_date = UNSET
        else:
            introduced_date = isoparse(_introduced_date)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, LatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = LatestAction.from_dict(_latest_action)

        number = d.pop("number", UNSET)

        _policy_area = d.pop("policyArea", UNSET)
        policy_area: Union[Unset, PolicyArea]
        if isinstance(_policy_area, Unset):
            policy_area = UNSET
        else:
            policy_area = PolicyArea.from_dict(_policy_area)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        sponsored_legislation = cls(
            congress=congress,
            introduced_date=introduced_date,
            latest_action=latest_action,
            number=number,
            policy_area=policy_area,
            title=title,
            type_=type_,
            url=url,
        )

        sponsored_legislation.additional_properties = d
        return sponsored_legislation

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
