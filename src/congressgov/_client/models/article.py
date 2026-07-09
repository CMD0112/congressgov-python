from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.section_article import SectionArticle


T = TypeVar("T", bound="Article")


@_attrs_define
class Article:
    """
    Attributes:
        name (Union[Unset, str]):  Example: Daily Digest.
        section_articles (Union[Unset, list['SectionArticle']]):
    """

    name: Union[Unset, str] = UNSET
    section_articles: Union[Unset, list["SectionArticle"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        section_articles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.section_articles, Unset):
            section_articles = []
            for section_articles_item_data in self.section_articles:
                section_articles_item = section_articles_item_data.to_dict()
                section_articles.append(section_articles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if section_articles is not UNSET:
            field_dict["sectionArticles"] = section_articles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.section_article import SectionArticle

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        section_articles = []
        _section_articles = d.pop("sectionArticles", UNSET)
        for section_articles_item_data in _section_articles or []:
            section_articles_item = SectionArticle.from_dict(section_articles_item_data)

            section_articles.append(section_articles_item)

        article = cls(
            name=name,
            section_articles=section_articles,
        )

        article.additional_properties = d
        return article

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
