import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.formats import Formats


T = TypeVar("T", bound="TextVersions")


@_attrs_define
class TextVersions:
    """
    Attributes:
        date (Union[Unset, datetime.date]):  Example: 2022-02-18T16:38:41Z.
        formats (Union[Unset, list['Formats']]):
        type_ (Union[Unset, str]):  Example: Enrolled Bill.
    """

    date: Union[Unset, datetime.date] = UNSET
    formats: Union[Unset, list["Formats"]] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        formats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.formats, Unset):
            formats = []
            for formats_item_data in self.formats:
                formats_item = formats_item_data.to_dict()
                formats.append(formats_item)

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date
        if formats is not UNSET:
            field_dict["formats"] = formats
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.formats import Formats

        d = dict(src_dict)
        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.date]
        if isinstance(_date, Unset) or _date is None:
            date = UNSET
        else:
            date = isoparse(_date)

        formats = []
        _formats = d.pop("formats", UNSET)
        for formats_item_data in _formats or []:
            formats_item = Formats.from_dict(formats_item_data)

            formats.append(formats_item)

        type_ = d.pop("type", UNSET)

        text_versions = cls(
            date=date,
            formats=formats,
            type_=type_,
        )

        text_versions.additional_properties = d
        return text_versions

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
