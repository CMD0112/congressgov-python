from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.article import Article


T = TypeVar("T", bound="DailyCongressionalRecordArticles")


@_attrs_define
class DailyCongressionalRecordArticles:
    """
    Attributes:
        articles (Union[Unset, list['Article']]):
    """

    articles: Union[Unset, list["Article"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.articles, Unset):
            articles = []
            for articles_item_data in self.articles:
                articles_item = articles_item_data.to_dict()
                articles.append(articles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if articles is not UNSET:
            field_dict["articles"] = articles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.article import Article

        d = dict(src_dict)
        articles = []
        _articles = d.pop("articles", UNSET)
        for articles_item_data in _articles or []:
            articles_item = Article.from_dict(articles_item_data)

            articles.append(articles_item)

        daily_congressional_record_articles = cls(
            articles=articles,
        )

        daily_congressional_record_articles.additional_properties = d
        return daily_congressional_record_articles

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
