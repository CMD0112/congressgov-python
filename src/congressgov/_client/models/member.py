import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.leadership import Leadership
    from ..models.member_cosponsored_legislation import MemberCosponsoredLegislation
    from ..models.member_depiction import MemberDepiction
    from ..models.member_detail_terms import MemberDetailTerms
    from ..models.member_sponsored_legislation import MemberSponsoredLegislation
    from ..models.party_history import PartyHistory


T = TypeVar("T", bound="Member")


@_attrs_define
class Member:
    """
    Attributes:
        bioguide_id (Union[Unset, str]):  Example: L000174.
        birth_year (Union[Unset, str]):  Example: 1940.
        cosponsored_legislation (Union[Unset, MemberCosponsoredLegislation]):
        depiction (Union[Unset, MemberDepiction]):
        direct_order_name (Union[Unset, str]):  Example: Patrick J. Leahy.
        first_name (Union[Unset, str]):  Example: Patrick.
        honorific_name (Union[Unset, str]):  Example: Mr..
        inverted_order_name (Union[Unset, str]):  Example: Leahy, Patrick J..
        lastname (Union[Unset, str]):  Example: Leahy.
        leadership (Union[Unset, list['Leadership']]):
        party_history (Union[Unset, list['PartyHistory']]):
        sponsored_legislation (Union[Unset, MemberSponsoredLegislation]):
        state (Union[Unset, str]):  Example: Vermont.
        terms (Union[Unset, list['MemberDetailTerms']]):
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-11-07T13:42:19Z.
    """

    bioguide_id: Union[Unset, str] = UNSET
    birth_year: Union[Unset, str] = UNSET
    cosponsored_legislation: Union[Unset, "MemberCosponsoredLegislation"] = UNSET
    depiction: Union[Unset, "MemberDepiction"] = UNSET
    direct_order_name: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    honorific_name: Union[Unset, str] = UNSET
    inverted_order_name: Union[Unset, str] = UNSET
    lastname: Union[Unset, str] = UNSET
    leadership: Union[Unset, list["Leadership"]] = UNSET
    party_history: Union[Unset, list["PartyHistory"]] = UNSET
    sponsored_legislation: Union[Unset, "MemberSponsoredLegislation"] = UNSET
    state: Union[Unset, str] = UNSET
    terms: Union[Unset, list["MemberDetailTerms"]] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bioguide_id = self.bioguide_id

        birth_year = self.birth_year

        cosponsored_legislation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cosponsored_legislation, Unset):
            cosponsored_legislation = self.cosponsored_legislation.to_dict()

        depiction: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.depiction, Unset):
            depiction = self.depiction.to_dict()

        direct_order_name = self.direct_order_name

        first_name = self.first_name

        honorific_name = self.honorific_name

        inverted_order_name = self.inverted_order_name

        lastname = self.lastname

        leadership: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.leadership, Unset):
            leadership = []
            for leadership_item_data in self.leadership:
                leadership_item = leadership_item_data.to_dict()
                leadership.append(leadership_item)

        party_history: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.party_history, Unset):
            party_history = []
            for party_history_item_data in self.party_history:
                party_history_item = party_history_item_data.to_dict()
                party_history.append(party_history_item)

        sponsored_legislation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sponsored_legislation, Unset):
            sponsored_legislation = self.sponsored_legislation.to_dict()

        state = self.state

        terms: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.terms, Unset):
            terms = []
            for terms_item_data in self.terms:
                terms_item = terms_item_data.to_dict()
                terms.append(terms_item)

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bioguide_id is not UNSET:
            field_dict["bioguideId"] = bioguide_id
        if birth_year is not UNSET:
            field_dict["birthYear"] = birth_year
        if cosponsored_legislation is not UNSET:
            field_dict["cosponsoredLegislation"] = cosponsored_legislation
        if depiction is not UNSET:
            field_dict["depiction"] = depiction
        if direct_order_name is not UNSET:
            field_dict["directOrderName"] = direct_order_name
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if honorific_name is not UNSET:
            field_dict["honorificName"] = honorific_name
        if inverted_order_name is not UNSET:
            field_dict["invertedOrderName"] = inverted_order_name
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if leadership is not UNSET:
            field_dict["leadership"] = leadership
        if party_history is not UNSET:
            field_dict["partyHistory"] = party_history
        if sponsored_legislation is not UNSET:
            field_dict["sponsoredLegislation"] = sponsored_legislation
        if state is not UNSET:
            field_dict["state"] = state
        if terms is not UNSET:
            field_dict["terms"] = terms
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.leadership import Leadership
        from ..models.member_cosponsored_legislation import MemberCosponsoredLegislation
        from ..models.member_depiction import MemberDepiction
        from ..models.member_detail_terms import MemberDetailTerms
        from ..models.member_sponsored_legislation import MemberSponsoredLegislation
        from ..models.party_history import PartyHistory

        d = dict(src_dict)
        bioguide_id = d.pop("bioguideId", UNSET)

        birth_year = d.pop("birthYear", UNSET)

        _cosponsored_legislation = d.pop("cosponsoredLegislation", UNSET)
        cosponsored_legislation: Union[Unset, MemberCosponsoredLegislation]
        if isinstance(_cosponsored_legislation, Unset):
            cosponsored_legislation = UNSET
        else:
            cosponsored_legislation = MemberCosponsoredLegislation.from_dict(_cosponsored_legislation)

        _depiction = d.pop("depiction", UNSET)
        depiction: Union[Unset, MemberDepiction]
        if isinstance(_depiction, Unset):
            depiction = UNSET
        else:
            depiction = MemberDepiction.from_dict(_depiction)

        direct_order_name = d.pop("directOrderName", UNSET)

        first_name = d.pop("firstName", UNSET)

        honorific_name = d.pop("honorificName", UNSET)

        inverted_order_name = d.pop("invertedOrderName", UNSET)

        lastname = d.pop("lastname", UNSET)

        leadership = []
        _leadership = d.pop("leadership", UNSET)
        for leadership_item_data in _leadership or []:
            leadership_item = Leadership.from_dict(leadership_item_data)

            leadership.append(leadership_item)

        party_history = []
        _party_history = d.pop("partyHistory", UNSET)
        for party_history_item_data in _party_history or []:
            party_history_item = PartyHistory.from_dict(party_history_item_data)

            party_history.append(party_history_item)

        _sponsored_legislation = d.pop("sponsoredLegislation", UNSET)
        sponsored_legislation: Union[Unset, MemberSponsoredLegislation]
        if isinstance(_sponsored_legislation, Unset):
            sponsored_legislation = UNSET
        else:
            sponsored_legislation = MemberSponsoredLegislation.from_dict(_sponsored_legislation)

        state = d.pop("state", UNSET)

        terms = []
        _terms = d.pop("terms", UNSET)
        for terms_item_data in _terms or []:
            terms_item = MemberDetailTerms.from_dict(terms_item_data)

            terms.append(terms_item)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        member = cls(
            bioguide_id=bioguide_id,
            birth_year=birth_year,
            cosponsored_legislation=cosponsored_legislation,
            depiction=depiction,
            direct_order_name=direct_order_name,
            first_name=first_name,
            honorific_name=honorific_name,
            inverted_order_name=inverted_order_name,
            lastname=lastname,
            leadership=leadership,
            party_history=party_history,
            sponsored_legislation=sponsored_legislation,
            state=state,
            terms=terms,
            update_date=update_date,
        )

        member.additional_properties = d
        return member

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
