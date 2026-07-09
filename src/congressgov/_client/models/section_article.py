from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.section_article_text_item import SectionArticleTextItem


T = TypeVar("T", bound="SectionArticle")


@_attrs_define
class SectionArticle:
    """
    Attributes:
        end_page (Union[Unset, str]):  Example: D760.
        start_page (Union[Unset, str]):  Example: D759.
        text (Union[Unset, list['SectionArticleTextItem']]):
        title (Union[Unset, str]):  Example: Daily Digest/Next Meeting of the SENATE + Next Meeting of the HOUSE OF
            REPRESENTATIVES + Other End Matter; Congressional Record Vol. 166, No. 153.
    """

    end_page: Union[Unset, str] = UNSET
    start_page: Union[Unset, str] = UNSET
    text: Union[Unset, list["SectionArticleTextItem"]] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_page = self.end_page

        start_page = self.start_page

        text: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.text, Unset):
            text = []
            for text_item_data in self.text:
                text_item = text_item_data.to_dict()
                text.append(text_item)

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if end_page is not UNSET:
            field_dict["endPage"] = end_page
        if start_page is not UNSET:
            field_dict["startPage"] = start_page
        if text is not UNSET:
            field_dict["text"] = text
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.section_article_text_item import SectionArticleTextItem

        d = dict(src_dict)
        end_page = d.pop("endPage", UNSET)

        start_page = d.pop("startPage", UNSET)

        text = []
        _text = d.pop("text", UNSET)
        for text_item_data in _text or []:
            text_item = SectionArticleTextItem.from_dict(text_item_data)

            text.append(text_item)

        title = d.pop("title", UNSET)

        section_article = cls(
            end_page=end_page,
            start_page=start_page,
            text=text,
            title=title,
        )

        section_article.additional_properties = d
        return section_article

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
