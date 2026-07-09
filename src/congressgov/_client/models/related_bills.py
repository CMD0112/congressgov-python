from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.related_bills_lastest_action import RelatedBillsLastestAction
    from ..models.relationship_details import RelationshipDetails


T = TypeVar("T", bound="RelatedBills")


@_attrs_define
class RelatedBills:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 117.
        lastest_action (Union[Unset, RelatedBillsLastestAction]):
        number (Union[Unset, int]):  Example: 1720.
        relationship_details (Union[Unset, list['RelationshipDetails']]):
    """

    congress: Union[Unset, int] = UNSET
    lastest_action: Union[Unset, "RelatedBillsLastestAction"] = UNSET
    number: Union[Unset, int] = UNSET
    relationship_details: Union[Unset, list["RelationshipDetails"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        lastest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.lastest_action, Unset):
            lastest_action = self.lastest_action.to_dict()

        number = self.number

        relationship_details: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.relationship_details, Unset):
            relationship_details = []
            for relationship_details_item_data in self.relationship_details:
                relationship_details_item = relationship_details_item_data.to_dict()
                relationship_details.append(relationship_details_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if lastest_action is not UNSET:
            field_dict["lastestAction"] = lastest_action
        if number is not UNSET:
            field_dict["number"] = number
        if relationship_details is not UNSET:
            field_dict["relationshipDetails"] = relationship_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.related_bills_lastest_action import RelatedBillsLastestAction
        from ..models.relationship_details import RelationshipDetails

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        _lastest_action = d.pop("lastestAction", UNSET)
        lastest_action: Union[Unset, RelatedBillsLastestAction]
        if isinstance(_lastest_action, Unset):
            lastest_action = UNSET
        else:
            lastest_action = RelatedBillsLastestAction.from_dict(_lastest_action)

        number = d.pop("number", UNSET)

        relationship_details = []
        _relationship_details = d.pop("relationshipDetails", UNSET)
        for relationship_details_item_data in _relationship_details or []:
            relationship_details_item = RelationshipDetails.from_dict(relationship_details_item_data)

            relationship_details.append(relationship_details_item)

        related_bills = cls(
            congress=congress,
            lastest_action=lastest_action,
            number=number,
            relationship_details=relationship_details,
        )

        related_bills.additional_properties = d
        return related_bills

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
