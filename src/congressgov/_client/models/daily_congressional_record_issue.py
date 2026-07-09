from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.daily_congressional_record_issue_issue import DailyCongressionalRecordIssueIssue


T = TypeVar("T", bound="DailyCongressionalRecordIssue")


@_attrs_define
class DailyCongressionalRecordIssue:
    """
    Attributes:
        issue (Union[Unset, DailyCongressionalRecordIssueIssue]):
    """

    issue: Union[Unset, "DailyCongressionalRecordIssueIssue"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issue: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.issue, Unset):
            issue = self.issue.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if issue is not UNSET:
            field_dict["issue"] = issue

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.daily_congressional_record_issue_issue import DailyCongressionalRecordIssueIssue

        d = dict(src_dict)
        _issue = d.pop("issue", UNSET)
        issue: Union[Unset, DailyCongressionalRecordIssueIssue]
        if isinstance(_issue, Unset):
            issue = UNSET
        else:
            issue = DailyCongressionalRecordIssueIssue.from_dict(_issue)

        daily_congressional_record_issue = cls(
            issue=issue,
        )

        daily_congressional_record_issue.additional_properties = d
        return daily_congressional_record_issue

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
