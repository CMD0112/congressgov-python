import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CboCost")


@_attrs_define
class CboCost:
    """
    Attributes:
        description (Union[Unset, str]):  Example: As ordered reported by the House Committee on Oversight and
            Accountability on September 20, 2023
            .
        pub_date (Union[Unset, datetime.date]):  Example: 2023-10-10T19:58:00Z.
        title (Union[Unset, str]):  Example: H.R. 4984, D.C. Robert F. Kennedy Memorial Stadium Campus Revitalization
            Act.
        url (Union[Unset, str]):  Example: https://www.cbo.gov/publication/59651.
    """

    description: Union[Unset, str] = UNSET
    pub_date: Union[Unset, datetime.date] = UNSET
    title: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        pub_date: Union[Unset, str] = UNSET
        if not isinstance(self.pub_date, Unset):
            pub_date = self.pub_date.isoformat()

        title = self.title

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if pub_date is not UNSET:
            field_dict["pubDate"] = pub_date
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        _pub_date = d.pop("pubDate", UNSET)
        pub_date: Union[Unset, datetime.date]
        if isinstance(_pub_date, Unset) or _pub_date is None:
            pub_date = UNSET
        else:
            pub_date = isoparse(_pub_date)

        title = d.pop("title", UNSET)

        url = d.pop("url", UNSET)

        cbo_cost = cls(
            description=description,
            pub_date=pub_date,
            title=title,
            url=url,
        )

        cbo_cost.additional_properties = d
        return cbo_cost

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
