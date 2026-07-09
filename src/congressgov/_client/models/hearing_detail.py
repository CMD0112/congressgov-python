import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.associated_meeting import AssociatedMeeting
    from ..models.formats import Formats
    from ..models.subcommittees import Subcommittees


T = TypeVar("T", bound="HearingDetail")


@_attrs_define
class HearingDetail:
    """
    Attributes:
        associated_meeting (Union[Unset, AssociatedMeeting]):
        chamber (Union[Unset, str]):  Example: House.
        citation (Union[Unset, str]):  Example: H.Hrg.118.
        committees (Union[Unset, list['Subcommittees']]):
        congress (Union[Unset, int]):  Example: 118.
        dates (Union[Unset, list[datetime.date]]):
        formats (Union[Unset, list['Formats']]):
        jacket_number (Union[Unset, int]):  Example: 50896.
        library_of_congressidentifier (Union[Unset, str]):  Example: LC70380.
        title (Union[Unset, str]):  Example: FEDERAL PANDEMIC SPENDING: A PRESCRIPTION FOR WASTE, FRAUD AND ABUSE.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-11-04T03:21:12Z.
    """

    associated_meeting: Union[Unset, "AssociatedMeeting"] = UNSET
    chamber: Union[Unset, str] = UNSET
    citation: Union[Unset, str] = UNSET
    committees: Union[Unset, list["Subcommittees"]] = UNSET
    congress: Union[Unset, int] = UNSET
    dates: Union[Unset, list[datetime.date]] = UNSET
    formats: Union[Unset, list["Formats"]] = UNSET
    jacket_number: Union[Unset, int] = UNSET
    library_of_congressidentifier: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        associated_meeting: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.associated_meeting, Unset):
            associated_meeting = self.associated_meeting.to_dict()

        chamber = self.chamber

        citation = self.citation

        committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = []
            for committees_item_data in self.committees:
                committees_item = committees_item_data.to_dict()
                committees.append(committees_item)

        congress = self.congress

        dates: Union[Unset, list[str]] = UNSET
        if not isinstance(self.dates, Unset):
            dates = []
            for dates_item_data in self.dates:
                dates_item = dates_item_data.isoformat()
                dates.append(dates_item)

        formats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.formats, Unset):
            formats = []
            for formats_item_data in self.formats:
                formats_item = formats_item_data.to_dict()
                formats.append(formats_item)

        jacket_number = self.jacket_number

        library_of_congressidentifier = self.library_of_congressidentifier

        title = self.title

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if associated_meeting is not UNSET:
            field_dict["associatedMeeting"] = associated_meeting
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if citation is not UNSET:
            field_dict["citation"] = citation
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if dates is not UNSET:
            field_dict["dates"] = dates
        if formats is not UNSET:
            field_dict["formats"] = formats
        if jacket_number is not UNSET:
            field_dict["jacketNumber"] = jacket_number
        if library_of_congressidentifier is not UNSET:
            field_dict["libraryOfCongressidentifier"] = library_of_congressidentifier
        if title is not UNSET:
            field_dict["title"] = title
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.associated_meeting import AssociatedMeeting
        from ..models.formats import Formats
        from ..models.subcommittees import Subcommittees

        d = dict(src_dict)
        _associated_meeting = d.pop("associatedMeeting", UNSET)
        associated_meeting: Union[Unset, AssociatedMeeting]
        if isinstance(_associated_meeting, Unset):
            associated_meeting = UNSET
        else:
            associated_meeting = AssociatedMeeting.from_dict(_associated_meeting)

        chamber = d.pop("chamber", UNSET)

        citation = d.pop("citation", UNSET)

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = Subcommittees.from_dict(committees_item_data)

            committees.append(committees_item)

        congress = d.pop("congress", UNSET)

        dates = []
        _dates = d.pop("dates", UNSET)
        for dates_item_data in _dates or []:
            dates_item = isoparse(dates_item_data).date()

            dates.append(dates_item)

        formats = []
        _formats = d.pop("formats", UNSET)
        for formats_item_data in _formats or []:
            formats_item = Formats.from_dict(formats_item_data)

            formats.append(formats_item)

        jacket_number = d.pop("jacketNumber", UNSET)

        library_of_congressidentifier = d.pop("libraryOfCongressidentifier", UNSET)

        title = d.pop("title", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        hearing_detail = cls(
            associated_meeting=associated_meeting,
            chamber=chamber,
            citation=citation,
            committees=committees,
            congress=congress,
            dates=dates,
            formats=formats,
            jacket_number=jacket_number,
            library_of_congressidentifier=library_of_congressidentifier,
            title=title,
            update_date=update_date,
        )

        hearing_detail.additional_properties = d
        return hearing_detail

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
