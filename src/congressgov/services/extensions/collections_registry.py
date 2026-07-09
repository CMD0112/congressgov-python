"""Register list-like protocols on all collection wrapper models."""

from __future__ import annotations

from congressgov.services.extensions._collection_protocols import (
    register_collection_protocols,
)


def register_all_collection_protocols() -> None:
    """Apply shared ``__iter__`` / ``__len__`` / … helpers to every collection model."""
    from congressgov.models.actions.action import Actions
    from congressgov.models.communications.house_communication import HouseCommunications
    from congressgov.models.communications.house_requirement import HouseRequirements
    from congressgov.models.communications.house_vote import HouseVotes
    from congressgov.models.communications.senate_communication import SenateCommunications
    from congressgov.models.committees.committee import Committees
    from congressgov.models.documents.bound_congressional_record import BoundCongressionalRecords
    from congressgov.models.documents.crs_reports import CRSReports
    from congressgov.models.documents.prints import CommitteePrints
    from congressgov.models.documents.reports import CommitteeReports
    from congressgov.models.entities.congress import Congresses
    from congressgov.models.meetings.meeting import CommitteeMeetings
    from congressgov.models.documents.hearing import Hearings
    from congressgov.models.entities.amendment import Amendments
    from congressgov.models.entities.bill import Bills, Summaries
    from congressgov.models.entities.member import (
        CosponsoredLegislation,
        Members,
        SponsoredLegislation,
    )
    from congressgov.models.entities.sponsor import Cosponsors
    from congressgov.models.entities.treaty import Treaties
    from congressgov.models.nominations.nomination import Nominations

    list_collection_specs: list[tuple[type, str]] = [
        (Members, "members"),
        (Bills, "bills"),
        (Amendments, "amendments"),
        (Committees, "committees"),
        (Hearings, "hearings"),
        (Nominations, "nominations"),
        (Treaties, "treaties"),
        (HouseVotes, "houseRollCallVotes"),
        (HouseCommunications, "houseCommunications"),
        (SenateCommunications, "senateCommunications"),
        (CommitteeMeetings, "meetings"),
        (CommitteeReports, "reports"),
        (CommitteePrints, "committeePrints"),
        (Congresses, "congresses"),
        (CRSReports, "crsReports"),
        (HouseRequirements, "houseRequirements"),
        (BoundCongressionalRecords, "boundCongressionalRecord"),
        (SponsoredLegislation, "sponsoredLegislation"),
        (CosponsoredLegislation, "cosponsoredLegislation"),
    ]

    # Bill sub-resource envelopes: keep Model.__repr__, not ``<Name: N items>``.
    subresource_envelope_specs: list[tuple[type, str]] = [
        (Summaries, "summaries"),
        (Actions, "actions"),
        (Cosponsors, "cosponsors"),
    ]

    for collection_class, items_field in list_collection_specs:
        register_collection_protocols(collection_class, items_field, register_repr=True)

    for collection_class, items_field in subresource_envelope_specs:
        register_collection_protocols(collection_class, items_field, register_repr=False)


register_all_collection_protocols()
