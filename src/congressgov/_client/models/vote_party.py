from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.party import Party


T = TypeVar("T", bound="VoteParty")


@_attrs_define
class VoteParty:
    """
    Attributes:
        nay_total (Union[Unset, int]):
        not_voting_total (Union[Unset, int]):  Example: 6.
        present_total (Union[Unset, int]):
        vote_party (Union[Unset, str]):  Example: R.
        yea_total (Union[Unset, int]):  Example: 213.
        party (Union[Unset, Party]):
    """

    nay_total: Union[Unset, int] = UNSET
    not_voting_total: Union[Unset, int] = UNSET
    present_total: Union[Unset, int] = UNSET
    vote_party: Union[Unset, str] = UNSET
    yea_total: Union[Unset, int] = UNSET
    party: Union[Unset, "Party"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nay_total = self.nay_total

        not_voting_total = self.not_voting_total

        present_total = self.present_total

        vote_party = self.vote_party

        yea_total = self.yea_total

        party: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.party, Unset):
            party = self.party.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nay_total is not UNSET:
            field_dict["nayTotal"] = nay_total
        if not_voting_total is not UNSET:
            field_dict["notVotingTotal"] = not_voting_total
        if present_total is not UNSET:
            field_dict["presentTotal"] = present_total
        if vote_party is not UNSET:
            field_dict["voteParty"] = vote_party
        if yea_total is not UNSET:
            field_dict["yeaTotal"] = yea_total
        if party is not UNSET:
            field_dict["party"] = party

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.party import Party

        d = dict(src_dict)
        nay_total = d.pop("nayTotal", UNSET)

        not_voting_total = d.pop("notVotingTotal", UNSET)

        present_total = d.pop("presentTotal", UNSET)

        vote_party = d.pop("voteParty", UNSET)

        yea_total = d.pop("yeaTotal", UNSET)

        _party = d.pop("party", UNSET)
        party: Union[Unset, Party]
        if isinstance(_party, Unset):
            party = UNSET
        else:
            party = Party.from_dict(_party)

        vote_party = cls(
            nay_total=nay_total,
            not_voting_total=not_voting_total,
            present_total=present_total,
            vote_party=vote_party,
            yea_total=yea_total,
            party=party,
        )

        vote_party.additional_properties = d
        return vote_party

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
