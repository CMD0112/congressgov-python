from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.committee_bill import CommitteeBill


T = TypeVar("T", bound="CommitteeBills")


@_attrs_define
class CommitteeBills:
    """
    Attributes:
        bills (Union[Unset, list['CommitteeBill']]):
        count (Union[Unset, int]):  Example: 27251.
        url (Union[Unset, str]):  Example: https://api.congress.gov/v3/committee/house/hspw00/bills?format=json.
    """

    bills: Union[Unset, list["CommitteeBill"]] = UNSET
    count: Union[Unset, int] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bills: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.bills, Unset):
            bills = []
            for bills_item_data in self.bills:
                bills_item = bills_item_data.to_dict()
                bills.append(bills_item)

        count = self.count

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bills is not UNSET:
            field_dict["bills"] = bills
        if count is not UNSET:
            field_dict["count"] = count
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.committee_bill import CommitteeBill

        d = dict(src_dict)
        bills = []
        _bills = d.pop("bills", UNSET)
        for bills_item_data in _bills or []:
            bills_item = CommitteeBill.from_dict(bills_item_data)

            bills.append(bills_item)

        count = d.pop("count", UNSET)

        url = d.pop("url", UNSET)

        committee_bills = cls(
            bills=bills,
            count=count,
            url=url,
        )

        committee_bills.additional_properties = d
        return committee_bills

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
