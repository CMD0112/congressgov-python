import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.committee_meeting_detail_hearing_transcript_item import CommitteeMeetingDetailHearingTranscriptItem
    from ..models.committee_meeting_detail_location import CommitteeMeetingDetailLocation
    from ..models.meetingdocument import Meetingdocument
    from ..models.related_item import RelatedItem
    from ..models.subcommittees import Subcommittees
    from ..models.video import Video
    from ..models.witness import Witness
    from ..models.witness_document import WitnessDocument


T = TypeVar("T", bound="CommitteeMeetingDetail")


@_attrs_define
class CommitteeMeetingDetail:
    """
    Attributes:
        chamber (Union[Unset, str]):  Example: House.
        committees (Union[Unset, list['Subcommittees']]):
        congress (Union[Unset, int]):  Example: 117.
        date (Union[Unset, datetime.datetime]):  Example: 2022-08-01T04:44:57Z.
        eventid (Union[Unset, str]):  Example: 115538.
        hearing_transcript (Union[Unset, list['CommitteeMeetingDetailHearingTranscriptItem']]):
        location (Union[Unset, CommitteeMeetingDetailLocation]):
        meeting_documents (Union[Unset, list['Meetingdocument']]):
        meeting_status (Union[Unset, str]):  Example: Scheduled.
        related_items (Union[Unset, list['RelatedItem']]):
        title (Union[Unset, str]):  Example: Legislative hearing on: •	H.R. 1246 (Rep. Hageman), To authorize leases of
            up to 99 years for land held in trust for federally recognized Indian tribes; and
            •	H.R. 1532 (Rep. Hageman), To authorize any Indian Tribe to lease, sell, convey, warrant, or otherwise transfer
            real property to which that Indian Tribe holds fee title without the consent of the Federal Government, and for
            other purposes..
        type_ (Union[Unset, str]):  Example: Hearing.
        update_date (Union[Unset, datetime.datetime]):  Example: 2022-08-01T04:44:57Z.
        videos (Union[Unset, list['Video']]):
        witness_documents (Union[Unset, list['WitnessDocument']]):
        witnesses (Union[Unset, list['Witness']]):
    """

    chamber: Union[Unset, str] = UNSET
    committees: Union[Unset, list["Subcommittees"]] = UNSET
    congress: Union[Unset, int] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET
    eventid: Union[Unset, str] = UNSET
    hearing_transcript: Union[Unset, list["CommitteeMeetingDetailHearingTranscriptItem"]] = UNSET
    location: Union[Unset, "CommitteeMeetingDetailLocation"] = UNSET
    meeting_documents: Union[Unset, list["Meetingdocument"]] = UNSET
    meeting_status: Union[Unset, str] = UNSET
    related_items: Union[Unset, list["RelatedItem"]] = UNSET
    title: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    videos: Union[Unset, list["Video"]] = UNSET
    witness_documents: Union[Unset, list["WitnessDocument"]] = UNSET
    witnesses: Union[Unset, list["Witness"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chamber = self.chamber

        committees: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = []
            for committees_item_data in self.committees:
                committees_item = committees_item_data.to_dict()
                committees.append(committees_item)

        congress = self.congress

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        eventid = self.eventid

        hearing_transcript: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.hearing_transcript, Unset):
            hearing_transcript = []
            for hearing_transcript_item_data in self.hearing_transcript:
                hearing_transcript_item = hearing_transcript_item_data.to_dict()
                hearing_transcript.append(hearing_transcript_item)

        location: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        meeting_documents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.meeting_documents, Unset):
            meeting_documents = []
            for meeting_documents_item_data in self.meeting_documents:
                meeting_documents_item = meeting_documents_item_data.to_dict()
                meeting_documents.append(meeting_documents_item)

        meeting_status = self.meeting_status

        related_items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.related_items, Unset):
            related_items = []
            for related_items_item_data in self.related_items:
                related_items_item = related_items_item_data.to_dict()
                related_items.append(related_items_item)

        title = self.title

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        videos: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.videos, Unset):
            videos = []
            for videos_item_data in self.videos:
                videos_item = videos_item_data.to_dict()
                videos.append(videos_item)

        witness_documents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.witness_documents, Unset):
            witness_documents = []
            for witness_documents_item_data in self.witness_documents:
                witness_documents_item = witness_documents_item_data.to_dict()
                witness_documents.append(witness_documents_item)

        witnesses: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.witnesses, Unset):
            witnesses = []
            for witnesses_item_data in self.witnesses:
                witnesses_item = witnesses_item_data.to_dict()
                witnesses.append(witnesses_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if chamber is not UNSET:
            field_dict["chamber"] = chamber
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if date is not UNSET:
            field_dict["date"] = date
        if eventid is not UNSET:
            field_dict["eventid"] = eventid
        if hearing_transcript is not UNSET:
            field_dict["hearingTranscript"] = hearing_transcript
        if location is not UNSET:
            field_dict["location"] = location
        if meeting_documents is not UNSET:
            field_dict["meetingDocuments"] = meeting_documents
        if meeting_status is not UNSET:
            field_dict["meetingStatus"] = meeting_status
        if related_items is not UNSET:
            field_dict["relatedItems"] = related_items
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if videos is not UNSET:
            field_dict["videos"] = videos
        if witness_documents is not UNSET:
            field_dict["witnessDocuments"] = witness_documents
        if witnesses is not UNSET:
            field_dict["witnesses"] = witnesses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.committee_meeting_detail_hearing_transcript_item import (
            CommitteeMeetingDetailHearingTranscriptItem,
        )
        from ..models.committee_meeting_detail_location import CommitteeMeetingDetailLocation
        from ..models.meetingdocument import Meetingdocument
        from ..models.related_item import RelatedItem
        from ..models.subcommittees import Subcommittees
        from ..models.video import Video
        from ..models.witness import Witness
        from ..models.witness_document import WitnessDocument

        d = dict(src_dict)
        chamber = d.pop("chamber", UNSET)

        committees = []
        _committees = d.pop("committees", UNSET)
        for committees_item_data in _committees or []:
            committees_item = Subcommittees.from_dict(committees_item_data)

            committees.append(committees_item)

        congress = d.pop("congress", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset) or _date is None:
            date = UNSET
        else:
            date = isoparse(_date)

        eventid = d.pop("eventid", UNSET)

        hearing_transcript = []
        _hearing_transcript = d.pop("hearingTranscript", UNSET)
        for hearing_transcript_item_data in _hearing_transcript or []:
            hearing_transcript_item = CommitteeMeetingDetailHearingTranscriptItem.from_dict(
                hearing_transcript_item_data
            )

            hearing_transcript.append(hearing_transcript_item)

        _location = d.pop("location", UNSET)
        location: Union[Unset, CommitteeMeetingDetailLocation]
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = CommitteeMeetingDetailLocation.from_dict(_location)

        meeting_documents = []
        _meeting_documents = d.pop("meetingDocuments", UNSET)
        for meeting_documents_item_data in _meeting_documents or []:
            meeting_documents_item = Meetingdocument.from_dict(meeting_documents_item_data)

            meeting_documents.append(meeting_documents_item)

        meeting_status = d.pop("meetingStatus", UNSET)

        related_items = []
        _related_items = d.pop("relatedItems", UNSET)
        for related_items_item_data in _related_items or []:
            related_items_item = RelatedItem.from_dict(related_items_item_data)

            related_items.append(related_items_item)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        videos = []
        _videos = d.pop("videos", UNSET)
        for videos_item_data in _videos or []:
            videos_item = Video.from_dict(videos_item_data)

            videos.append(videos_item)

        witness_documents = []
        _witness_documents = d.pop("witnessDocuments", UNSET)
        for witness_documents_item_data in _witness_documents or []:
            witness_documents_item = WitnessDocument.from_dict(witness_documents_item_data)

            witness_documents.append(witness_documents_item)

        witnesses = []
        _witnesses = d.pop("witnesses", UNSET)
        for witnesses_item_data in _witnesses or []:
            witnesses_item = Witness.from_dict(witnesses_item_data)

            witnesses.append(witnesses_item)

        committee_meeting_detail = cls(
            chamber=chamber,
            committees=committees,
            congress=congress,
            date=date,
            eventid=eventid,
            hearing_transcript=hearing_transcript,
            location=location,
            meeting_documents=meeting_documents,
            meeting_status=meeting_status,
            related_items=related_items,
            title=title,
            type_=type_,
            update_date=update_date,
            videos=videos,
            witness_documents=witness_documents,
            witnesses=witnesses,
        )

        committee_meeting_detail.additional_properties = d
        return committee_meeting_detail

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
