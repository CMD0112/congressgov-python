from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.full_issue_articles import FullIssueArticles
    from ..models.full_issue_entire_issue_item import FullIssueEntireIssueItem
    from ..models.full_issue_sections_item import FullIssueSectionsItem


T = TypeVar("T", bound="FullIssue")


@_attrs_define
class FullIssue:
    """
    Attributes:
        articles (Union[Unset, FullIssueArticles]):
        entire_issue (Union[Unset, list['FullIssueEntireIssueItem']]):
        sections (Union[Unset, list['FullIssueSectionsItem']]):
    """

    articles: Union[Unset, "FullIssueArticles"] = UNSET
    entire_issue: Union[Unset, list["FullIssueEntireIssueItem"]] = UNSET
    sections: Union[Unset, list["FullIssueSectionsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.articles, Unset):
            articles = self.articles.to_dict()

        entire_issue: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.entire_issue, Unset):
            entire_issue = []
            for entire_issue_item_data in self.entire_issue:
                entire_issue_item = entire_issue_item_data.to_dict()
                entire_issue.append(entire_issue_item)

        sections: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sections, Unset):
            sections = []
            for sections_item_data in self.sections:
                sections_item = sections_item_data.to_dict()
                sections.append(sections_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if articles is not UNSET:
            field_dict["articles"] = articles
        if entire_issue is not UNSET:
            field_dict["entireIssue"] = entire_issue
        if sections is not UNSET:
            field_dict["sections"] = sections

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.full_issue_articles import FullIssueArticles
        from ..models.full_issue_entire_issue_item import FullIssueEntireIssueItem
        from ..models.full_issue_sections_item import FullIssueSectionsItem

        d = dict(src_dict)
        _articles = d.pop("articles", UNSET)
        articles: Union[Unset, FullIssueArticles]
        if isinstance(_articles, Unset):
            articles = UNSET
        else:
            articles = FullIssueArticles.from_dict(_articles)

        entire_issue = []
        _entire_issue = d.pop("entireIssue", UNSET)
        for entire_issue_item_data in _entire_issue or []:
            entire_issue_item = FullIssueEntireIssueItem.from_dict(entire_issue_item_data)

            entire_issue.append(entire_issue_item)

        sections = []
        _sections = d.pop("sections", UNSET)
        for sections_item_data in _sections or []:
            sections_item = FullIssueSectionsItem.from_dict(sections_item_data)

            sections.append(sections_item)

        full_issue = cls(
            articles=articles,
            entire_issue=entire_issue,
            sections=sections,
        )

        full_issue.additional_properties = d
        return full_issue

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
