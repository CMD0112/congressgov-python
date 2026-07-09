from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.issues import Issues


T = TypeVar("T", bound="CongressionalRecord")


@_attrs_define
class CongressionalRecord:
    """
    Attributes:
        index_start (Union[Unset, int]):  Example: 1.
        issues (Union[Unset, list['Issues']]):
    """

    index_start: Union[Unset, int] = UNSET
    issues: Union[Unset, list["Issues"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        index_start = self.index_start

        issues: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.issues, Unset):
            issues = []
            for issues_item_data in self.issues:
                issues_item = issues_item_data.to_dict()
                issues.append(issues_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if index_start is not UNSET:
            field_dict["IndexStart"] = index_start
        if issues is not UNSET:
            field_dict["Issues"] = issues

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.issues import Issues

        d = dict(src_dict)
        index_start = d.pop("IndexStart", UNSET)

        issues = []
        _issues = d.pop("Issues", UNSET)
        for issues_item_data in _issues or []:
            issues_item = Issues.from_dict(issues_item_data)

            issues.append(issues_item)

        congressional_record = cls(
            index_start=index_start,
            issues=issues,
        )

        congressional_record.additional_properties = d
        return congressional_record

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
