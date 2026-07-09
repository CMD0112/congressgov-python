import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.author import Author
    from ..models.format_ import Format
    from ..models.related_material import RelatedMaterial
    from ..models.topic import Topic


T = TypeVar("T", bound="CrsReportDetail")


@_attrs_define
class CrsReportDetail:
    """
    Attributes:
        authors (Union[Unset, list['Author']]):
        content_type (Union[Unset, str]):  Example: Reports.
        formats (Union[Unset, list['Format']]):
        id (Union[Unset, str]):  Example: R47175.
        publish_date (Union[Unset, datetime.datetime]):  Example: 2022-07-11T04:00:00Z.
        related_materials (Union[Unset, list['RelatedMaterial']]):
        status (Union[Unset, str]):  Example: Active.
        summary (Union[Unset, str]):  Example: The Congressional Budget Act of 1974 directs Congress to adopt a budget
            resolution each spring, providing an agreement between the House and Senate on a budget plan for the upcoming
            fiscal year (and at least four additional years). The annual budget resolution includes certain spending and
            revenue levels that become enforceable through points of order once both chambers have adopted the resolution.
            Congress does not always adopt a budget resolution, however, and this may complicate the development and
            consideration of budgetary legislation. Congress has, therefore, developed an alternative legislative tool,
            typically referred to as a “deeming resolution” because it is deemed to serve in place of an annual budget
            resolution for the purposes of establishing enforceable budgetary levels.
            On June 8, 2022, the House of Representatives adopted H.Res. 1151, a deeming resolution for FY2023. H.Res. 1151
            provided a committee spending allocation (302(a) allocation) to the House Appropriations Committee ($1.603
            trillion). It also directed the chair of the House Budget Committee to subsequently file a statement in the
            Congressional Record that includes committee spending allocations for all other committees, as well as aggregate
            spending and revenue levels. (Those levels were filed on June 21, 2022.) H.Res. 1151 specified that the levels
            filed in the Congressional Record be consistent with the “most recent baseline of the Congressional Budget
            Office,” meaning that the committee spending allocations (other than for the Appropriations Committee) and the
            aggregate spending and revenue levels have been set at the levels currently projected under current law.
            In addition to providing enforceable budgetary levels within the House, H.Res. 1151 grants authority to the
            chair of the House Budget Committee to “adjust” the budgetary levels provided under the deeming resolution in
            the future under specified circumstances. In addition, the resolution states that provisions designated as
            “emergency” shall be effectively exempt from House budgetary rules and specifies that certain accounts may
            receive advance appropriations for FY2024 and FY2025.
            .
        title (Union[Unset, str]):  Example: Settings Budgetary Levels: The House's FY2023 Deeming Resolution.
        topics (Union[Unset, list['Topic']]):
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-06-20T23:46:23Z.
        url (Union[Unset, str]):  Example: www.congress.gov/crs-report/R47175.
        version (Union[Unset, int]):  Example: 1.
    """

    authors: Union[Unset, list["Author"]] = UNSET
    content_type: Union[Unset, str] = UNSET
    formats: Union[Unset, list["Format"]] = UNSET
    id: Union[Unset, str] = UNSET
    publish_date: Union[Unset, datetime.datetime] = UNSET
    related_materials: Union[Unset, list["RelatedMaterial"]] = UNSET
    status: Union[Unset, str] = UNSET
    summary: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    topics: Union[Unset, list["Topic"]] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    version: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authors, Unset):
            authors = []
            for authors_item_data in self.authors:
                authors_item = authors_item_data.to_dict()
                authors.append(authors_item)

        content_type = self.content_type

        formats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.formats, Unset):
            formats = []
            for formats_item_data in self.formats:
                formats_item = formats_item_data.to_dict()
                formats.append(formats_item)

        id = self.id

        publish_date: Union[Unset, str] = UNSET
        if not isinstance(self.publish_date, Unset):
            publish_date = self.publish_date.isoformat()

        related_materials: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.related_materials, Unset):
            related_materials = []
            for related_materials_item_data in self.related_materials:
                related_materials_item = related_materials_item_data.to_dict()
                related_materials.append(related_materials_item)

        status = self.status

        summary = self.summary

        title = self.title

        topics: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.topics, Unset):
            topics = []
            for topics_item_data in self.topics:
                topics_item = topics_item_data.to_dict()
                topics.append(topics_item)

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        url = self.url

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authors is not UNSET:
            field_dict["authors"] = authors
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if formats is not UNSET:
            field_dict["formats"] = formats
        if id is not UNSET:
            field_dict["id"] = id
        if publish_date is not UNSET:
            field_dict["publishDate"] = publish_date
        if related_materials is not UNSET:
            field_dict["relatedMaterials"] = related_materials
        if status is not UNSET:
            field_dict["status"] = status
        if summary is not UNSET:
            field_dict["summary"] = summary
        if title is not UNSET:
            field_dict["title"] = title
        if topics is not UNSET:
            field_dict["topics"] = topics
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if url is not UNSET:
            field_dict["url"] = url
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.author import Author
        from ..models.format_ import Format
        from ..models.related_material import RelatedMaterial
        from ..models.topic import Topic

        d = dict(src_dict)
        authors = []
        _authors = d.pop("authors", UNSET)
        for authors_item_data in _authors or []:
            authors_item = Author.from_dict(authors_item_data)

            authors.append(authors_item)

        content_type = d.pop("contentType", UNSET)

        formats = []
        _formats = d.pop("formats", UNSET)
        for formats_item_data in _formats or []:
            formats_item = Format.from_dict(formats_item_data)

            formats.append(formats_item)

        id = d.pop("id", UNSET)

        _publish_date = d.pop("publishDate", UNSET)
        publish_date: Union[Unset, datetime.datetime]
        if isinstance(_publish_date, Unset) or _publish_date is None:
            publish_date = UNSET
        else:
            publish_date = isoparse(_publish_date)

        related_materials = []
        _related_materials = d.pop("relatedMaterials", UNSET)
        for related_materials_item_data in _related_materials or []:
            related_materials_item = RelatedMaterial.from_dict(related_materials_item_data)

            related_materials.append(related_materials_item)

        status = d.pop("status", UNSET)

        summary = d.pop("summary", UNSET)

        title = d.pop("title", UNSET)

        topics = []
        _topics = d.pop("topics", UNSET)
        for topics_item_data in _topics or []:
            topics_item = Topic.from_dict(topics_item_data)

            topics.append(topics_item)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        url = d.pop("url", UNSET)

        version = d.pop("version", UNSET)

        crs_report_detail = cls(
            authors=authors,
            content_type=content_type,
            formats=formats,
            id=id,
            publish_date=publish_date,
            related_materials=related_materials,
            status=status,
            summary=summary,
            title=title,
            topics=topics,
            update_date=update_date,
            url=url,
            version=version,
        )

        crs_report_detail.additional_properties = d
        return crs_report_detail

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
