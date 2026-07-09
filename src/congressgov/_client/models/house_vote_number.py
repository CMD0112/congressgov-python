import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vote_party import VoteParty


T = TypeVar("T", bound="HouseVoteNumber")


@_attrs_define
class HouseVoteNumber:
    """
    Attributes:
        congress (Union[Unset, int]):  Example: 119.
        identifier (Union[Unset, int]):  Example: 1191202517.
        legislation_number (Union[Unset, str]):  Example: 30.
        legislation_type (Union[Unset, str]):  Example: HR.
        legislation_url (Union[Unset, str]):  Example: https://congress.gov/bill/119/house-bill/30.
        result (Union[Unset, str]):  Example: Passed.
        roll_call_number (Union[Unset, int]):  Example: 17.
        session_number (Union[Unset, int]):  Example: 1.
        source_data_url (Union[Unset, str]):  Example: https://clerk.house.gov/evs/2025/roll017.xml.
        start_date (Union[Unset, datetime.datetime]):  Example: 2025-01-16T11:00:00-05:00.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-04-18T08:44:47-04:00.
        vote_type (Union[Unset, str]):  Example: Yea-and-Nay.
        vote_party_total (Union[Unset, list['VoteParty']]):
        vote_question (Union[Unset, str]):  Example: On Passage.
    """

    congress: Union[Unset, int] = UNSET
    identifier: Union[Unset, int] = UNSET
    legislation_number: Union[Unset, str] = UNSET
    legislation_type: Union[Unset, str] = UNSET
    legislation_url: Union[Unset, str] = UNSET
    result: Union[Unset, str] = UNSET
    roll_call_number: Union[Unset, int] = UNSET
    session_number: Union[Unset, int] = UNSET
    source_data_url: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    vote_type: Union[Unset, str] = UNSET
    vote_party_total: Union[Unset, list["VoteParty"]] = UNSET
    vote_question: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        congress = self.congress

        identifier = self.identifier

        legislation_number = self.legislation_number

        legislation_type = self.legislation_type

        legislation_url = self.legislation_url

        result = self.result

        roll_call_number = self.roll_call_number

        session_number = self.session_number

        source_data_url = self.source_data_url

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        vote_type = self.vote_type

        vote_party_total: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.vote_party_total, Unset):
            vote_party_total = []
            for vote_party_total_item_data in self.vote_party_total:
                vote_party_total_item = vote_party_total_item_data.to_dict()
                vote_party_total.append(vote_party_total_item)

        vote_question = self.vote_question

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if congress is not UNSET:
            field_dict["congress"] = congress
        if identifier is not UNSET:
            field_dict["identifier"] = identifier
        if legislation_number is not UNSET:
            field_dict["legislationNumber"] = legislation_number
        if legislation_type is not UNSET:
            field_dict["legislationType"] = legislation_type
        if legislation_url is not UNSET:
            field_dict["legislationUrl"] = legislation_url
        if result is not UNSET:
            field_dict["result"] = result
        if roll_call_number is not UNSET:
            field_dict["rollCallNumber"] = roll_call_number
        if session_number is not UNSET:
            field_dict["sessionNumber"] = session_number
        if source_data_url is not UNSET:
            field_dict["sourceDataURL"] = source_data_url
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if vote_type is not UNSET:
            field_dict["voteType"] = vote_type
        if vote_party_total is not UNSET:
            field_dict["votePartyTotal"] = vote_party_total
        if vote_question is not UNSET:
            field_dict["voteQuestion"] = vote_question

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vote_party import VoteParty

        d = dict(src_dict)
        congress = d.pop("congress", UNSET)

        identifier = d.pop("identifier", UNSET)

        legislation_number = d.pop("legislationNumber", UNSET)

        legislation_type = d.pop("legislationType", UNSET)

        legislation_url = d.pop("legislationUrl", UNSET)

        result = d.pop("result", UNSET)

        roll_call_number = d.pop("rollCallNumber", UNSET)

        session_number = d.pop("sessionNumber", UNSET)

        source_data_url = d.pop("sourceDataURL", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset) or _start_date is None:
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        vote_type = d.pop("voteType", UNSET)

        vote_party_total = []
        _vote_party_total = d.pop("votePartyTotal", UNSET)
        for vote_party_total_item_data in _vote_party_total or []:
            vote_party_total_item = VoteParty.from_dict(vote_party_total_item_data)

            vote_party_total.append(vote_party_total_item)

        vote_question = d.pop("voteQuestion", UNSET)

        house_vote_number = cls(
            congress=congress,
            identifier=identifier,
            legislation_number=legislation_number,
            legislation_type=legislation_type,
            legislation_url=legislation_url,
            result=result,
            roll_call_number=roll_call_number,
            session_number=session_number,
            source_data_url=source_data_url,
            start_date=start_date,
            update_date=update_date,
            vote_type=vote_type,
            vote_party_total=vote_party_total,
            vote_question=vote_question,
        )

        house_vote_number.additional_properties = d
        return house_vote_number

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
