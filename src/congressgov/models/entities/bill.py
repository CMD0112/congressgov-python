from __future__ import annotations
from typing import List, Any, TYPE_CHECKING
from datetime import date as DateType, datetime
from pydantic import Field, AliasChoices, model_validator
from ..base.model import Model

# Import protocols for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    from congressgov.services.protocols.bill import BillProtocol, BillsProtocol
    from congressgov.services.protocols.async_bill import AsyncBillProtocol
    from ..entities.amendment import Amendment
from ..base.enums import Chamber, LegislationType, TextVersionType
from ..base.types import CountRef, URL, PolicyArea
from ..base.references import CommitteeRef, AmendmentRef
from ..core.core import Title, Law, Subject, CBOCostEstimate, Note
from ..actions.action import LatestAction, Action
from ..entities.sponsor import Sponsor, Cosponsor, Cosponsors, OnBehalfOfSponsor

# Summary classes moved here to avoid circular imports

# Law, Laws, Subject, Subjects, CBOCostEstimate, CBOCostEstimates classes moved to classes.core.core to avoid circular imports


class Summary(Model):
    """
    Congressional Research Service (CRS) summary of a bill.
    
    CRS provides objective, nonpartisan summaries of legislation at various
    stages of the legislative process. Summaries may be updated as bills progress.
    
    Example:
        >>> summary = Summary(
        ...     text="This bill amends the Clean Air Act...",
        ...     actionDate=date(2023, 1, 15),
        ...     versionCode="00"
        ... )
    """
    
    bill: "Bill | None" = Field(
        default=None,
        description="Reference to the bill this summary describes"
    )
    
    text: str | None = Field(
        default=None,
        description="Full text of the CRS summary"
    )
    
    actionDate: DateType | None = Field(
        default=None,
        description="Date of the legislative action associated with this summary"
    )
    
    updateDate: datetime | None = Field(
        default=None,
        description="Date and time when this summary was last updated"
    )
    
    currentChamber: Chamber | str | None = Field(
        default=None,
        description="Chamber where the bill currently resides (House or Senate)"
    )
    
    currentChamberCode: str | None = Field(
        default=None,
        description="Chamber code where bill currently resides ('H' or 'S')"
    )
    
    actionDesc: str | None = Field(
        default=None,
        description="Description of the action associated with this summary"
    )
    
    versionCode: str | None = Field(
        default=None,
        description="CRS version code indicating the type of summary (e.g., '00' for Introduced, '36' for Passed House)"
    )
    
    lastSummaryUpdateDate: datetime | None = Field(
        default=None,
        description="Most recent date and time any summary for this bill was updated"
    )


class Summaries(Model):
    """
    Container for a list of bill summaries.
    
    Represents the collection of all CRS summaries for a bill across
    different versions and stages of the legislative process.
    
    Example:
        >>> summaries = Summaries(summaries=[
        ...     Summary(text="Introduced version summary", versionCode="00"),
        ...     Summary(text="Passed House summary", versionCode="36")
        ... ])
    """
    summaries: list[Summary] | None = Field(
        default=None,
        alias="summaries",
        description="List of Summary objects for a bill"
    )


class ConstitutionalAuthorityStatement(Model):
    """
    Constitutional authority statement for a bill.
    
    House Rule XII, clause 7(c) requires that each bill or joint resolution
    include a statement citing the specific constitutional authority for
    enacting the proposed law.
    
    Example:
        >>> statement = ConstitutionalAuthorityStatement(
        ...     text="Congress has the power to enact this legislation pursuant to Article I, Section 8...",
        ...     submitted_date=date(2023, 1, 9)
        ... )
    """
    text: str | None = Field(
        default=None,
        description="Full text of the constitutional authority statement"
    )
    
    submitted_date: DateType | None = Field(
        default=None,
        description="Date when the constitutional authority statement was submitted"
    )


# ConstitutionalAuthorityStatement.model_rebuild()  # Handled by centralized rebuild system


# Title and Titles classes moved to classes.core.core to avoid circular imports


class TextVersionFormat(Model):
    """
    Format information for a specific version of bill text.
    
    Bill text is available in multiple formats (PDF, XML, HTML, etc.).
    Each format has a URL for downloading or viewing the text.
    
    Example:
        >>> format = TextVersionFormat(
        ...     url="https://www.congress.gov/118/bills/hr1/BILLS-118hr1ih.pdf",
        ...     type="PDF"
        ... )
    """
    url: str | None = Field(
        default=None,
        description="URL to access this format of the bill text"
    )
    
    type: str | None = Field(
        default=None,
        description="Format type (PDF, XML, HTML, TXT, etc.)"
    )


# TextVersionFormat.model_rebuild()  # Handled by centralized rebuild system


class TextVersionFormats(Model):
    """
    Container for available formats of a bill text version.
    
    Groups all available format options (PDF, XML, HTML, etc.) for a
    specific version of bill text.
    
    Example:
        >>> formats = TextVersionFormats(formats=[
        ...     TextVersionFormat(url="http://example.com/bill.pdf", type="PDF"),
        ...     TextVersionFormat(url="http://example.com/bill.xml", type="XML")
        ... ])
    """
    formats: List[TextVersionFormat] | None = Field(
        default=None,
        description="List of available formats for this text version"
    )


# TextVersionFormats.model_rebuild()  # Handled by centralized rebuild system


class TextVersionItem(Model):
    """
    A specific version of bill text.
    
    Bills go through multiple versions as they progress through Congress
    (Introduced, Engrossed, Enrolled, etc.). Each version represents the
    bill text at a specific stage of the legislative process.
    
    Common Version Types:
        - IH: Introduced in House
        - IS: Introduced in Senate
        - EH: Engrossed in House (passed)
        - ES: Engrossed in Senate (passed)
        - ENR: Enrolled (passed both chambers, sent to President)
    
    Example:
        >>> version = TextVersionItem(
        ...     type="IH",
        ...     date=date(2023, 1, 9),
        ...     formats=[TextVersionFormat(url="...", type="PDF")]
        ... )
    """
    type: str | TextVersionType | None = Field(
        default=None,
        description="Version type code (IH, IS, EH, ES, ENR, etc.)"
    )
    
    date: DateType | str | None = Field(
        default=None,
        description="Date this version was created"
    )
    
    formats: list[TextVersionFormat] | None = Field(
        default=None,
        description="Available formats (PDF, XML, HTML, etc.) for this version"
    )


# TextVersionItem.model_rebuild()  # Handled by centralized rebuild system


class TextVersions(Model):
    """
    Container for all text versions of a bill.
    
    Represents the collection of all text versions for a bill as it
    progresses through the legislative process. Can handle multiple
    API response formats.
    
    API Response Forms:
        1. Reference form: {"count": N, "url": "..."}  
        2. Content form: [{"type": "IH", "date": "...", "formats": [...]}]
        3. Wrapped form: {"textVersions": [...]}
    
    Example:
        >>> versions = TextVersions(textVersions=[
        ...     TextVersionItem(type="IH", date=date(2023, 1, 9)),
        ...     TextVersionItem(type="EH", date=date(2023, 3, 15))
        ... ])
    """
    textVersions: List[TextVersionItem] | None = Field(
        default=None,
        alias="textVersions",
        description="List of text version items for the bill"
    )


# TextVersions.model_rebuild()  # Handled by centralized rebuild system


class Bill(Model):
    """
    Congressional bill model representing proposed legislation.
    
    Bills are the primary legislative vehicles in Congress. They must pass
    both the House and Senate in identical form and be signed by the President
    (or override a presidential veto) to become law.
    
    This model uses reference classes (CommitteeRef, AmendmentRef) to avoid
    circular import dependencies while maintaining full type safety and IDE support.
    
    Related Models:
        - Action: Legislative actions taken on the bill
        - Amendment: Proposed changes to the bill text  
        - Cosponsor: Members who support the bill
        - Subject: Policy areas the bill addresses
        - Summary: CRS summaries of the bill
        - TextVersionItem: Different versions of the bill text
        - Title: Official and popular titles
    
    Example:
        >>> from models.entities.bill import Bill
        >>> bill = Bill(
        ...     congress=118,
        ...     number=1,
        ...     type=LegislationType.HR,
        ...     title="Lower Energy Costs Act"
        ... )
        >>> print(f"{bill.type.value.upper()} {bill.number}")
        HR 1
    """
    
    # === [CORE IDENTIFICATION FIELDS] ===
    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 118 for 118th Congress, 2023-2025)",
        ge=1,
        examples=[118, 117, 116]
    )
    
    number: int | None = Field(
        default=None,
        description="Bill number within the Congress (e.g., 1 for H.R. 1)",
        ge=1,
        examples=[1, 100, 1234]
    )
    
    type: LegislationType | None = Field(
        default=None,
        description="Bill type: hr (House Bill), s (Senate Bill), hjres (House Joint Resolution), "
                    "sjres (Senate Joint Resolution), hconres (House Concurrent Resolution), "
                    "sconres (Senate Concurrent Resolution), hres (House Simple Resolution), "
                    "sres (Senate Simple Resolution)"
    )
    
    # === [METADATA FIELDS] ===
    updateDate: datetime | str | None = Field(
        default=None,
        description="Date and time when the bill data was last updated"
    )
    
    updateDateIncludingText: Any | None = Field(
        default=None,
        description="Date and time when bill data including text versions was last updated"
    )
    
    # === [ORIGIN INFORMATION] ===
    originChamber: Chamber | None = Field(
        default=None,
        description="Chamber where the bill originated (House or Senate)"
    )
    
    originChamberCode: str | None = Field(
        default=None,
        description="Chamber code where bill originated ('H' or 'S')"
    )
    
    introducedDate: datetime | str | None = Field(
        default=None,
        description="Date when the bill was introduced in Congress"
    )
    
    # === [STATUS INFORMATION] ===
    latestAction: LatestAction | None = Field(
        default=None,
        description="Most recent action taken on the bill"
    )
    
    # === [CONSTITUTIONAL AUTHORITY] ===
    constitutionalAuthorityStatementText: str | None = Field(
        default=None,
        description="Statement of constitutional authority for introducing the bill (required for House bills)"
    )
    
    # === [COMMITTEE INFORMATION] ===
    committees: list[CommitteeRef] | CountRef | None = Field(
        default=None,
        description="Committees that have considered or are considering the bill. "
                    "Can be a list of committee references or a count reference with URL."
    )
    
    committeeReports: list[dict] | CountRef | None = Field(
        default=None,
        description="Committee reports issued about the bill. "
                    "Can be a list of report data or a count reference with URL."
    )
    
    # === [RELATED LEGISLATION] ===
    relatedBills: list["Bill"] | CountRef | None = Field(
        default=None,
        alias="bills",
        description="Bills related to this bill (companion bills, identical bills, etc.). "
                    "Can be a list of Bill objects or a count reference with URL."
    )
    
    # === [LEGISLATIVE ACTIONS] ===
    actions: list[Action] | CountRef | None = Field(
        default=None,
        description="All legislative actions taken on the bill. "
                    "Can be a list of Action objects or a count reference with URL."
    )
    
    # === [SPONSORSHIP] ===
    sponsors: list[Sponsor] | CountRef | None = Field(
        default=None,
        description="Primary sponsor(s) of the bill. Typically one sponsor, but can be multiple. "
                    "Can be a list of Sponsor objects or a count reference with URL."
    )
    
    onBehalfOfSponsor: OnBehalfOfSponsor | list[OnBehalfOfSponsor] | None = Field(
        default=None,
        description=(
            "When a measure is introduced on behalf of another member; "
            "API may return one object or a list."
        ),
    )
    
    cosponsors: list[Cosponsor] | CountRef | Cosponsors | None = Field(
        default=None,
        description="Members who have cosponsored the bill. "
                    "Can be a list of Cosponsor objects, a count reference with URL, "
                    "or a fetched Cosponsors wrapper."
    )
    
    # === [COST ESTIMATES] ===
    cboCostEstimates: list[CBOCostEstimate] | CountRef | None = Field(
        default=None,
        description="Congressional Budget Office cost estimates for the bill. "
                    "Can be a list of CBOCostEstimate objects or a count reference with URL."
    )
    
    # === [LAW INFORMATION] ===
    laws: list[Law] | CountRef | None = Field(
        default=None,
        description="Public or private laws if the bill was enacted. "
                    "Can be a list of Law objects or a count reference with URL."
    )
    
    # === [NOTES] ===
    notes: list[Note] | CountRef | None = Field(
        default=None,
        description="Additional notes about the bill. "
                    "Can be a list of Note objects or a count reference with URL."
    )
    
    # === [POLICY INFORMATION] ===
    policyArea: PolicyArea | None = Field(
        default=None,
        description="Primary policy area that the bill addresses (e.g., 'Commerce', 'Health', 'Defense')"
    )
    
    subjects: list[Subject] | CountRef | None = Field(
        default=None,
        description="Legislative subjects and policy areas the bill addresses. "
                    "Can be a list of Subject objects or a count reference with URL."
    )
    
    # === [SUMMARIES] ===
    summaries: list[Summary] | CountRef | None = Field(
        default=None,
        description="Congressional Research Service summaries of the bill. "
                    "Can be a list of Summary objects or a count reference with URL."
    )
    
    # === [TITLES] ===
    title: str | None = Field(
        default=None,
        description="Primary title of the bill (usually the short title or official title)",
        examples=["Lower Energy Costs Act", "Infrastructure Investment and Jobs Act"]
    )
    
    titles: list[Title] | CountRef | None = Field(
        default=None,
        description="All titles associated with the bill (official, short, popular, etc.). "
                    "Can be a list of Title objects or a count reference with URL."
    )
    
    # === [AMENDMENTS] ===
    amendments: list[AmendmentRef] | list[Amendment] | CountRef | None = Field(
        default=None,
        description="Amendments proposed to the bill. "
                    "Can be amendment references, full Amendment objects after expand/fetch, "
                    "or a count reference with URL."
    )
    
    # === [TEXT VERSIONS] ===
    textVersions: list[TextVersionItem] | CountRef | None = Field(
        default=None,
        description="Different versions of the bill text (Introduced, Engrossed, Enrolled, etc.). "
                    "Can be a list of TextVersionItem objects or a count reference with URL."
    )
    
    # === [URL] ===
    url: URL | None = Field(
        default=None,
        description="API URL for accessing this bill's data"
    )
    
    # === [CLIENT] ===
    # NOTE: Client attribute for API operations (not part of API response)
    client: Any | None = Field(
        default=None,
        description="API client instance for making requests (used internally)",
        exclude=True
    )

    @model_validator(mode="after")
    def _link_count_ref_parents(self) -> "Bill":
        from congressgov.services.core.expansion_helpers import attach_count_ref_parents

        attach_count_ref_parents(self)
        return self

    @property
    def bill_number(self) -> int | None:
        return self.number

    @bill_number.setter
    def bill_number(self, value: int | None) -> None:
        self.number = value

    @property
    def bill_type(self) -> LegislationType | None:
        return self.type

    @bill_type.setter
    def bill_type(self, value: LegislationType | None) -> None:
        self.type = value

    @property
    def update_date(self) -> datetime | str | None:
        return self.updateDate

    @update_date.setter
    def update_date(self, value: datetime | str | None) -> None:
        self.updateDate = value

    @property
    def update_date_inc_text(self) -> Any | None:
        return self.updateDateIncludingText

    @update_date_inc_text.setter
    def update_date_inc_text(self, value: Any | None) -> None:
        self.updateDateIncludingText = value

    @property
    def origin_chamber(self) -> Chamber | None:
        return self.originChamber

    @origin_chamber.setter
    def origin_chamber(self, value: Chamber | None) -> None:
        self.originChamber = value

    @property
    def origin_chamber_code(self) -> str | None:
        return self.originChamberCode

    @origin_chamber_code.setter
    def origin_chamber_code(self, value: str | None) -> None:
        self.originChamberCode = value

    @property
    def introduced_date(self) -> datetime | str | None:
        return self.introducedDate

    @introduced_date.setter
    def introduced_date(self, value: datetime | str | None) -> None:
        self.introducedDate = value

    @property
    def latest_action(self) -> "LatestAction | None":
        return self.latestAction

    @latest_action.setter
    def latest_action(self, value: "LatestAction | None") -> None:
        self.latestAction = value

    @property
    def constitutional_authority_statement_text(self) -> str | None:
        return self.constitutionalAuthorityStatementText

    @constitutional_authority_statement_text.setter
    def constitutional_authority_statement_text(self, value: str | None) -> None:
        self.constitutionalAuthorityStatementText = value

    @property
    def committee_reports(self) -> list[dict] | None:
        return self.committeeReports

    @committee_reports.setter
    def committee_reports(self, value: list[dict] | None) -> None:
        self.committeeReports = value

    @property
    def related_bills(self) -> list["Bill"] | None:
        return self.relatedBills

    @related_bills.setter
    def related_bills(self, value: list["Bill"] | None) -> None:
        self.relatedBills = value

    @property
    def on_behalf_of_sponsor(self) -> OnBehalfOfSponsor | list[OnBehalfOfSponsor] | None:
        return self.onBehalfOfSponsor

    @on_behalf_of_sponsor.setter
    def on_behalf_of_sponsor(
        self, value: OnBehalfOfSponsor | list[OnBehalfOfSponsor] | None
    ) -> None:
        self.onBehalfOfSponsor = value

    @property
    def cbo_cost_estimates(self) -> list[CBOCostEstimate] | None:
        return self.cboCostEstimates

    @cbo_cost_estimates.setter
    def cbo_cost_estimates(self, value: list[CBOCostEstimate] | None) -> None:
        self.cboCostEstimates = value

    @property
    def policy_area(self) -> PolicyArea | None:
        return self.policyArea

    @policy_area.setter
    def policy_area(self, value: PolicyArea | None) -> None:
        self.policyArea = value

    @property
    def text_versions(self) -> list[TextVersionItem] | None:
        return self.textVersions

    @text_versions.setter
    def text_versions(self, value: list[TextVersionItem] | None) -> None:
        self.textVersions = value


# Bill.model_rebuild()


class Bills(Model):
    """A container for a list of `Bill` objects, as returned by list/search/related-bill endpoints."""

    bills: List[Bill] | None = Field(
        default=None,
        alias=AliasChoices("bills", "relatedBills", "committee-bills"),
        validation_alias=AliasChoices("bills", "relatedBills", "committee-bills"),
    )

# Add Protocol inheritance for IDE type hinting (only in TYPE_CHECKING)
if TYPE_CHECKING:
    # Create intersection types for IDE awareness without changing runtime behavior
    class Bill(Model, BillProtocol, AsyncBillProtocol):
        """Bill model with sync and async extension method type hints for IDE support."""
        pass
    
    class Bills(Model, BillsProtocol):
        """Bills collection with extension method type hints for IDE support."""
        pass
