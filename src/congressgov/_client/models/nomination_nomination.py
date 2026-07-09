import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nomination_nomination_actions import NominationNominationActions
    from ..models.nomination_nomination_committees import NominationNominationCommittees
    from ..models.nomination_nomination_hearings import NominationNominationHearings
    from ..models.nomination_nomination_latest_action import NominationNominationLatestAction
    from ..models.nomination_type import NominationType
    from ..models.nominee import Nominee


T = TypeVar("T", bound="NominationNomination")


@_attrs_define
class NominationNomination:
    """
    Attributes:
        actions (Union[Unset, NominationNominationActions]):
        authority_date (Union[Unset, datetime.date]):  Example: 2025-10-21.
        citation (Union[Unset, str]):  Example: PN16.
        committees (Union[Unset, NominationNominationCommittees]):
        congress (Union[Unset, int]):  Example: 118.
        description (Union[Unset, str]):  Example: Daniel B. Maffei, of New York, to be a Federal Maritime Commissioner
            for a term expiring June 30, 2027.  (Reappointment).
        hearings (Union[Unset, NominationNominationHearings]):
        latest_action (Union[Unset, NominationNominationLatestAction]):
        nomination_type (Union[Unset, NominationType]):
        nominees (Union[Unset, list['Nominee']]):
        number (Union[Unset, int]):  Example: 16.
        part_number (Union[Unset, str]):  Example: 00.
        received_date (Union[Unset, datetime.date]):  Example: 2023-01-03.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-10-22T15:58:44Z.
    """

    actions: Union[Unset, "NominationNominationActions"] = UNSET
    authority_date: Union[Unset, datetime.date] = UNSET
    citation: Union[Unset, str] = UNSET
    committees: Union[Unset, "NominationNominationCommittees"] = UNSET
    congress: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    hearings: Union[Unset, "NominationNominationHearings"] = UNSET
    latest_action: Union[Unset, "NominationNominationLatestAction"] = UNSET
    nomination_type: Union[Unset, "NominationType"] = UNSET
    nominees: Union[Unset, list["Nominee"]] = UNSET
    number: Union[Unset, int] = UNSET
    part_number: Union[Unset, str] = UNSET
    received_date: Union[Unset, datetime.date] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        authority_date: Union[Unset, str] = UNSET
        if not isinstance(self.authority_date, Unset):
            authority_date = self.authority_date.isoformat()

        citation = self.citation

        committees: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = self.committees.to_dict()

        congress = self.congress

        description = self.description

        hearings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.hearings, Unset):
            hearings = self.hearings.to_dict()

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        nomination_type: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.nomination_type, Unset):
            nomination_type = self.nomination_type.to_dict()

        nominees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nominees, Unset):
            nominees = []
            for nominees_item_data in self.nominees:
                nominees_item = nominees_item_data.to_dict()
                nominees.append(nominees_item)

        number = self.number

        part_number = self.part_number

        received_date: Union[Unset, str] = UNSET
        if not isinstance(self.received_date, Unset):
            received_date = self.received_date.isoformat()

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if authority_date is not UNSET:
            field_dict["authorityDate"] = authority_date
        if citation is not UNSET:
            field_dict["citation"] = citation
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if description is not UNSET:
            field_dict["description"] = description
        if hearings is not UNSET:
            field_dict["hearings"] = hearings
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if nomination_type is not UNSET:
            field_dict["nominationType"] = nomination_type
        if nominees is not UNSET:
            field_dict["nominees"] = nominees
        if number is not UNSET:
            field_dict["number"] = number
        if part_number is not UNSET:
            field_dict["partNumber"] = part_number
        if received_date is not UNSET:
            field_dict["receivedDate"] = received_date
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nomination_nomination_actions import NominationNominationActions
        from ..models.nomination_nomination_committees import NominationNominationCommittees
        from ..models.nomination_nomination_hearings import NominationNominationHearings
        from ..models.nomination_nomination_latest_action import NominationNominationLatestAction
        from ..models.nomination_type import NominationType
        from ..models.nominee import Nominee

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, NominationNominationActions]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = NominationNominationActions.from_dict(_actions)

        _authority_date = d.pop("authorityDate", UNSET)
        authority_date: Union[Unset, datetime.date]
        if isinstance(_authority_date, Unset) or _authority_date is None:
            authority_date = UNSET
        else:
            authority_date = isoparse(_authority_date)

        citation = d.pop("citation", UNSET)

        _committees = d.pop("committees", UNSET)
        committees: Union[Unset, NominationNominationCommittees]
        if isinstance(_committees, Unset):
            committees = UNSET
        else:
            committees = NominationNominationCommittees.from_dict(_committees)

        congress = d.pop("congress", UNSET)

        description = d.pop("description", UNSET)

        _hearings = d.pop("hearings", UNSET)
        hearings: Union[Unset, NominationNominationHearings]
        if isinstance(_hearings, Unset):
            hearings = UNSET
        else:
            hearings = NominationNominationHearings.from_dict(_hearings)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, NominationNominationLatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = NominationNominationLatestAction.from_dict(_latest_action)

        _nomination_type = d.pop("nominationType", UNSET)
        nomination_type: Union[Unset, NominationType]
        if isinstance(_nomination_type, Unset):
            nomination_type = UNSET
        else:
            nomination_type = NominationType.from_dict(_nomination_type)

        nominees = []
        _nominees = d.pop("nominees", UNSET)
        for nominees_item_data in _nominees or []:
            nominees_item = Nominee.from_dict(nominees_item_data)

            nominees.append(nominees_item)

        number = d.pop("number", UNSET)

        part_number = d.pop("partNumber", UNSET)

        _received_date = d.pop("receivedDate", UNSET)
        received_date: Union[Unset, datetime.date]
        if isinstance(_received_date, Unset) or _received_date is None:
            received_date = UNSET
        else:
            received_date = isoparse(_received_date)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        nomination_nomination = cls(
            actions=actions,
            authority_date=authority_date,
            citation=citation,
            committees=committees,
            congress=congress,
            description=description,
            hearings=hearings,
            latest_action=latest_action,
            nomination_type=nomination_type,
            nominees=nominees,
            number=number,
            part_number=part_number,
            received_date=received_date,
            update_date=update_date,
        )

        nomination_nomination.additional_properties = d
        return nomination_nomination

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
