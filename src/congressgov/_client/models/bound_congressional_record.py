from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bound_congressional_record_item import BoundCongressionalRecordItem


T = TypeVar("T", bound="BoundCongressionalRecord")


@_attrs_define
class BoundCongressionalRecord:
    """
    Attributes:
        bound_congressional_record (Union[Unset, list['BoundCongressionalRecordItem']]):
    """

    bound_congressional_record: Union[Unset, list["BoundCongressionalRecordItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bound_congressional_record: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.bound_congressional_record, Unset):
            bound_congressional_record = []
            for bound_congressional_record_item_data in self.bound_congressional_record:
                bound_congressional_record_item = bound_congressional_record_item_data.to_dict()
                bound_congressional_record.append(bound_congressional_record_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bound_congressional_record is not UNSET:
            field_dict["boundCongressionalRecord"] = bound_congressional_record

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bound_congressional_record_item import BoundCongressionalRecordItem

        d = dict(src_dict)
        bound_congressional_record = []
        _bound_congressional_record = d.pop("boundCongressionalRecord", UNSET)
        for bound_congressional_record_item_data in _bound_congressional_record or []:
            bound_congressional_record_item = BoundCongressionalRecordItem.from_dict(
                bound_congressional_record_item_data
            )

            bound_congressional_record.append(bound_congressional_record_item)

        bound_congressional_record = cls(
            bound_congressional_record=bound_congressional_record,
        )

        bound_congressional_record.additional_properties = d
        return bound_congressional_record

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
