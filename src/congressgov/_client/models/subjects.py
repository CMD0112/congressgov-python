from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.legislative_subjects import LegislativeSubjects
    from ..models.policy_area import PolicyArea


T = TypeVar("T", bound="Subjects")


@_attrs_define
class Subjects:
    """
    Attributes:
        legislative_subjects (Union[Unset, list['LegislativeSubjects']]):
        policy_area (Union[Unset, PolicyArea]):
    """

    legislative_subjects: Union[Unset, list["LegislativeSubjects"]] = UNSET
    policy_area: Union[Unset, "PolicyArea"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        legislative_subjects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.legislative_subjects, Unset):
            legislative_subjects = []
            for legislative_subjects_item_data in self.legislative_subjects:
                legislative_subjects_item = legislative_subjects_item_data.to_dict()
                legislative_subjects.append(legislative_subjects_item)

        policy_area: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_area, Unset):
            policy_area = self.policy_area.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if legislative_subjects is not UNSET:
            field_dict["legislativeSubjects"] = legislative_subjects
        if policy_area is not UNSET:
            field_dict["policyArea"] = policy_area

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.legislative_subjects import LegislativeSubjects
        from ..models.policy_area import PolicyArea

        d = dict(src_dict)
        legislative_subjects = []
        _legislative_subjects = d.pop("legislativeSubjects", UNSET)
        for legislative_subjects_item_data in _legislative_subjects or []:
            legislative_subjects_item = LegislativeSubjects.from_dict(legislative_subjects_item_data)

            legislative_subjects.append(legislative_subjects_item)

        _policy_area = d.pop("policyArea", UNSET)
        policy_area: Union[Unset, PolicyArea]
        if isinstance(_policy_area, Unset):
            policy_area = UNSET
        else:
            policy_area = PolicyArea.from_dict(_policy_area)

        subjects = cls(
            legislative_subjects=legislative_subjects,
            policy_area=policy_area,
        )

        subjects.additional_properties = d
        return subjects

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
