import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parentcommittee import Parentcommittee
    from ..models.subcommittees import Subcommittees


T = TypeVar("T", bound="Committees")


@_attrs_define
class Committees:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        committee_type_code (Union[Unset, str]):  Example: Standing.
        update_date (Union[Unset, datetime.datetime]):  Example: 2020-02-04T00:07:37Z.
        name (Union[Unset, str]):  Example: Transportation and Infrastructure Committee.
        parent (Union[Unset, Parentcommittee]):
        subcommittees (Union[Unset, list['Subcommittees']]):
        system_code (Union[Unset, str]):  Example: hspw00.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee/house/hspw00?format=json.
    """

    chamber: Union[Unset, str] = UNSET
    committee_type_code: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    name: Union[Unset, str] = UNSET
    parent: Union[Unset, "Parentcommittee"] = UNSET
    subcommittees: Union[Unset, list["Subcommittees"]] = UNSET
    system_code: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        committee_type_code = self.committee_type_code

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        name = self.name

        parent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent, Unset):
            parent = self.parent.to_dict()

        subcommittees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subcommittees, Unset):
            subcommittees = []
            for subcommittees_item_data in self.subcommittees:
                subcommittees_item = subcommittees_item_data.to_dict()
                subcommittees.append(subcommittees_item)

        system_code = self.system_code

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if committee_type_code is not UNSET:
            field_dict["committeeTypeCode"] = committee_type_code
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if name is not UNSET:
            field_dict["name"] = name
        if parent is not UNSET:
            field_dict["parent"] = parent
        if subcommittees is not UNSET:
            field_dict["subcommittees"] = subcommittees
        if system_code is not UNSET:
            field_dict["systemCode"] = system_code
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parentcommittee import Parentcommittee
        from ..models.subcommittees import Subcommittees

        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        committee_type_code = d.pop("committeeTypeCode", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        name = d.pop("name", UNSET)

        _parent = d.pop("parent", UNSET)
        parent: Union[Unset, Parentcommittee]
        if isinstance(_parent, Unset):
            parent = UNSET
        else:
            parent = Parentcommittee.from_dict(_parent)

        subcommittees = []
        _subcommittees = d.pop("subcommittees", UNSET)
        for subcommittees_item_data in _subcommittees or []:
            subcommittees_item = Subcommittees.from_dict(subcommittees_item_data)

            subcommittees.append(subcommittees_item)

        system_code = d.pop("systemCode", UNSET)

        url = d.pop("url", UNSET)

        committees = cls(
            chamber=chamber,
            committee_type_code=committee_type_code,
            update_date=update_date,
            name=name,
            parent=parent,
            subcommittees=subcommittees,
            system_code=system_code,
            url=url,
        )

        committees.additional_properties = d
        return committees

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
