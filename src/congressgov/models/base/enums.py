from enum import Enum


class AmendmentType(str, Enum):
    HAMDT = "HAMDT"
    SAMDT = "SAMDT"
    SUAMDT = "SUAMDT"
    
    @classmethod
    def from_api_value(cls, value: str):
        """Convert API abbreviation to enum value"""
        mapping = {
            "HAMDT": cls.HAMDT,
            "SAMDT": cls.SAMDT,
            "SUAMDT": cls.SUAMDT
        }
        return mapping.get(value, value)


_AMENDMENTTYPE_DESCRIPTIONS = {
    AmendmentType.HAMDT: "House Amendment",
    AmendmentType.SAMDT: "Senate Amendment",
    AmendmentType.SUAMDT: "Senate Unprinted Amendment"
}

def _amendmenttype_description(self):
    return _AMENDMENTTYPE_DESCRIPTIONS.get(self, self.value)


AmendmentType.__str__ = _amendmenttype_description
AmendmentType.__repr__ = lambda self: f"<AmendmentType.{self.name}: {_AMENDMENTTYPE_DESCRIPTIONS.get(self, self.value)}>"


class Chamber(str, Enum):
    HOUSE = "House"
    SENATE = "Senate"
    JOINT = "Joint"
    NO_CHAMBER = "NoChamber"
    HOUSE_OF_REPRESENTATIVES = "House of Representatives"
    H = "H"  # Abbreviation for House
    S = "S"  # Abbreviation for Senate
    J = "J"  # Abbreviation for Joint
    N = "N"  # Abbreviation for No Chamber
    HR = "HR"  # Abbreviation for House of Representatives


class LegislationType(str, Enum):
    HR = "HR"
    HRES = "HRES"
    HJRES = "HJRES"
    HCONRES = "HCONRES"
    S = "S"
    SRES = "SRES"
    SJRES = "SJRES"
    SCONRES = "SCONRES"


class SessionType(str, Enum):
    R = "R"
    S = "S"
    REGULAR = "Regular"
    SPECIAL = "Special"


_LegislationType_DESCRIPTIONS = {
    LegislationType.HR: "House Bill",
    LegislationType.HRES: "House Resolution",
    LegislationType.HJRES: "House Joint Resolution",
    LegislationType.HCONRES: "House Concurrent Resolution",
    LegislationType.S: "Senate Bill",
    LegislationType.SRES: "Senate Resolution",
    LegislationType.SJRES: "Senate Joint Resolution",
    LegislationType.SCONRES: "Senate Concurrent Resolution",
}

def _LegislationType_description(self):
    return _LegislationType_DESCRIPTIONS.get(self, self.value)


LegislationType.__str__ = _LegislationType_description
LegislationType.__repr__ = lambda self: f"<LegislationType.{self.name}: {_LegislationType_DESCRIPTIONS.get(self, self.value)}>"


class LawType(str, Enum):
    PUB = "Public"
    PRIV = "Private"


class CommitteeType(str, Enum):
    COMMISSION_OR_CACUS = "Commission or Caucus"
    JOINT = "Joint"
    OTHER = "Other"
    SELECT = "Select"
    SPECIAL = "Special"
    STANDING = "Standing"
    SUBCOMMITTEE = "Subcommittee"
    TASK_FORCE = "Task Force"


class ReportType(str, Enum):
    HRPT = "HRPT"  # House Report code
    SRPT = "SRPT"  # Senate Report code  
    ERPT = "ERPT"  # Executive Report code
    HOUSE_REPORT = "House Report"  # Full name
    SENATE_REPORT = "Senate Report"  # Full name
    EXECUTIVE_REPORT = "Executive Report"  # Full name


class CommunicationCode(str, Enum):
    EC = "Executive Communication"
    PM = "Presidential Message"
    PT = "Petition"
    ML = "Memorial"
    R = "Requirement"


class DocumentTypes(str, Enum):
    ACTIVITY_REPORT = "Activity Report"
    BILLS_AND_RESOLUTIONS = "Bills and Resolutions"
    COMMITTEE_AMENDMENT = "Committee Amendment"
    COMMITTEE_RECORDED_VOTE = "Committee Recorded Vote"
    COMMITTEE_REPORT = "Committee Report"
    COMMITTEE_RULES = "Committee Rules"
    CONFERENCE_REPORT = "Conference Report"
    FLOOR_AMENDMENT = "Floor Amendment"
    GENERIC_DOCUMENT = "Generic Document"
    HEARING_COVER_PAGE = "Hearing: Cover Page"
    HEARING_MEMBER_ROSTER = "Hearing: Member Roster"
    HEARING_QUESTIONS_FOR_THE_RECORD = "Hearing: Questions for the Record"
    HEARING_TABLE_OF_CONTENTS = "Hearing: Table of Contents"
    HEARING_TRANSCRIPT = "Hearing: Transcript"
    HEARING_WITNESS_LIST = "Hearing: Witness List"
    HOUSE_OR_SENATE_AMENDMENT = "House or Senate Amendment"
    MEMBER_STATEMENTS = "Member Statements"
    SUPPORT_DOCUMENT = "Support Document"


class WitnessDocumentTypes(str, Enum):
    WITNESS_BIOGRAPHY = "Witness Biography"
    WITNESS_SUPPORTING_DOCUMENT = "Witness Supporting Document"
    WITNESS_STATEMENT = "Witness Statement"
    WITNESS_TRUTH_IN_TESTIMONY = "Witness Truth in Testimony"


class MeetingStatus(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELED = "Canceled"
    POSTPONED = "Postponed"
    RESCHEDULED = "Rescheduled"


class MeetingType(str, Enum):
    MEETING = "Meeting"
    HEARING = "Hearing"
    MARKUP = "Markup"


class TextVersionType(str, Enum):
    INTRODUCED = "As Introduced"
    REPORTED = "Reported"
    ENGROSSED = "Engrossed"
    ENROLLED = "Enrolled"
    PUBLIC_PRINT = "Public Print"
    PUBLIC_LAW = "Public Law"
    CONFERENCE = "Conference"
    # Additional types that the API actually returns
    ENROLLED_BILL = "Enrolled Bill"
    PLACED_ON_CALENDAR_SENATE = "Placed on Calendar Senate"
    RETURNED_TO_HOUSE_BY_UNANIMOUS_CONSENT = "Returned to the House by Unanimous Consent"
    ENGROSSED_IN_HOUSE = "Engrossed in House"
    REPORTED_IN_HOUSE = "Reported in House"
    INTRODUCED_IN_HOUSE = "Introduced in House"


class TextFormatType(str, Enum):
    """
    Enum for text format types returned by the API.
    These are different from TextVersionType - they represent the format of the text file.
    """
    FORMATTED_TEXT = "Formatted Text"
    PDF = "PDF"
    FORMATTED_XML = "Formatted XML"
    XML = "XML"
    HTML = "HTML"
    TEXT = "Text"


class ActionType(str, Enum):
    COMMITTEE = "Committee"
    CALENDARS = "Calendars"
    FLOOR = "Floor"
    BECAME_LAW = "BecameLaw"
    INTRO_REFERRAL = "IntroReferral"
    PRESIDENT = "President"
    RESOLVING_DIFFERENCES = "ResolvingDifferences"
    DISCHARGE = "Discharge"
    NOT_USED = "NotUsed"
    VETO = "Veto"


class ActionCode(str, Enum):
    INTRODUCED_IN_HOUSE = "1000"  # Introduced in House
    REPORTED_ORIGINAL_MEASURE = "1010"  # Reported Original Measure
    SUBMITTED_IN_HOUSE = "1025"  # Submitted in House
    REFERRED_TO_HOUSE_COMMITTEE = "2000"  # Referred to House committee
    REFERRED_TO_HOUSE_SUBCOMMITTEE = "3000"  # Referred to House subcommittee
    HOUSE_COMMITTEE_SUBCOMMITTEE_ACTIONS = "4000"  # House committee/subcommittee actions
    HOUSE_COMMITTEE_SUBCOMMITTEE_HEARINGS = "4100"  # House committee/subcommittee hearings
    HOUSE_COMMITTEE_SUBCOMMITTEE_MARKUPS = "4200"  # House committee/subcommittee markups
    HOUSE_COMMITTEE_TIME_EXTENSION = "4900"  # House committee time extension
    HOUSE_DISCHARGE_PETITION_FILED = "4950"  # House discharge petition filed
    REPORTED_TO_HOUSE = "5000"  # Reported to House
    HOUSE_COMMITTEE_DISCHARGED = "5500"  # House committee discharged
    HOUSE_FLOOR_ACTIONS = "7000"  # House floor actions
    PASSED_AGREED_TO_IN_HOUSE = "8000"  # Passed/agreed to in House
    FAILED_OF_PASSAGE_NOT_AGREED_TO_IN_HOUSE = "9000"  # Failed of passage/not agreed to in House
    INTRODUCED_IN_SENATE = "10000"  # Introduced in Senate
    REFERRED_TO_SENATE_COMMITTEE = "11000"  # Referred to Senate committee
    REFERRED_TO_SENATE_SUBCOMMITTEE = "12000"  # Referred to Senate subcommittee
    SENATE_COMMITTEE_SUBCOMMITTEE_ACTIONS = "13000"  # Senate committee/subcommittee actions
    SENATE_COMMITTEE_SUBCOMMITTEE_HEARINGS = "13100"  # Senate committee/subcommittee hearings
    SENATE_COMMITTEE_SUBCOMMITTEE_MARKUPS = "13200"  # Senate committee/subcommittee markups
    SENATE_COMMITTEE_TIME_EXTENSION = "13900"  # Senate committee time extension
    REPORTED_TO_SENATE = "14000"  # Reported to Senate
    SENATE_COMMITTEE_DISCHARGED = "14500"  # Senate committee discharged
    SENATE_COMMITTEE_REPORT_FILED_AFTER_REPORTING = "14900"  # Senate committee report filed after reporting
    SENATE_FLOOR_ACTIONS = "16000"  # Senate floor actions
    PASSED_AGREED_TO_IN_SENATE = "17000"  # Passed/agreed to in Senate
    FAILED_OF_PASSAGE_NOT_AGREED_TO_IN_SENATE = "18000"  # Failed of passage/not agreed to in Senate
    RESOLVING_DIFFERENCES_HOUSE_ACTIONS = "19000"  # Resolving differences -- House actions
    RESOLVING_DIFFERENCES_SENATE_ACTIONS = "20000"  # Resolving differences -- Senate actions
    CONFERENCE_COMMITTEE_ACTIONS = "20800"  # Conference committee actions
    CONFERENCE_REPORT_FILED = "20900"  # Conference report filed
    CONFERENCE_REPORT_AGREED_TO_IN_HOUSE = "21000"  # Conference report agreed to in House
    CONFERENCE_REPORT_DISAGREED_TO_IN_HOUSE = "22000"  # Conference report disagreed to in House
    CONFERENCE_REPORT_AGREED_TO_IN_SENATE = "23000"  # Conference report agreed to in Senate
    CONFERENCE_REPORT_DISAGREED_TO_IN_SENATE = "24000"  # Conference report disagreed to in Senate
    ROLL_CALL_VOTES_ON_MEASURES_IN_HOUSE = "25000"  # Roll call votes on measures in House
    ROLL_CALL_VOTES_ON_MEASURES_IN_SENATE = "26000"  # Roll call votes on measures in Senate
    PRESENTED_TO_PRESIDENT = "28000"  # Presented to President
    SIGNED_BY_PRESIDENT = "29000"  # Signed by President
    SENT_TO_ARCHIVIST_UNSIGNED_BY_PRESIDENT = "29100"  # Sent to Archivist unsigned by President
    POCKET_VETOED_BY_PRESIDENT = "30000"  # Pocket vetoed by President
    VETOED_BY_PRESIDENT = "31000"  # Vetoed by President
    PASSED_HOUSE_OVER_VETO = "32000"  # Passed House over veto
    FAILED_OF_PASSAGE_IN_HOUSE_OVER_VETO = "33000"  # Failed of passage in House over veto
    PASSED_SENATE_OVER_VETO = "34000"  # Passed Senate over veto
    FAILED_OF_PASSAGE_IN_SENATE_OVER_VETO = "35000"  # Failed of passage in Senate over veto
    BECAME_PUBLIC_LAW = "36000"  # Became Public Law
    PUBLIC_LAW_SIGNED_BY_PRESIDENT = "37000"  # Public Law signed by President
    PUBLIC_LAW_UNSIGNED_BY_PRESIDENT = "38000"  # Public Law unsigned by President
    PUBLIC_LAW_ENACTED_OVER_VETO = "39000"  # Public Law enacted over veto
    PUBLIC_LAW_BY_OTHER_MEANS = "40000"  # Public Law by other means
    BECAME_PRIVATE_LAW = "41000"  # Became Private Law
    PRIVATE_LAW_SIGNED_BY_PRESIDENT = "42000"  # Private Law signed by President
    PRIVATE_LAW_UNSIGNED_BY_PRESIDENT = "43000"  # Private Law unsigned by President
    PRIVATE_LAW_ENACTED_OVER_VETO = "44000"  # Private Law enacted over veto
    PRIVATE_LAW_BY_OTHER_MEANS = "45000"  # Private Law by other means
    LINE_ITEM_VETO_BY_PRESIDENT = "46000"  # Line item veto by President
    DISAPPROVAL_BILL_IN_HOUSE = "47000"  # Disapproval bill in House
    DISAPPROVAL_BILL_IN_SENATE = "48000"  # Disapproval bill in Senate
    HOUSE_AMENDMENT_OFFERED = "71000"  # House amendment offered
    HOUSE_AMENDMENT_AGREED_TO = "72000"  # House amendment agreed to
    HOUSE_AMENDMENT_CONSIDERED_AS_ADOPTED = "72500"  # House amendment considered as adopted
    HOUSE_AMENDMENT_NOT_AGREED_TO = "73000"  # House amendment not agreed to
    OTHER_HOUSE_AMENDMENT_ACTIONS = "74000"  # Other House amendment actions
    ROLL_CALL_VOTES_ON_AMENDMENTS_IN_HOUSE = "75000"  # Roll call votes on amendments in House
    SENATE_AMENDMENT_SUBMITTED = "91000"  # Senate amendment submitted
    SENATE_AMENDMENT_REFERRED_TO_COMMITTEE = "92000"  # Senate amendment referred to committee
    SENATE_AMENDMENT_PROPOSED_ON_THE_FLOOR = "93000"  # Senate amendment proposed (on the floor)
    SENATE_AMENDMENT_AGREED_TO = "94000"  # Senate amendment agreed to
    SENATE_AMENDMENT_NOT_AGREED_TO = "95000"  # Senate amendment not agreed to
    OTHER_SENATE_AMENDMENT_ACTIONS = "96000"  # Other Senate amendment actions
    ROLL_CALL_VOTES_ON_AMENDMENTS_IN_SENATE = "97000"  # Roll call votes on amendments in Senate

    @property
    def description(self) -> str:
        return self.name.replace("_", " ").title()


class VersionCode(str, Enum):
    pass    # TODO: Need to implement this (https://github.com/LibraryOfCongress/api.congress.gov/blob/main/Documentation/BillEndpoint.md#summaries-level)


class TitleTypeCode(str, Enum):
    OFFICIAL_TITLE_AS_INTRODUCED = "6"
    OFFICIAL_TITLES_AS_AMENDED_BY_HOUSE = "7"
    OFFICIAL_TITLES_AS_AMENDED_BY_SENATE = "8"
    OFFICIAL_TITLE_AS_AGREED_TO_BY_HOUSE_AND_SENATE = "9"
    SHORT_TITLES_AS_INTRODUCED = "14"
    SHORT_TITLES_AS_PASSED_HOUSE = "17"
    SHORT_TITLES_AS_PASSED_SENATE = "18"
    SHORT_TITLES_AS_ENACTED = "19"
    SHORT_TITLES_AS_INTRODUCED_FOR_PORTIONS = "22"
    SHORT_TITLES_AS_REPORTED_TO_HOUSE_FOR_PORTIONS = "23"
    SHORT_TITLES_AS_REPORTED_TO_SENATE_FOR_PORTIONS = "24"
    SHORT_TITLES_AS_PASSED_HOUSE_FOR_PORTIONS = "25"
    SHORT_TITLES_AS_PASSED_SENATE_FOR_PORTIONS = "26"
    SHORT_TITLES_AS_ENACTED_FOR_PORTIONS = "27"
    POPULAR_TITLE = "30"
    DISPLAY_TITLE = "45"
    SHORT_TITLES_AS_INTRODUCED_ALT = "101"
    SHORT_TITLES_AS_REPORTED_TO_HOUSE = "102"
    SHORT_TITLES_AS_REPORTED_TO_SENATE = "103"
    SHORT_TITLES_AS_PASSED_HOUSE_ALT = "104"
    SHORT_TITLES_AS_PASSED_SENATE_ALT = "105"
    SHORT_TITLES_AS_INTRODUCED_FOR_PORTIONS_ALT = "106"
    SHORT_TITLES_AS_REPORTED_TO_HOUSE_FOR_PORTIONS_ALT = "107"
    SHORT_TITLES_AS_REPORTED_TO_SENATE_FOR_PORTIONS_ALT = "108"
    SHORT_TITLES_AS_PASSED_HOUSE_FOR_PORTIONS_ALT = "109"
    SHORT_TITLES_AS_PASSED_SENATE_FOR_PORTIONS_ALT = "110"
    SHORT_TITLES_FROM_ENR_BILL_TEXT = "147"
    SHORT_TITLES_FROM_ENGROSSED_AMENDMENT_SENATE = "250"
    SHORT_TITLES_FROM_ENGROSSED_AMENDMENT_HOUSE_FOR_PORTIONS = "253"
    SHORT_TITLES_FROM_ENGROSSED_AMENDMENT_SENATE_FOR_PORTIONS = "254"

    DESCRIPTIONS = {
        "6": "Official Title as Introduced",
        "7": "Official Titles as Amended by House",
        "8": "Official Titles as Amended by Senate",
        "9": "Official Title as Agreed to by House and Senate",
        "14": "Short Titles as Introduced",
        "17": "Short Titles as Passed House",
        "18": "Short Titles as Passed Senate",
        "19": "Short Titles as Enacted",
        "22": "Short Titles as Introduced for portions of this bill",
        "23": "Short Titles as Reported to House for portions of this bill",
        "24": "Short Titles as Reported to Senate for portions of this bill",
        "25": "Short Titles as Passed House for portions of this bill",
        "26": "Short Titles as Passed Senate for portions of this bill",
        "27": "Short Titles as Enacted for portions of this bill",
        "30": "Popular Title",
        "45": "Display Title",
        "101": "Short Title(s) as Introduced",
        "102": "Short Title(s) as Reported to House",
        "103": "Short Title(s) as Reported to Senate",
        "104": "Short Title(s) as Passed House",
        "105": "Short Title(s) as Passed Senate",
        "106": "Short Title(s) as Introduced for portions of this bill",
        "107": "Short Title(s) as Reported to House for portions of this bill",
        "108": "Short Title(s) as Reported to Senate for portions of this bill",
        "109": "Short Title(s) as Passed House for portions of this bill",
        "110": "Short Title(s) as Passed Senate for portions of this bill",
        "147": "Short Title(s) from ENR (Enrolled) bill text",
        "250": "Short Title(s) from Engrossed Amendment Senate",
        "253": "Short Title(s) from Engrossed Amendment House for portions of this bill",
        "254": "Short Title(s) from Engrossed Amendment Senate for portions of this bill",
    }

    @property
    def description(self) -> str:
        """
        Returns a human-readable description for the title type code.
        Uses a class-level mapping for efficiency and clarity.
        """
        # Use self.value (the enum value, e.g., "6", "7", etc.) as the key
        return self.DESCRIPTIONS.get(self.value, "Unknown Title Type Code")


class StateCode(str, Enum):
    AL = "Alabama"
    AK = "Alaska"
    AZ = "Arizona"
    AR = "Arkansas"
    CA = "California"
    CO = "Colorado"
    CT = "Connecticut"
    DE = "Delaware"
    FL = "Florida"
    GA = "Georgia"
    HI = "Hawaii"
    ID = "Idaho"
    IL = "Illinois"
    IN = "Indiana"
    IA = "Iowa"
    KS = "Kansas"
    KY = "Kentucky"
    LA = "Louisiana"
    ME = "Maine"
    MD = "Maryland"
    MA = "Massachusetts"
    MI = "Michigan"
    MN = "Minnesota"
    MS = "Mississippi"
    MO = "Missouri"
    MT = "Montana"
    NE = "Nebraska"
    NV = "Nevada"
    NH = "New Hampshire"
    NJ = "New Jersey"
    NM = "New Mexico"
    NY = "New York"
    NC = "North Carolina"
    ND = "North Dakota"
    OH = "Ohio"
    OK = "Oklahoma"
    OR = "Oregon"
    PA = "Pennsylvania"
    RI = "Rhode Island"
    SC = "South Carolina"
    SD = "South Dakota"
    TN = "Tennessee"
    TX = "Texas"
    UT = "Utah"
    VT = "Vermont"
    VA = "Virginia"
    WA = "Washington"
    WV = "West Virginia"
    WI = "Wisconsin"
    WY = "Wyoming"
    DC = "District of Columbia"
    AS = "American Samoa"
    GU = "Guam"
    MP = "Northern Mariana Islands"
    PR = "Puerto Rico"
    VI = "U.S. Virgin Islands"


class VoteType(str, Enum):
    TWO_THIRDS_RECORDED_VOTE = "2/3 Recorded Vote"
    TWO_THIRDS_YEA_AND_NAY = "2/3 Yea-And-Nay"
    THREE_FIFTHS_RECORDED_VOTE = "3/5 Recorded Vote"
    THREE_FIFTHS_YEA_AND_NAY = "3/5 Yea-And-Nay"
    QUORUM = "Quorum"
    RECORDED_VOTE = "Recorded Vote"
    YEA_AND_NAY = "Yea-and-Nay"


class VoteResult(str, Enum):
    PASSED = "Passed"
    FAILED = "Failed"
    AGREED_TO = "Agreed to"


class VoteQuestion(str, Enum):
    ON_AGREEING_TO_THE_AMENDMENT = "On Agreeing to the Amendment"
    ON_AGREEING_TO_THE_RESOLUTION = "On Agreeing to the Resolution"
    ON_AGREEING_TO_THE_RESOLUTION_AS_AMENDED = "On Agreeing to the Resolution, as Amended"
    ON_MOTION_TO_RECOMMIT = "On Motion to Recommit"
    ON_MOTION_TO_RECONSIDER = "On Motion to Reconsider"
    ON_MOTION_TO_SUSPEND_THE_RULES_AND_AGREE = "On Motion to Suspend the Rules and Agree"
    ON_MOTION_TO_SUSPEND_THE_RULES_AND_AGREE_AS_AMENDED = "On Motion to Suspend the Rules and Agree, as Amended"
    ON_MOTION_TO_SUSPEND_THE_RULES_AND_CONCUR_IN_THE_SENATE_AMENDMENT = "On Motion to Suspend the Rules and Concur in the Senate Amendment"
    ON_MOTION_TO_SUSPEND_THE_RULES_AND_PASS = "On Motion to Suspend the Rules and Pass"
    ON_MOTION_TO_SUSPEND_THE_RULES_AND_PASS_AS_AMENDED = "On Motion to Suspend the Rules and Pass, as Amended"
    ON_MOTION_TO_TABLE = "On Motion to Table"
    ON_ORDERING_THE_PREVIOUS_QUESTION = "On Ordering the Previous Question"
    ON_PASSAGE = "On Passage"

class SourceSystemCode(int, Enum):
    SENATE = 0
    HOUSE_1 = 1
    HOUSE_2 = 2
    LIBRARY_OF_CONGRESS = 9

class TextFormats(str, Enum):
    FORMATTED_TEXT = "Formatted Text"
    PDF = "PDF"
    FORMATTED_XML = "Formatted XML"


# Note: This file contains enums, not Pydantic models, so no model_rebuild() calls are needed
