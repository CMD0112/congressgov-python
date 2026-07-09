import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.committee_communication_communication_type import CommitteeCommunicationCommunicationType


T = TypeVar("T", bound="CommitteeCommunication")


@_attrs_define
class CommitteeCommunication:
    """
    Attributes:
        communication_type (Union[Unset, CommitteeCommunicationCommunicationType]):
        congress (Union[Unset, int]):  Example: 114.
        number (Union[Unset, int]):  Example: 3262.
        referral_date (Union[Unset, datetime.date]):  Example: 2015-10-27.
        update_date (Union[Unset, datetime.date]):  Example: 2018-02-02.
    """

    communication_type: Union[Unset, "CommitteeCommunicationCommunicationType"] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, int] = UNSET
    referral_date: Union[Unset, datetime.date] = UNSET
    update_date: Union[Unset, datetime.date] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        communication_type: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.communication_type, Unset):
            communication_type = self.communication_type.to_dict()

        congress = self.congress

        number = self.number

        referral_date: Union[Unset, str] = UNSET
        if not isinstance(self.referral_date, Unset):
            referral_date = self.referral_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if communication_type is not UNSET:
            field_dict["communicationType"] = communication_type
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if referral_date is not UNSET:
            field_dict["referralDate"] = referral_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.committee_communication_communication_type import CommitteeCommunicationCommunicationType

        d = dict(src_dict)
        _communication_type = d.pop("communicationType", UNSET)
        communication_type: Union[Unset, CommitteeCommunicationCommunicationType]
        if isinstance(_communication_type, Unset):
            communication_type = UNSET
        else:
            communication_type = CommitteeCommunicationCommunicationType.from_dict(_communication_type)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        _referral_date = d.pop("referralDate", UNSET)
        referral_date: Union[Unset, datetime.date]
        if isinstance(_referral_date, Unset) or _referral_date is None:
            referral_date = UNSET
        else:
            referral_date = isoparse(_referral_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.date]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        committee_communication = cls(
            communication_type=communication_type,
            congress=congress,
            number=number,
            referral_date=referral_date,
            update_date=update_date,
        )

        committee_communication.additional_properties = d
        return committee_communication

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
