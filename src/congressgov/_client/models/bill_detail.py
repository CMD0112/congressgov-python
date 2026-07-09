import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bill_detail_actions import BillDetailActions
    from ..models.bill_detail_committees import BillDetailCommittees
    from ..models.bill_detail_latest_action import BillDetailLatestAction
    from ..models.bill_detail_policy_area import BillDetailPolicyArea
    from ..models.sponsor import Sponsor


T = TypeVar("T", bound="BillDetail")


@_attrs_define
class BillDetail:
    """
    Attributes:
        actions (Union[Unset, BillDetailActions]):
        committees (Union[Unset, BillDetailCommittees]):
        congress (Union[Unset, int]):  Example: 117.
        introduced_date (Union[Unset, datetime.date]):  Example: 2019-01-01.
        latest_action (Union[Unset, BillDetailLatestAction]):
        legislation_url (Union[Unset, str]):  Example: https://www.congress.gov/bill/117th-congress/senate-bill/1234.
        number (Union[Unset, str]):  Example: 1234.
        origin_chamber (Union[Unset, str]):  Example: Senate.
        origin_chamber_code (Union[Unset, str]):  Example: S.
        policy_area (Union[Unset, BillDetailPolicyArea]):
        related_bills (Union[Unset, str]):  Example:
            https://api.congress.gov/v3/bill/117/s/1234/relatedbills?format=json.
        sponsors (Union[Unset, list['Sponsor']]):
    """

    actions: Union[Unset, "BillDetailActions"] = UNSET
    committees: Union[Unset, "BillDetailCommittees"] = UNSET
    congress: Union[Unset, int] = UNSET
    introduced_date: Union[Unset, datetime.date] = UNSET
    latest_action: Union[Unset, "BillDetailLatestAction"] = UNSET
    legislation_url: Union[Unset, str] = UNSET
    number: Union[Unset, str] = UNSET
    origin_chamber: Union[Unset, str] = UNSET
    origin_chamber_code: Union[Unset, str] = UNSET
    policy_area: Union[Unset, "BillDetailPolicyArea"] = UNSET
    related_bills: Union[Unset, str] = UNSET
    sponsors: Union[Unset, list["Sponsor"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        committees: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = self.committees.to_dict()

        congress = self.congress

        introduced_date: Union[Unset, str] = UNSET
        if not isinstance(self.introduced_date, Unset):
            introduced_date = self.introduced_date.isoformat()

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        legislation_url = self.legislation_url

        number = self.number

        origin_chamber = self.origin_chamber

        origin_chamber_code = self.origin_chamber_code

        policy_area: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_area, Unset):
            policy_area = self.policy_area.to_dict()

        related_bills = self.related_bills

        sponsors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sponsors, Unset):
            sponsors = []
            for sponsors_item_data in self.sponsors:
                sponsors_item = sponsors_item_data.to_dict()
                sponsors.append(sponsors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if introduced_date is not UNSET:
            field_dict["introducedDate"] = introduced_date
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if legislation_url is not UNSET:
            field_dict["legislationUrl"] = legislation_url
        if number is not UNSET:
            field_dict["number"] = number
        if origin_chamber is not UNSET:
            field_dict["originChamber"] = origin_chamber
        if origin_chamber_code is not UNSET:
            field_dict["originChamberCode"] = origin_chamber_code
        if policy_area is not UNSET:
            field_dict["policyArea"] = policy_area
        if related_bills is not UNSET:
            field_dict["relatedBills"] = related_bills
        if sponsors is not UNSET:
            field_dict["sponsors"] = sponsors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bill_detail_actions import BillDetailActions
        from ..models.bill_detail_committees import BillDetailCommittees
        from ..models.bill_detail_latest_action import BillDetailLatestAction
        from ..models.bill_detail_policy_area import BillDetailPolicyArea
        from ..models.sponsor import Sponsor

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, BillDetailActions]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = BillDetailActions.from_dict(_actions)

        _committees = d.pop("committees", UNSET)
        committees: Union[Unset, BillDetailCommittees]
        if isinstance(_committees, Unset):
            committees = UNSET
        else:
            committees = BillDetailCommittees.from_dict(_committees)

        congress = d.pop("congress", UNSET)

        _introduced_date = d.pop("introducedDate", UNSET)
        introduced_date: Union[Unset, datetime.date]
        if isinstance(_introduced_date, Unset) or _introduced_date is None:
            introduced_date = UNSET
        else:
            introduced_date = isoparse(_introduced_date)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, BillDetailLatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = BillDetailLatestAction.from_dict(_latest_action)

        legislation_url = d.pop("legislationUrl", UNSET)

        number = d.pop("number", UNSET)

        origin_chamber = d.pop("originChamber", UNSET)

        origin_chamber_code = d.pop("originChamberCode", UNSET)

        _policy_area = d.pop("policyArea", UNSET)
        policy_area: Union[Unset, BillDetailPolicyArea]
        if isinstance(_policy_area, Unset):
            policy_area = UNSET
        else:
            policy_area = BillDetailPolicyArea.from_dict(_policy_area)

        related_bills = d.pop("relatedBills", UNSET)

        sponsors = []
        _sponsors = d.pop("sponsors", UNSET)
        for sponsors_item_data in _sponsors or []:
            sponsors_item = Sponsor.from_dict(sponsors_item_data)

            sponsors.append(sponsors_item)

        bill_detail = cls(
            actions=actions,
            committees=committees,
            congress=congress,
            introduced_date=introduced_date,
            latest_action=latest_action,
            legislation_url=legislation_url,
            number=number,
            origin_chamber=origin_chamber,
            origin_chamber_code=origin_chamber_code,
            policy_area=policy_area,
            related_bills=related_bills,
            sponsors=sponsors,
        )

        bill_detail.additional_properties = d
        return bill_detail

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
