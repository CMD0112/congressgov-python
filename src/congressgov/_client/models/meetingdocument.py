from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Meetingdocument")


@_attrs_define
class Meetingdocument:
    """
    Attributes:
        description (Union[Unset, str]):
        document_type (Union[Unset, str]):  Example: Support Document .
        format_ (Union[Unset, str]):  Example: PDF.
        name (Union[Unset, str]):  Example: Hearing Notice.
        url (Union[Unset, str]):  Example:
            https://www.congress.gov/118/meeting/house/115538/documents/HHRG-118-II24-20230324-SD001.pdf.
    """

    description: Union[Unset, str] = UNSET
    document_type: Union[Unset, str] = UNSET
    format_: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        document_type = self.document_type

        format_ = self.format_

        name = self.name

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if document_type is not UNSET:
            field_dict["documentType"] = document_type
        if format_ is not UNSET:
            field_dict["format"] = format_
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        document_type = d.pop("documentType", UNSET)

        format_ = d.pop("format", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        meetingdocument = cls(
            description=description,
            document_type=document_type,
            format_=format_,
            name=name,
            url=url,
        )

        meetingdocument.additional_properties = d
        return meetingdocument

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
