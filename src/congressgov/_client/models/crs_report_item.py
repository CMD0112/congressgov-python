import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CrsReportItem")


@_attrs_define
class CrsReportItem:
    """
    Attributes:
        content_type (Union[Unset, str]):  Example: Reports.
        id (Union[Unset, str]):  Example: R43083.
        publish_date (Union[Unset, datetime.datetime]):  Example: 2025-02-05T11:34:25Z.
        status (Union[Unset, str]):  Example: Active.
        title (Union[Unset, str]):  Example: SBA Assistance to Small Business Startups: Client Experiences and Program
            Impact.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-02-07T01:36:49Z.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/crsreport/R43083.
        version (Union[Unset, int]):  Example: 145.
    """

    content_type: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    publish_date: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    version: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content_type = self.content_type

        id = self.id

        publish_date: Union[Unset, str] = UNSET
        if not isinstance(self.publish_date, Unset):
            publish_date = self.publish_date.isoformat()

        status = self.status

        title = self.title

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if id is not UNSET:
            field_dict["id"] = id
        if publish_date is not UNSET:
            field_dict["publishDate"] = publish_date
        if status is not UNSET:
            field_dict["status"] = status
        if title is not UNSET:
            field_dict["title"] = title
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        content_type = d.pop("contentType", UNSET)

        id = d.pop("id", UNSET)

        _publish_date = d.pop("publishDate", UNSET)
        publish_date: Union[Unset, datetime.datetime]
        if isinstance(_publish_date, Unset) or _publish_date is None:
            publish_date = UNSET
        else:
            publish_date = isoparse(_publish_date)

        status = d.pop("status", UNSET)

        title = d.pop("title", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        version = d.pop("version", UNSET)

        crs_report_item = cls(
            content_type=content_type,
            id=id,
            publish_date=publish_date,
            status=status,
            title=title,
            update_date=update_date,
            url=url,
            version=version,
        )

        crs_report_item.additional_properties = d
        return crs_report_item

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
