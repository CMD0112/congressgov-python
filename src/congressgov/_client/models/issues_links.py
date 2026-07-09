from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.issues_links_digest import IssuesLinksDigest
    from ..models.issues_links_full_record import IssuesLinksFullRecord
    from ..models.issues_links_house import IssuesLinksHouse
    from ..models.issues_links_remarks import IssuesLinksRemarks
    from ..models.issues_links_senate import IssuesLinksSenate


T = TypeVar("T", bound="IssuesLinks")


@_attrs_define
class IssuesLinks:
    """
    Attributes:
        digest (Union[Unset, IssuesLinksDigest]):
        full_record (Union[Unset, IssuesLinksFullRecord]):
        house (Union[Unset, IssuesLinksHouse]):
        remarks (Union[Unset, IssuesLinksRemarks]):
        senate (Union[Unset, IssuesLinksSenate]):
    """

    digest: Union[Unset, "IssuesLinksDigest"] = UNSET
    full_record: Union[Unset, "IssuesLinksFullRecord"] = UNSET
    house: Union[Unset, "IssuesLinksHouse"] = UNSET
    remarks: Union[Unset, "IssuesLinksRemarks"] = UNSET
    senate: Union[Unset, "IssuesLinksSenate"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        digest: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.digest, Unset):
            digest = self.digest.to_dict()

        full_record: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.full_record, Unset):
            full_record = self.full_record.to_dict()

        house: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.house, Unset):
            house = self.house.to_dict()

        remarks: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.remarks, Unset):
            remarks = self.remarks.to_dict()

        senate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.senate, Unset):
            senate = self.senate.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if digest is not UNSET:
            field_dict["Digest"] = digest
        if full_record is not UNSET:
            field_dict["FullRecord"] = full_record
        if house is not UNSET:
            field_dict["House"] = house
        if remarks is not UNSET:
            field_dict["Remarks"] = remarks
        if senate is not UNSET:
            field_dict["Senate"] = senate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.issues_links_digest import IssuesLinksDigest
        from ..models.issues_links_full_record import IssuesLinksFullRecord
        from ..models.issues_links_house import IssuesLinksHouse
        from ..models.issues_links_remarks import IssuesLinksRemarks
        from ..models.issues_links_senate import IssuesLinksSenate

        d = dict(src_dict)
        _digest = d.pop("Digest", UNSET)
        digest: Union[Unset, IssuesLinksDigest]
        if isinstance(_digest, Unset):
            digest = UNSET
        else:
            digest = IssuesLinksDigest.from_dict(_digest)

        _full_record = d.pop("FullRecord", UNSET)
        full_record: Union[Unset, IssuesLinksFullRecord]
        if isinstance(_full_record, Unset):
            full_record = UNSET
        else:
            full_record = IssuesLinksFullRecord.from_dict(_full_record)

        _house = d.pop("House", UNSET)
        house: Union[Unset, IssuesLinksHouse]
        if isinstance(_house, Unset):
            house = UNSET
        else:
            house = IssuesLinksHouse.from_dict(_house)

        _remarks = d.pop("Remarks", UNSET)
        remarks: Union[Unset, IssuesLinksRemarks]
        if isinstance(_remarks, Unset):
            remarks = UNSET
        else:
            remarks = IssuesLinksRemarks.from_dict(_remarks)

        _senate = d.pop("Senate", UNSET)
        senate: Union[Unset, IssuesLinksSenate]
        if isinstance(_senate, Unset):
            senate = UNSET
        else:
            senate = IssuesLinksSenate.from_dict(_senate)

        issues_links = cls(
            digest=digest,
            full_record=full_record,
            house=house,
            remarks=remarks,
            senate=senate,
        )

        issues_links.additional_properties = d
        return issues_links

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
