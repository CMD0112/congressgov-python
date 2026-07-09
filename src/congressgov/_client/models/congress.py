from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sessions import Sessions


T = TypeVar("T", bound="Congress")


@_attrs_define
class Congress:
    """
    Attributes:
        end_year (Union[Unset, str]):  Example: 2022.
        name (Union[Unset, str]):  Example: 117th Congress.
        sessions (Union[Unset, list['Sessions']]):
        start_year (Union[Unset, str]):  Example: 2021.
    """

    end_year: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    sessions: Union[Unset, list["Sessions"]] = UNSET
    start_year: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_year = self.end_year

        name = self.name

        sessions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sessions, Unset):
            sessions = []
            for sessions_item_data in self.sessions:
                sessions_item = sessions_item_data.to_dict()
                sessions.append(sessions_item)

        start_year = self.start_year

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if end_year is not UNSET:
            field_dict["endYear"] = end_year
        if name is not UNSET:
            field_dict["name"] = name
        if sessions is not UNSET:
            field_dict["sessions"] = sessions
        if start_year is not UNSET:
            field_dict["startYear"] = start_year

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sessions import Sessions

        d = dict(src_dict)
        end_year = d.pop("endYear", UNSET)

        name = d.pop("name", UNSET)

        sessions = []
        _sessions = d.pop("sessions", UNSET)
        for sessions_item_data in _sessions or []:
            sessions_item = Sessions.from_dict(sessions_item_data)

            sessions.append(sessions_item)

        start_year = d.pop("startYear", UNSET)

        congress = cls(
            end_year=end_year,
            name=name,
            sessions=sessions,
            start_year=start_year,
        )

        congress.additional_properties = d
        return congress

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
