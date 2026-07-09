from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HouseVoteResults")


@_attrs_define
class HouseVoteResults:
    """
    Attributes:
        bioguide_id (Union[Unset, str]):  Example: A000055.
        first_name (Union[Unset, str]):  Example: Robert.
        last_name (Union[Unset, str]):  Example: Aderholt.
        vote_cast (Union[Unset, str]):  Example: Yea.
        vote_party (Union[Unset, str]):  Example: R.
        vote_state (Union[Unset, str]):  Example: AL.
    """

    bioguide_id: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    vote_cast: Union[Unset, str] = UNSET
    vote_party: Union[Unset, str] = UNSET
    vote_state: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bioguide_id = self.bioguide_id

        first_name = self.first_name

        last_name = self.last_name

        vote_cast = self.vote_cast

        vote_party = self.vote_party

        vote_state = self.vote_state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bioguide_id is not UNSET:
            field_dict["bioguideID"] = bioguide_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if vote_cast is not UNSET:
            field_dict["voteCast"] = vote_cast
        if vote_party is not UNSET:
            field_dict["voteParty"] = vote_party
        if vote_state is not UNSET:
            field_dict["voteState"] = vote_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bioguide_id = d.pop("bioguideID", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        vote_cast = d.pop("voteCast", UNSET)

        vote_party = d.pop("voteParty", UNSET)

        vote_state = d.pop("voteState", UNSET)

        house_vote_results = cls(
            bioguide_id=bioguide_id,
            first_name=first_name,
            last_name=last_name,
            vote_cast=vote_cast,
            vote_party=vote_party,
            vote_state=vote_state,
        )

        house_vote_results.additional_properties = d
        return house_vote_results

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
