import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cbo_cost import CboCost
    from ..models.committee_report import CommitteeReport
    from ..models.law_number_actions import LawNumberActions
    from ..models.law_number_committees import LawNumberCommittees
    from ..models.law_number_cosponsors import LawNumberCosponsors
    from ..models.law_number_latest_action import LawNumberLatestAction
    from ..models.law_number_policy_area import LawNumberPolicyArea
    from ..models.law_number_subjects import LawNumberSubjects
    from ..models.law_number_summaries import LawNumberSummaries
    from ..models.law_number_text_versions import LawNumberTextVersions
    from ..models.law_number_titles import LawNumberTitles
    from ..models.laws import Laws
    from ..models.sponsor import Sponsor


T = TypeVar("T", bound="LawNumber")


@_attrs_define
class LawNumber:
    """
    Attributes:
        actions (Union[Unset, LawNumberActions]):
        cbo_cost_estimates (Union[Unset, list['CboCost']]):
        committee_reports (Union[Unset, list['CommitteeReport']]):
        committees (Union[Unset, LawNumberCommittees]):
        congress (Union[Unset, int]):  Example: 118.
        constitutional_authority_statement_text (Union[Unset, str]):  Example: <pre>
            [Congressional Record Volume 169, Number 130 (Thursday, July 27, 2023)]
            [House]
            [Pages H4143-H4144]
            From the Congressional Record Online through the Government Publishing Office [<a
            href="https://www.gpo.gov">www.gpo.gov</a>]
            By Mr. COMER:
            H.R. 4984.
            Congress has the power to enact this legislation pursuant
            to the following:
            Article I, Section 8, Clause 17 of the U.S. Constitution,
            in that the legislation ``to exercise exclusive Legislation
            in all Cases
            [[Page H4144]]
            whatsoever, over such District (not exceeding ten Miles
            square) as may, by Cession of particular States, and the
            Acceptance of Congress, become the Seat of the Government of
            the United States, and to exercise like Authority over all
            Places purchased by the Consent of the Legislature of the
            State in which the Same shall be, for the Erection of Forts,
            Magazines, Arsenals, dock-Yards, and other needful
            Buildings.''
            The single subject of this legislation is:
            To transfer administrative jurisdiction of the District of
            Columbia RFK Memorial Stadium campus from the Secretary of
            the Interior to the Administrator of General Services and
            authorize a new lease with D.C. for redevelopment.
            </pre>.
        cosponsors (Union[Unset, LawNumberCosponsors]):
        introduced_date (Union[Unset, datetime.date]):  Example: 2023-07-27.
        latest_action (Union[Unset, LawNumberLatestAction]):
        laws (Union[Unset, list['Laws']]):
        number (Union[Unset, str]):  Example: 4984.
        origin_chamber (Union[Unset, str]):  Example: House.
        origin_chamber_code (Union[Unset, str]):  Example: H.
        policy_area (Union[Unset, LawNumberPolicyArea]):
        sponsors (Union[Unset, list['Sponsor']]):
        subjects (Union[Unset, LawNumberSubjects]):
        summaries (Union[Unset, LawNumberSummaries]):
        text_versions (Union[Unset, LawNumberTextVersions]):
        title (Union[Unset, str]):  Example: D.C. Robert F. Kennedy Memorial Stadium Campus Revitalization Act.
        titles (Union[Unset, LawNumberTitles]):
        type_ (Union[Unset, str]):  Example: HR.
        update_date (Union[Unset, datetime.datetime]):  Example: 2025-05-27T14:16:54Z.
        update_date_including_text (Union[Unset, datetime.datetime]):  Example: 2025-05-27T14:16:54Z.
    """

    actions: Union[Unset, "LawNumberActions"] = UNSET
    cbo_cost_estimates: Union[Unset, list["CboCost"]] = UNSET
    committee_reports: Union[Unset, list["CommitteeReport"]] = UNSET
    committees: Union[Unset, "LawNumberCommittees"] = UNSET
    congress: Union[Unset, int] = UNSET
    constitutional_authority_statement_text: Union[Unset, str] = UNSET
    cosponsors: Union[Unset, "LawNumberCosponsors"] = UNSET
    introduced_date: Union[Unset, datetime.date] = UNSET
    latest_action: Union[Unset, "LawNumberLatestAction"] = UNSET
    laws: Union[Unset, list["Laws"]] = UNSET
    number: Union[Unset, str] = UNSET
    origin_chamber: Union[Unset, str] = UNSET
    origin_chamber_code: Union[Unset, str] = UNSET
    policy_area: Union[Unset, "LawNumberPolicyArea"] = UNSET
    sponsors: Union[Unset, list["Sponsor"]] = UNSET
    subjects: Union[Unset, "LawNumberSubjects"] = UNSET
    summaries: Union[Unset, "LawNumberSummaries"] = UNSET
    text_versions: Union[Unset, "LawNumberTextVersions"] = UNSET
    title: Union[Unset, str] = UNSET
    titles: Union[Unset, "LawNumberTitles"] = UNSET
    type_: Union[Unset, str] = UNSET
    update_date: Union[Unset, datetime.datetime] = UNSET
    update_date_including_text: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        cbo_cost_estimates: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.cbo_cost_estimates, Unset):
            cbo_cost_estimates = []
            for cbo_cost_estimates_item_data in self.cbo_cost_estimates:
                cbo_cost_estimates_item = cbo_cost_estimates_item_data.to_dict()
                cbo_cost_estimates.append(cbo_cost_estimates_item)

        committee_reports: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.committee_reports, Unset):
            committee_reports = []
            for committee_reports_item_data in self.committee_reports:
                committee_reports_item = committee_reports_item_data.to_dict()
                committee_reports.append(committee_reports_item)

        committees: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.committees, Unset):
            committees = self.committees.to_dict()

        congress = self.congress

        constitutional_authority_statement_text = self.constitutional_authority_statement_text

        cosponsors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cosponsors, Unset):
            cosponsors = self.cosponsors.to_dict()

        introduced_date: Union[Unset, str] = UNSET
        if not isinstance(self.introduced_date, Unset):
            introduced_date = self.introduced_date.isoformat()

        latest_action: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.latest_action, Unset):
            latest_action = self.latest_action.to_dict()

        laws: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.laws, Unset):
            laws = []
            for laws_item_data in self.laws:
                laws_item = laws_item_data.to_dict()
                laws.append(laws_item)

        number = self.number

        origin_chamber = self.origin_chamber

        origin_chamber_code = self.origin_chamber_code

        policy_area: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_area, Unset):
            policy_area = self.policy_area.to_dict()

        sponsors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sponsors, Unset):
            sponsors = []
            for sponsors_item_data in self.sponsors:
                sponsors_item = sponsors_item_data.to_dict()
                sponsors.append(sponsors_item)

        subjects: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.subjects, Unset):
            subjects = self.subjects.to_dict()

        summaries: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.summaries, Unset):
            summaries = self.summaries.to_dict()

        text_versions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.text_versions, Unset):
            text_versions = self.text_versions.to_dict()

        title = self.title

        titles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.titles, Unset):
            titles = self.titles.to_dict()

        type_ = self.type_

        update_date: Union[Unset, str] = UNSET
        if not isinstance(self.update_date, Unset):
            update_date = self.update_date.isoformat()

        update_date_including_text: Union[Unset, str] = UNSET
        if not isinstance(self.update_date_including_text, Unset):
            update_date_including_text = self.update_date_including_text.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if cbo_cost_estimates is not UNSET:
            field_dict["cboCostEstimates"] = cbo_cost_estimates
        if committee_reports is not UNSET:
            field_dict["committeeReports"] = committee_reports
        if committees is not UNSET:
            field_dict["committees"] = committees
        if congress is not UNSET:
            field_dict["congress"] = congress
        if constitutional_authority_statement_text is not UNSET:
            field_dict["constitutionalAuthorityStatementText"] = constitutional_authority_statement_text
        if cosponsors is not UNSET:
            field_dict["cosponsors"] = cosponsors
        if introduced_date is not UNSET:
            field_dict["introducedDate"] = introduced_date
        if latest_action is not UNSET:
            field_dict["latestAction"] = latest_action
        if laws is not UNSET:
            field_dict["laws"] = laws
        if number is not UNSET:
            field_dict["number"] = number
        if origin_chamber is not UNSET:
            field_dict["originChamber"] = origin_chamber
        if origin_chamber_code is not UNSET:
            field_dict["originChamberCode"] = origin_chamber_code
        if policy_area is not UNSET:
            field_dict["policyArea"] = policy_area
        if sponsors is not UNSET:
            field_dict["sponsors"] = sponsors
        if subjects is not UNSET:
            field_dict["subjects"] = subjects
        if summaries is not UNSET:
            field_dict["summaries"] = summaries
        if text_versions is not UNSET:
            field_dict["textVersions"] = text_versions
        if title is not UNSET:
            field_dict["title"] = title
        if titles is not UNSET:
            field_dict["titles"] = titles
        if type_ is not UNSET:
            field_dict["type"] = type_
        if update_date is not UNSET:
            field_dict["updateDate"] = update_date
        if update_date_including_text is not UNSET:
            field_dict["updateDateIncludingText"] = update_date_including_text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cbo_cost import CboCost
        from ..models.committee_report import CommitteeReport
        from ..models.law_number_actions import LawNumberActions
        from ..models.law_number_committees import LawNumberCommittees
        from ..models.law_number_cosponsors import LawNumberCosponsors
        from ..models.law_number_latest_action import LawNumberLatestAction
        from ..models.law_number_policy_area import LawNumberPolicyArea
        from ..models.law_number_subjects import LawNumberSubjects
        from ..models.law_number_summaries import LawNumberSummaries
        from ..models.law_number_text_versions import LawNumberTextVersions
        from ..models.law_number_titles import LawNumberTitles
        from ..models.laws import Laws
        from ..models.sponsor import Sponsor

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, LawNumberActions]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = LawNumberActions.from_dict(_actions)

        cbo_cost_estimates = []
        _cbo_cost_estimates = d.pop("cboCostEstimates", UNSET)
        for cbo_cost_estimates_item_data in _cbo_cost_estimates or []:
            cbo_cost_estimates_item = CboCost.from_dict(cbo_cost_estimates_item_data)

            cbo_cost_estimates.append(cbo_cost_estimates_item)

        committee_reports = []
        _committee_reports = d.pop("committeeReports", UNSET)
        for committee_reports_item_data in _committee_reports or []:
            committee_reports_item = CommitteeReport.from_dict(committee_reports_item_data)

            committee_reports.append(committee_reports_item)

        _committees = d.pop("committees", UNSET)
        committees: Union[Unset, LawNumberCommittees]
        if isinstance(_committees, Unset):
            committees = UNSET
        else:
            committees = LawNumberCommittees.from_dict(_committees)

        congress = d.pop("congress", UNSET)

        constitutional_authority_statement_text = d.pop("constitutionalAuthorityStatementText", UNSET)

        _cosponsors = d.pop("cosponsors", UNSET)
        cosponsors: Union[Unset, LawNumberCosponsors]
        if isinstance(_cosponsors, Unset):
            cosponsors = UNSET
        else:
            cosponsors = LawNumberCosponsors.from_dict(_cosponsors)

        _introduced_date = d.pop("introducedDate", UNSET)
        introduced_date: Union[Unset, datetime.date]
        if isinstance(_introduced_date, Unset) or _introduced_date is None:
            introduced_date = UNSET
        else:
            introduced_date = isoparse(_introduced_date)

        _latest_action = d.pop("latestAction", UNSET)
        latest_action: Union[Unset, LawNumberLatestAction]
        if isinstance(_latest_action, Unset):
            latest_action = UNSET
        else:
            latest_action = LawNumberLatestAction.from_dict(_latest_action)

        laws = []
        _laws = d.pop("laws", UNSET)
        for laws_item_data in _laws or []:
            laws_item = Laws.from_dict(laws_item_data)

            laws.append(laws_item)

        number = d.pop("number", UNSET)

        origin_chamber = d.pop("originChamber", UNSET)

        origin_chamber_code = d.pop("originChamberCode", UNSET)

        _policy_area = d.pop("policyArea", UNSET)
        policy_area: Union[Unset, LawNumberPolicyArea]
        if isinstance(_policy_area, Unset):
            policy_area = UNSET
        else:
            policy_area = LawNumberPolicyArea.from_dict(_policy_area)

        sponsors = []
        _sponsors = d.pop("sponsors", UNSET)
        for sponsors_item_data in _sponsors or []:
            sponsors_item = Sponsor.from_dict(sponsors_item_data)

            sponsors.append(sponsors_item)

        _subjects = d.pop("subjects", UNSET)
        subjects: Union[Unset, LawNumberSubjects]
        if isinstance(_subjects, Unset):
            subjects = UNSET
        else:
            subjects = LawNumberSubjects.from_dict(_subjects)

        _summaries = d.pop("summaries", UNSET)
        summaries: Union[Unset, LawNumberSummaries]
        if isinstance(_summaries, Unset):
            summaries = UNSET
        else:
            summaries = LawNumberSummaries.from_dict(_summaries)

        _text_versions = d.pop("textVersions", UNSET)
        text_versions: Union[Unset, LawNumberTextVersions]
        if isinstance(_text_versions, Unset):
            text_versions = UNSET
        else:
            text_versions = LawNumberTextVersions.from_dict(_text_versions)

        title = d.pop("title", UNSET)

        _titles = d.pop("titles", UNSET)
        titles: Union[Unset, LawNumberTitles]
        if isinstance(_titles, Unset):
            titles = UNSET
        else:
            titles = LawNumberTitles.from_dict(_titles)

        type_ = d.pop("type", UNSET)

        _update_date = d.pop("updateDate", UNSET)
        update_date: Union[Unset, datetime.datetime]
        if isinstance(_update_date, Unset) or _update_date is None:
            update_date = UNSET
        else:
            update_date = isoparse(_update_date)

        _update_date_including_text = d.pop("updateDateIncludingText", UNSET)
        update_date_including_text: Union[Unset, datetime.datetime]
        if isinstance(_update_date_including_text, Unset) or _update_date_including_text is None:
            update_date_including_text = UNSET
        else:
            update_date_including_text = isoparse(_update_date_including_text)

        law_number = cls(
            actions=actions,
            cbo_cost_estimates=cbo_cost_estimates,
            committee_reports=committee_reports,
            committees=committees,
            congress=congress,
            constitutional_authority_statement_text=constitutional_authority_statement_text,
            cosponsors=cosponsors,
            introduced_date=introduced_date,
            latest_action=latest_action,
            laws=laws,
            number=number,
            origin_chamber=origin_chamber,
            origin_chamber_code=origin_chamber_code,
            policy_area=policy_area,
            sponsors=sponsors,
            subjects=subjects,
            summaries=summaries,
            text_versions=text_versions,
            title=title,
            titles=titles,
            type_=type_,
            update_date=update_date,
            update_date_including_text=update_date_including_text,
        )

        law_number.additional_properties = d
        return law_number

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
