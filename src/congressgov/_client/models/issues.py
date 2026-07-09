import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.issues_links import IssuesLinks


T = TypeVar("T", bound="Issues")


@_attrs_define
class Issues:
    """
    Attributes:
        congress (Union[Unset, str]):  Example: 117.
        id (Union[Unset, int]):  Example: 26958.
        issue (Union[Unset, str]):  Example: 109.
        links (Union[Unset, IssuesLinks]):
        publish_date (Union[Unset, datetime.date]):  Example: 2022-02-18.
        session (Union[Unset, str]):  Example: 2.
        volume (Union[Unset, str]):  Example: 168.
    """

    congress: Union[Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    issue: Union[Unset, str] = UNSET
    links: Union[Unset, "IssuesLinks"] = UNSET
    publish_date: Union[Unset, datetime.date] = UNSET
    session: Union[Unset, str] = UNSET
    volume: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        id = self.id

        issue = self.issue

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()

        publish_date: Union[Unset, str] = UNSET
        if not isinstance(self.publish_date, Unset):
            publish_date = self.publish_date.isoformat()

        session = self.session

        volume = self.volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["Congress"] = congress
        if id is not UNSET:
            field_dict["Id"] = id
        if issue is not UNSET:
            field_dict["Issue"] = issue
        if links is not UNSET:
            field_dict["Links"] = links
        if publish_date is not UNSET:
            field_dict["PublishDate"] = publish_date
        if session is not UNSET:
            field_dict["Session"] = session
        if volume is not UNSET:
            field_dict["Volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.issues_links import IssuesLinks

        d = dict(src_dict)
        congress = d.pop("Congress", UNSET)

        id = d.pop("Id", UNSET)

        issue = d.pop("Issue", UNSET)

        _links = d.pop("Links", UNSET)
        links: Union[Unset, IssuesLinks]
        if isinstance(_links, Unset):
            links = UNSET
        else:
            links = IssuesLinks.from_dict(_links)

        _publish_date = d.pop("PublishDate", UNSET)
        publish_date: Union[Unset, datetime.date]
        if isinstance(_publish_date, Unset) or _publish_date is None:
            publish_date = UNSET
        else:
            publish_date = isoparse(_publish_date)

        session = d.pop("Session", UNSET)

        volume = d.pop("Volume", UNSET)

        issues = cls(
            congress=congress,
            id=id,
            issue=issue,
            links=links,
            publish_date=publish_date,
            session=session,
            volume=volume,
        )

        issues.additional_properties = d
        return issues

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
