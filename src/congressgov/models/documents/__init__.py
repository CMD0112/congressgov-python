"""
Document-related classes for congressgov models

This module contains classes for legislative documents like reports, hearings, etc.
"""

from .reports import CommitteeReport, CommitteeReports, Report, Reports
from .crs_reports import CRSReport, CRSReports, CRSReportRef, CRSFormats, CRSRelatedMaterial, CRSRelatedMaterials, CRSTopic, CRSTopics, CRSAuthor, CRSAuthors
from .congressional_record import DailyCongressionalRecord, Issue, Section
from .bound_congressional_record import BoundCongressionalRecord, BoundCongressionalRecords, DailyDigest, DailyDigestText, Section as BoundSection, Sections
from .hearing import Hearing, Hearings
from .prints import CommitteePrint, CommitteePrints
from .committee_print import CommitteePrint as CommitteePrintDoc, CommitteePrints as CommitteePrintsDoc, CommitteePrintRef, CommitteePrintText, CommitteePrintTexts
from .committee_report import CommitteeReport as CommitteeReportDoc, CommitteeReports as CommitteeReportsDoc, CommitteeReportRef, CommitteeReportText, CommitteeReportTexts

__all__ = [
    # Reports
    "CommitteeReport",
    "CommitteeReports",
    "Report",
    "Reports",
    
    # CRS Reports
    "CRSReport", 
    "CRSReports",
    "CRSReportRef",
    "CRSFormats",
    "CRSRelatedMaterial",
    "CRSRelatedMaterials",
    "CRSTopic",
    "CRSTopics",
    "CRSAuthor",
    "CRSAuthors",
    
    # Congressional Record
    "DailyCongressionalRecord",
    "Issue",
    "Section",
    
    # Bound Congressional Record
    "BoundCongressionalRecord",
    "BoundCongressionalRecords",
    "DailyDigest",
    "DailyDigestText",
    "BoundSection",
    "Sections",
    
    # Hearings
    "Hearing",
    "Hearings",
    
    # Prints
    "CommitteePrint",
    "CommitteePrints",
    
    # Committee Documents
    "CommitteePrintDoc",
    "CommitteePrintsDoc", 
    "CommitteePrintRef",
    "CommitteePrintText",
    "CommitteePrintTexts",
    "CommitteeReportDoc",
    "CommitteeReportsDoc",
    "CommitteeReportRef",
    "CommitteeReportText",
    "CommitteeReportTexts",
]
