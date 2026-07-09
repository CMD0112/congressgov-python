from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treaty_committee_activities_item import TreatyCommitteeActivitiesItem
    from ..models.treaty_committee_subcommittees_item import TreatyCommitteeSubcommitteesItem


T = TypeVar("T", bound="TreatyCommittee")


@_attrs_define
class TreatyCommittee:
    """
    Attributes:
        activities (Union[Unset, list['TreatyCommitteeActivitiesItem']]):
        chamber (Union[Unset, str]):  Example: Senate.
        name (Union[Unset, str]):  Example: Foreign Relations Committee.
        subcommittees (Union[Unset, list['TreatyCommitteeSubcommitteesItem']]):
        system_code (Union[Unset, str]):  Example: ssfr00.
        type_ (Union[Unset, str]):  Example: Standing.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee/senate/ssfr00?format=json.
    """

    activities: Union[Unset, list["TreatyCommitteeActivitiesItem"]] = UNSET
    chamber: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    subcommittees: Union[Unset, list["TreatyCommitteeSubcommitteesItem"]] = UNSET
    system_code: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activities: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.activities, Unset):
            activities = []
            for activities_item_data in self.activities:
                activities_item = activities_item_data.to_dict()
                activities.append(activities_item)

        chamber = self.chamber

        name = self.name

        subcommittees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subcommittees, Unset):
            subcommittees = []
            for subcommittees_item_data in self.subcommittees:
                subcommittees_item = subcommittees_item_data.to_dict()
                subcommittees.append(subcommittees_item)

        system_code = self.system_code

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if activities is not UNSET:
            field_dict["activities"] = activities
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if name is not UNSET:
            field_dict["name"] = name
        if subcommittees is not UNSET:
            field_dict["subcommittees"] = subcommittees
        if system_code is not UNSET:
            field_dict["systemCode"] = system_code
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.treaty_committee_activities_item import TreatyCommitteeActivitiesItem
        from ..models.treaty_committee_subcommittees_item import TreatyCommitteeSubcommitteesItem

        d = dict(src_dict)
        activities = []
        _activities = d.pop("activities", UNSET)
        for activities_item_data in _activities or []:
            activities_item = TreatyCommitteeActivitiesItem.from_dict(activities_item_data)

            activities.append(activities_item)

        chamber = d.pop("chamber", UNSET)

        name = d.pop("name", UNSET)

        subcommittees = []
        _subcommittees = d.pop("subcommittees", UNSET)
        for subcommittees_item_data in _subcommittees or []:
            subcommittees_item = TreatyCommitteeSubcommitteesItem.from_dict(subcommittees_item_data)

            subcommittees.append(subcommittees_item)

        system_code = d.pop("systemCode", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        treaty_committee = cls(
            activities=activities,
            chamber=chamber,
            name=name,
            subcommittees=subcommittees,
            system_code=system_code,
            type_=type_,
            url=url,
        )

        treaty_committee.additional_properties = d
        return treaty_committee

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
