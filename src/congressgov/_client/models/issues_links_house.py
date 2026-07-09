from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.issues_links_house_pdf_item import IssuesLinksHousePDFItem


T = TypeVar("T", bound="IssuesLinksHouse")


@_attrs_define
class IssuesLinksHouse:
    """
    Attributes:
        label (Union[Unset, str]):  Example: House Section.
        ordinal (Union[Unset, int]):  Example: 3.
        pdf (Union[Unset, list['IssuesLinksHousePDFItem']]):
    """

    label: Union[Unset, str] = UNSET
    ordinal: Union[Unset, int] = UNSET
    pdf: Union[Unset, list["IssuesLinksHousePDFItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        ordinal = self.ordinal

        pdf: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.pdf, Unset):
            pdf = []
            for pdf_item_data in self.pdf:
                pdf_item = pdf_item_data.to_dict()
                pdf.append(pdf_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["Label"] = label
        if ordinal is not UNSET:
            field_dict["Ordinal"] = ordinal
        if pdf is not UNSET:
            field_dict["PDF"] = pdf

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.issues_links_house_pdf_item import IssuesLinksHousePDFItem

        d = dict(src_dict)
        label = d.pop("Label", UNSET)

        ordinal = d.pop("Ordinal", UNSET)

        pdf = []
        _pdf = d.pop("PDF", UNSET)
        for pdf_item_data in _pdf or []:
            pdf_item = IssuesLinksHousePDFItem.from_dict(pdf_item_data)

            pdf.append(pdf_item)

        issues_links_house = cls(
            label=label,
            ordinal=ordinal,
            pdf=pdf,
        )

        issues_links_house.additional_properties = d
        return issues_links_house

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
