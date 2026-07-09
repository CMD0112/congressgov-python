# classes/base/rebuild.py
"""
Centralized model rebuild system to handle circular imports properly.
This ensures all forward references are resolved in the correct order.
"""

import logging

logger = logging.getLogger(__name__)


def rebuild_all_models():
    """
    Rebuild all models in the correct dependency order.
    This must be called after all modules are imported.
    """
    # Import all modules first to ensure they're loaded
    # from ..summaries import summary  # Summaries are imported from entities.bill
    
    # Rebuild in dependency order (most dependent last)
    
    # Level 1: Base classes with no dependencies
    # Import specific enums instead of using *
    
    # Level 2: Simple entity classes
    
    # Level 3: Complex entity classes that depend on Level 2
    
    # Level 4: Document classes
    
    # Level 5: Communication classes
    
    # Level 6: Meeting and nomination classes
    
    # Now rebuild all models with proper namespace
    rebuild_models_with_namespace()

def rebuild_models_with_namespace():
    """Rebuild models with all classes available in namespace"""
    import sys
    
    # Get the current module's namespace
    current_module = sys.modules[__name__]
    namespace = current_module.__dict__.copy()
    
    # Add all imported classes to namespace
    from ..entities.bill import Bill, Bills, Summary, Summaries, ConstitutionalAuthorityStatement, TextVersionItem, TextVersions
    from ..entities.member import Member, Members, Term, Depiction
    from ..entities.sponsor import Sponsor, Sponsors, Cosponsor, Cosponsors, OnBehalfOfSponsor, OnBehalfOfSponsors
    from ..entities.amendment import Amendment, Amendments
    from ..base.references import AmendmentRef
    from ..entities.treaty import Treaty, Treaties, TreatyCommittee, TreatyCommittees
    from ..entities.congress import Congress, Congresses, CongressSession, CongressSessions
    from ..committees.committee import Committee, Committees, CommitteeRef, CommitteeShortRef, CommitteeBills
    from ..actions.action import Action, Actions, ActionsRef, LatestAction
    from ..actions.vote import RecordedVote, RecordedVotes
    from ..actions.calendar import CalendarNumber
    from ..core.core import Title, Titles, Law, Laws, Subject, Subjects, CBOCostEstimate, CBOCostEstimates, Note, Notes
    from ..documents.reports import CommitteeReport, CommitteeReports, CRSReport, CRSReports, Report, Reports, CommitteeReportRef, CommitteeReportText, CommitteeReportTexts, CRSReportRef, CRSFormats, CRSRelatedMaterial, CRSRelatedMaterials, CRSTopic, CRSTopics, CRSAuthor, CRSAuthors
    from ..documents.hearing import Hearing, Hearings
    from ..documents.bound_congressional_record import BoundCongressionalRecord, BoundCongressionalRecords
    from ..documents.prints import CommitteePrint, CommitteePrints, CommitteePrintRef, CommitteePrintText, CommitteePrintTexts
    from ..communications.house_communication import HouseCommunication, HouseCommunications
    from ..communications.senate_communication import SenateCommunication, SenateCommunications
    from ..communications.house_requirement import HouseRequirement, HouseRequirements
    from ..communications.house_vote import HouseVote, HouseVotes, MemberVotes
    from ..meetings.meeting import CommitteeMeeting, CommitteeMeetings, CommitteeMeetingRef, CommitteeLocation, CommitteeLocations, CommitteeVideo, CommitteeVideos, CommitteeWitness, CommitteeWitnesses, CommitteeWitnessDocument, CommitteeWitnessDocuments, CommitteeMeetingDocument, CommitteeHearingTranscript, RelatedItems
    from ..nominations.nomination import Nomination, Nominations, Nominee, Nominees
    
    # Add to namespace
    namespace.update({
        'Bill': Bill, 'Bills': Bills, 'Summary': Summary, 'Summaries': Summaries,
        'ConstitutionalAuthorityStatement': ConstitutionalAuthorityStatement,
        'TextVersionItem': TextVersionItem, 'TextVersions': TextVersions,
        'Member': Member, 'Members': Members, 'Term': Term, 'Depiction': Depiction,
        'Sponsor': Sponsor, 'Sponsors': Sponsors, 'Cosponsor': Cosponsor, 'Cosponsors': Cosponsors,
        'OnBehalfOfSponsor': OnBehalfOfSponsor, 'OnBehalfOfSponsors': OnBehalfOfSponsors,
        'Amendment': Amendment, 'Amendments': Amendments, 'AmendmentRef': AmendmentRef,
        'Treaty': Treaty, 'Treaties': Treaties, 'TreatyCommittee': TreatyCommittee, 'TreatyCommittees': TreatyCommittees,
        'Congress': Congress, 'Congresses': Congresses, 'CongressSession': CongressSession, 'CongressSessions': CongressSessions,
        'Committee': Committee, 'Committees': Committees, 'CommitteeRef': CommitteeRef, 'CommitteeShortRef': CommitteeShortRef,
        'CommitteeBills': CommitteeBills,
        'Action': Action, 'Actions': Actions, 'ActionsRef': ActionsRef, 'LatestAction': LatestAction,
        'RecordedVote': RecordedVote, 'RecordedVotes': RecordedVotes, 'CalendarNumber': CalendarNumber,
        'Title': Title, 'Titles': Titles, 'Law': Law, 'Laws': Laws, 'Subject': Subject, 'Subjects': Subjects,
        'CBOCostEstimate': CBOCostEstimate, 'CBOCostEstimates': CBOCostEstimates, 'Note': Note, 'Notes': Notes,
        'CommitteeReport': CommitteeReport, 'CommitteeReports': CommitteeReports, 'CRSReport': CRSReport, 'CRSReports': CRSReports,
        'Report': Report, 'Reports': Reports, 'CommitteeReportRef': CommitteeReportRef,
        'CommitteeReportText': CommitteeReportText, 'CommitteeReportTexts': CommitteeReportTexts,
        'CRSReportRef': CRSReportRef, 'CRSFormats': CRSFormats, 'CRSRelatedMaterial': CRSRelatedMaterial,
        'CRSRelatedMaterials': CRSRelatedMaterials, 'CRSTopic': CRSTopic, 'CRSTopics': CRSTopics,
        'CRSAuthor': CRSAuthor, 'CRSAuthors': CRSAuthors,
        'Hearing': Hearing, 'Hearings': Hearings, 'BoundCongressionalRecord': BoundCongressionalRecord, 'BoundCongressionalRecords': BoundCongressionalRecords,
        'CommitteePrint': CommitteePrint, 'CommitteePrints': CommitteePrints, 'CommitteePrintRef': CommitteePrintRef,
        'CommitteePrintText': CommitteePrintText, 'CommitteePrintTexts': CommitteePrintTexts,
        'HouseCommunication': HouseCommunication, 'HouseCommunications': HouseCommunications,
        'SenateCommunication': SenateCommunication, 'SenateCommunications': SenateCommunications,
        'HouseRequirement': HouseRequirement, 'HouseRequirements': HouseRequirements,
        'HouseVote': HouseVote, 'HouseVotes': HouseVotes, 'MemberVotes': MemberVotes,
        'CommitteeMeeting': CommitteeMeeting, 'CommitteeMeetings': CommitteeMeetings, 'CommitteeMeetingRef': CommitteeMeetingRef,
        'CommitteeLocation': CommitteeLocation, 'CommitteeLocations': CommitteeLocations,
        'CommitteeVideo': CommitteeVideo, 'CommitteeVideos': CommitteeVideos,
        'CommitteeWitness': CommitteeWitness, 'CommitteeWitnesses': CommitteeWitnesses,
        'CommitteeWitnessDocument': CommitteeWitnessDocument, 'CommitteeWitnessDocuments': CommitteeWitnessDocuments,
        'CommitteeMeetingDocument': CommitteeMeetingDocument, 'CommitteeHearingTranscript': CommitteeHearingTranscript,
        'RelatedItems': RelatedItems,
        'Nomination': Nomination, 'Nominations': Nominations, 'Nominee': Nominee, 'Nominees': Nominees
    })
    
    # Now rebuild all models with the complete namespace
    try:
        # Core entities
        Bill.model_rebuild(_types_namespace=namespace)
        Bills.model_rebuild(_types_namespace=namespace)
        Summary.model_rebuild(_types_namespace=namespace)
        Summaries.model_rebuild(_types_namespace=namespace)
        ConstitutionalAuthorityStatement.model_rebuild(_types_namespace=namespace)
        TextVersionItem.model_rebuild(_types_namespace=namespace)
        TextVersions.model_rebuild(_types_namespace=namespace)
        
        # Member and sponsor classes
        Member.model_rebuild(_types_namespace=namespace)
        Members.model_rebuild(_types_namespace=namespace)
        Term.model_rebuild(_types_namespace=namespace)
        Depiction.model_rebuild(_types_namespace=namespace)
        Sponsor.model_rebuild(_types_namespace=namespace)
        Sponsors.model_rebuild(_types_namespace=namespace)
        Cosponsor.model_rebuild(_types_namespace=namespace)
        Cosponsors.model_rebuild(_types_namespace=namespace)
        OnBehalfOfSponsor.model_rebuild(_types_namespace=namespace)
        OnBehalfOfSponsors.model_rebuild(_types_namespace=namespace)
        
        # Amendment classes
        Amendment.model_rebuild(_types_namespace=namespace)
        Amendments.model_rebuild(_types_namespace=namespace)
        AmendmentRef.model_rebuild(_types_namespace=namespace)
        
        # Treaty classes
        Treaty.model_rebuild(_types_namespace=namespace)
        Treaties.model_rebuild(_types_namespace=namespace)
        TreatyCommittee.model_rebuild(_types_namespace=namespace)
        TreatyCommittees.model_rebuild(_types_namespace=namespace)
        
        # Congress classes
        Congress.model_rebuild(_types_namespace=namespace)
        Congresses.model_rebuild(_types_namespace=namespace)
        CongressSession.model_rebuild(_types_namespace=namespace)
        CongressSessions.model_rebuild(_types_namespace=namespace)
        
        # Committee classes
        Committee.model_rebuild(_types_namespace=namespace)
        Committees.model_rebuild(_types_namespace=namespace)
        CommitteeRef.model_rebuild(_types_namespace=namespace)
        CommitteeShortRef.model_rebuild(_types_namespace=namespace)
        CommitteeBills.model_rebuild(_types_namespace=namespace)
        
        # Action classes
        Action.model_rebuild(_types_namespace=namespace)
        Actions.model_rebuild(_types_namespace=namespace)
        ActionsRef.model_rebuild(_types_namespace=namespace)
        LatestAction.model_rebuild(_types_namespace=namespace)
        RecordedVote.model_rebuild(_types_namespace=namespace)
        RecordedVotes.model_rebuild(_types_namespace=namespace)
        CalendarNumber.model_rebuild(_types_namespace=namespace)
        
        # Core classes
        Title.model_rebuild(_types_namespace=namespace)
        Titles.model_rebuild(_types_namespace=namespace)
        Law.model_rebuild(_types_namespace=namespace)
        Laws.model_rebuild(_types_namespace=namespace)
        Subject.model_rebuild(_types_namespace=namespace)
        Subjects.model_rebuild(_types_namespace=namespace)
        CBOCostEstimate.model_rebuild(_types_namespace=namespace)
        CBOCostEstimates.model_rebuild(_types_namespace=namespace)
        Note.model_rebuild(_types_namespace=namespace)
        Notes.model_rebuild(_types_namespace=namespace)
        
        # Document classes
        CommitteeReport.model_rebuild(_types_namespace=namespace)
        CommitteeReports.model_rebuild(_types_namespace=namespace)
        CRSReport.model_rebuild(_types_namespace=namespace)
        CRSReports.model_rebuild(_types_namespace=namespace)
        Report.model_rebuild(_types_namespace=namespace)
        Reports.model_rebuild(_types_namespace=namespace)
        CommitteeReportRef.model_rebuild(_types_namespace=namespace)
        CommitteeReportText.model_rebuild(_types_namespace=namespace)
        CommitteeReportTexts.model_rebuild(_types_namespace=namespace)
        CRSReportRef.model_rebuild(_types_namespace=namespace)
        CRSFormats.model_rebuild(_types_namespace=namespace)
        CRSRelatedMaterial.model_rebuild(_types_namespace=namespace)
        CRSRelatedMaterials.model_rebuild(_types_namespace=namespace)
        CRSTopic.model_rebuild(_types_namespace=namespace)
        CRSTopics.model_rebuild(_types_namespace=namespace)
        CRSAuthor.model_rebuild(_types_namespace=namespace)
        CRSAuthors.model_rebuild(_types_namespace=namespace)
        
        # Hearing classes
        Hearing.model_rebuild(_types_namespace=namespace)
        Hearings.model_rebuild(_types_namespace=namespace)
        
        # Congressional record classes
        BoundCongressionalRecord.model_rebuild(_types_namespace=namespace)
        BoundCongressionalRecords.model_rebuild(_types_namespace=namespace)
        
        # Print classes
        CommitteePrint.model_rebuild(_types_namespace=namespace)
        CommitteePrints.model_rebuild(_types_namespace=namespace)
        CommitteePrintRef.model_rebuild(_types_namespace=namespace)
        CommitteePrintText.model_rebuild(_types_namespace=namespace)
        CommitteePrintTexts.model_rebuild(_types_namespace=namespace)
        
        # Communication classes
        HouseCommunication.model_rebuild(_types_namespace=namespace)
        HouseCommunications.model_rebuild(_types_namespace=namespace)
        SenateCommunication.model_rebuild(_types_namespace=namespace)
        SenateCommunications.model_rebuild(_types_namespace=namespace)
        HouseRequirement.model_rebuild(_types_namespace=namespace)
        HouseRequirements.model_rebuild(_types_namespace=namespace)
        HouseVote.model_rebuild(_types_namespace=namespace)
        HouseVotes.model_rebuild(_types_namespace=namespace)
        MemberVotes.model_rebuild(_types_namespace=namespace)
        
        # Meeting classes
        CommitteeMeeting.model_rebuild(_types_namespace=namespace)
        CommitteeMeetings.model_rebuild(_types_namespace=namespace)
        CommitteeMeetingRef.model_rebuild(_types_namespace=namespace)
        CommitteeLocation.model_rebuild(_types_namespace=namespace)
        CommitteeLocations.model_rebuild(_types_namespace=namespace)
        CommitteeVideo.model_rebuild(_types_namespace=namespace)
        CommitteeVideos.model_rebuild(_types_namespace=namespace)
        CommitteeWitness.model_rebuild(_types_namespace=namespace)
        CommitteeWitnesses.model_rebuild(_types_namespace=namespace)
        CommitteeWitnessDocument.model_rebuild(_types_namespace=namespace)
        CommitteeWitnessDocuments.model_rebuild(_types_namespace=namespace)
        CommitteeMeetingDocument.model_rebuild(_types_namespace=namespace)
        CommitteeHearingTranscript.model_rebuild(_types_namespace=namespace)
        RelatedItems.model_rebuild(_types_namespace=namespace)
        
        # Nomination classes
        Nomination.model_rebuild(_types_namespace=namespace)
        Nominations.model_rebuild(_types_namespace=namespace)
        Nominee.model_rebuild(_types_namespace=namespace)
        Nominees.model_rebuild(_types_namespace=namespace)
        
        logger.debug("All models rebuilt successfully")
    except Exception as e:
        logger.warning("Some models could not be rebuilt: %s", e)
        # Continue anyway - some models might work without rebuild