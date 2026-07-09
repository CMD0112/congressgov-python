from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.associated_bill import AssociatedBill
    from ..models.related_item_nominations_item import RelatedItemNominationsItem
    from ..models.related_item_treaties_item import RelatedItemTreatiesItem


T = TypeVar("T", bound="RelatedItem")


@_attrs_define
class RelatedItem:
    """
    Attributes:
        bills (Union[Unset, list['AssociatedBill']]):
        nominations (Union[Unset, list['RelatedItemNominationsItem']]):
        treaties (Union[Unset, list['RelatedItemTreatiesItem']]):
    """

    bills: Union[Unset, list["AssociatedBill"]] = UNSET
    nominations: Union[Unset, list["RelatedItemNominationsItem"]] = UNSET
    treaties: Union[Unset, list["RelatedItemTreatiesItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bills: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.bills, Unset):
            bills = []
            for bills_item_data in self.bills:
                bills_item = bills_item_data.to_dict()
                bills.append(bills_item)

        nominations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nominations, Unset):
            nominations = []
            for nominations_item_data in self.nominations:
                nominations_item = nominations_item_data.to_dict()
                nominations.append(nominations_item)

        treaties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.treaties, Unset):
            treaties = []
            for treaties_item_data in self.treaties:
                treaties_item = treaties_item_data.to_dict()
                treaties.append(treaties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bills is not UNSET:
            field_dict["bills"] = bills
        if nominations is not UNSET:
            field_dict["nominations"] = nominations
        if treaties is not UNSET:
            field_dict["treaties"] = treaties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.associated_bill import AssociatedBill
        from ..models.related_item_nominations_item import RelatedItemNominationsItem
        from ..models.related_item_treaties_item import RelatedItemTreatiesItem

        d = dict(src_dict)
        bills = []
        _bills = d.pop("bills", UNSET)
        for bills_item_data in _bills or []:
            bills_item = AssociatedBill.from_dict(bills_item_data)

            bills.append(bills_item)

        nominations = []
        _nominations = d.pop("nominations", UNSET)
        for nominations_item_data in _nominations or []:
            nominations_item = RelatedItemNominationsItem.from_dict(nominations_item_data)

            nominations.append(nominations_item)

        treaties = []
        _treaties = d.pop("treaties", UNSET)
        for treaties_item_data in _treaties or []:
            treaties_item = RelatedItemTreatiesItem.from_dict(treaties_item_data)

            treaties.append(treaties_item)

        related_item = cls(
            bills=bills,
            nominations=nominations,
            treaties=treaties,
        )

        related_item.additional_properties = d
        return related_item

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
