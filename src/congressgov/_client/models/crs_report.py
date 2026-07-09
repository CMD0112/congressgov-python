from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.crs_report_item import CrsReportItem


T = TypeVar("T", bound="CrsReport")


@_attrs_define
class CrsReport:
    """
    Attributes:
        crs_reports (Union[Unset, list['CrsReportItem']]):
    """

    crs_reports: Union[Unset, list["CrsReportItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        crs_reports: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.crs_reports, Unset):
            crs_reports = []
            for crs_reports_item_data in self.crs_reports:
                crs_reports_item = crs_reports_item_data.to_dict()
                crs_reports.append(crs_reports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if crs_reports is not UNSET:
            field_dict["CRSReports"] = crs_reports

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.crs_report_item import CrsReportItem

        d = dict(src_dict)
        crs_reports = []
        _crs_reports = d.pop("CRSReports", UNSET)
        for crs_reports_item_data in _crs_reports or []:
            crs_reports_item = CrsReportItem.from_dict(crs_reports_item_data)

            crs_reports.append(crs_reports_item)

        crs_report = cls(
            crs_reports=crs_reports,
        )

        crs_report.additional_properties = d
        return crs_report

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
