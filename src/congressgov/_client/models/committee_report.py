from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitteeReport")


@_attrs_define
class CommitteeReport:
    """
    Attributes:
        citation (Union[Unset, str]):  Example: H. Rept. 118-400.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee-report/118/HRPT/400?format=json.
    """

    citation: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        citation = self.citation

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if citation is not UNSET:
            field_dict["citation"] = citation
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        citation = d.pop("citation", UNSET)

        url = d.pop("url", UNSET)

        committee_report = cls(
            citation=citation,
            url=url,
        )

        committee_report.additional_properties = d
        return committee_report

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
