import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.amended_bill import AmendedBill
    from ..models.amendment_number_actions import AmendmentNumberActions
    from ..models.sponsor import Sponsor
    from ..models.text_version import TextVersion


T = TypeVar("T", bound="AmendmentNumber")


@_attrs_define
class AmendmentNumber:
    """
    Attributes:
        actions (Union[Unset, AmendmentNumberActions]):
        amended_bill (Union[Unset, AmendedBill]):
        chamber (Union[Unset, str]):
        congress (Union[Unset, int]):  Example: 117.
        number (Union[Unset, str]):  Example: 2137.
        sponsors (Union[Unset, list['Sponsor']]):
        submitted_date (Union[Unset, datetime.datetime]):  Example: 2021-02-02T05:00:00Z.
        text_versions (Union[Unset, TextVersion]):
        type_ (Union[Unset, str]):
        update_date (Union[Unset, datetime.datetime]):  Example: 2021-08-08T12:00:00Z.
    """

    actions: Union[Unset, "AmendmentNumberActions"] = UNSET
    amended_bill: Union[Unset, "AmendedBill"] = UNSET
    chamber: Union[Unset, str] = UNSET
    congress: Union[Unset, int] = UNSET
    number: Union[Unset, str] = UNSET
    sponsors: Union[Unset, list["Sponsor"]] = UNSET
    submitted_date: Union[Unset, datetime.datetime] = UNSET
    text_versions: Union[Unset, "TextVersion"] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        amended_bill: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.amended_bill, Unset):
            amended_bill = self.amended_bill.to_dict()

        chamber = self.chamber

        congress = self.congress

        number = self.number

        sponsors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sponsors, Unset):
            sponsors = []
            for sponsors_item_data in self.sponsors:
                sponsors_item = sponsors_item_data.to_dict()
                sponsors.append(sponsors_item)

        submitted_date: Union[Unset, str] = UNSET
        if not isinstance(self.submitted_date, Unset):
            submitted_date = self.submitted_date.isoformat()

        text_versions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.text_versions, Unset):
            text_versions = self.text_versions.to_dict()

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if amended_bill is not UNSET:
            field_dict["amendedBill"] = amended_bill
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if congress is not UNSET:
            field_dict["congress"] = congress
        if number is not UNSET:
            field_dict["number"] = number
        if sponsors is not UNSET:
            field_dict["sponsors"] = sponsors
        if submitted_date is not UNSET:
            field_dict["submittedDate"] = submitted_date
        if text_versions is not UNSET:
            field_dict["textVersions"] = text_versions
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.amended_bill import AmendedBill
        from ..models.amendment_number_actions import AmendmentNumberActions
        from ..models.sponsor import Sponsor
        from ..models.text_version import TextVersion

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, AmendmentNumberActions]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = AmendmentNumberActions.from_dict(_actions)

        _amended_bill = d.pop("amendedBill", UNSET)
        amended_bill: Union[Unset, AmendedBill]
        if isinstance(_amended_bill, Unset):
            amended_bill = UNSET
        else:
            amended_bill = AmendedBill.from_dict(_amended_bill)

        chamber = d.pop("chamber", UNSET)

        congress = d.pop("congress", UNSET)

        number = d.pop("number", UNSET)

        sponsors = []
        _sponsors = d.pop("sponsors", UNSET)
        for sponsors_item_data in _sponsors or []:
            sponsors_item = Sponsor.from_dict(sponsors_item_data)

            sponsors.append(sponsors_item)

        _submitted_date = d.pop("submittedDate", UNSET)
        submitted_date: Union[Unset, datetime.datetime]
        if isinstance(_submitted_date, Unset) or _submitted_date is None:
            submitted_date = UNSET
        else:
            submitted_date = isoparse(_submitted_date)

        _text_versions = d.pop("textVersions", UNSET)
        text_versions: Union[Unset, TextVersion]
        if isinstance(_text_versions, Unset):
            text_versions = UNSET
        else:
            text_versions = TextVersion.from_dict(_text_versions)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        amendment_number = cls(
            actions=actions,
            amended_bill=amended_bill,
            chamber=chamber,
            congress=congress,
            number=number,
            sponsors=sponsors,
            submitted_date=submitted_date,
            text_versions=text_versions,
            type_=type_,
            update_date=update_date,
        )

        amendment_number.additional_properties = d
        return amendment_number

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
