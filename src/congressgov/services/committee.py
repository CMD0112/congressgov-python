from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_chamber, validate_committee_code, validate_congress

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.committee import Committee as CommitteeModel, Committees as CommitteesModel
    from congressgov._client import AuthenticatedClient
from congressgov._client.api.committee import (
    committee_bills_list_sync,
    committee_details_sync,
    committee_reports_by_committee_sync,
    house_communications_by_committee_sync,
    nomination_by_committee_sync,
    senate_communications_by_committee_sync,
)
from congressgov._client.api.committee.get_committee_congress_chamber_committee_code import (
    sync_detailed as committee_by_congress_detailed,
)
from congressgov._client.models.get_committee_chamber_committee_code_chamber import (
    GetCommitteeChamberCommitteeCodeChamber,
)
from congressgov._client.models.get_committee_chamber_committee_code_format import (
    GetCommitteeChamberCommitteeCodeFormat,
)
from congressgov._client.models.get_committee_congress_chamber_committee_code_chamber import (
    GetCommitteeCongressChamberCommitteeCodeChamber,
)
from congressgov._client.models.get_committee_congress_chamber_committee_code_format import (
    GetCommitteeCongressChamberCommitteeCodeFormat,
)

from congressgov.models.base.model import ApiEnvelope

# NOTE: Using ModelRegistry for loose coupling
CommitteeModel = ModelRegistry.get_model("Committee")
CommitteesModel = ModelRegistry.get_model("Committees")
CommitteeReportsModel = ModelRegistry.get_model("CommitteeReports")
HouseCommunicationsModel = ModelRegistry.get_model("HouseCommunications")
SenateCommunicationsModel = ModelRegistry.get_model("SenateCommunications")
BillsModel = ModelRegistry.get_model("Bills")
NominationsModel = ModelRegistry.get_model("Nominations")

# ✅ Expansion mappings - exported for use by extension methods
COMMITTEE_MAPPINGS = {
    "bills": {committee_bills_list_sync: BillsModel},
    "reports": {committee_reports_by_committee_sync: CommitteeReportsModel},
    "houseCommunications": {house_communications_by_committee_sync: HouseCommunicationsModel},
    "senateCommunications": {senate_communications_by_committee_sync: SenateCommunicationsModel},
    "nominations": {nomination_by_committee_sync: NominationsModel}
}

COMMITTEE_PARAMETERS = {
    "chamber": "chamber",
    "committee_code": ["committee_code", "committeeCode"]
}

__all__ = ['Committee', 'COMMITTEE_MAPPINGS', 'COMMITTEE_PARAMETERS']


class Committee(ApiService):
    """
    Committee service provides API access for fetching Congressional committee data.
    
    Separation of Concerns:
    - This service class: Fetches data from API (get, search)
    - Committee model extensions: Operate on fetched data (expand, get_bills, etc.)
    - Committees model extensions: Query and filter collections
    """
    
    def __init__(self, client: 'AuthenticatedClient | None' = None) -> None:
        self.client = client
        self._last_result: 'CommitteeModel | None' = None

    def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        chamber: str,
        committee_code: str,
        format_: str | None = None
    ) -> 'CommitteeModel':
        """Get detailed information about a specific committee."""
        # CUSTOM: validation
        validate_chamber(chamber)
        validate_committee_code(committee_code)
        
        client = ApiService._resolve_client(self, client)
        chamber_param = GetCommitteeChamberCommitteeCodeChamber(chamber.lower())

        response = committee_details_sync(
            client=client,
            chamber=chamber_param,
            committee_code=committee_code,
            format_=resolve_response_format(format_, GetCommitteeChamberCommitteeCodeFormat),
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteeModel.model_validate(api_envelope.data)
        
        result.client = client
        self._last_result = result
        
        return result

    def get_by_congress(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        chamber: str,
        committee_code: str,
        format_: str | None = None,
    ) -> 'CommitteeModel':
        """Get committee detail scoped to a specific Congress."""
        # CUSTOM: congress-scoped committee detail
        validate_congress(congress)
        validate_chamber(chamber)
        validate_committee_code(committee_code)

        client = ApiService._resolve_client(self, client)
        chamber_param = GetCommitteeCongressChamberCommitteeCodeChamber(chamber)
        response = committee_by_congress_detailed(
            client=client,
            congress=congress,
            chamber=chamber_param,
            committee_code=committee_code,
            format_=resolve_response_format(
                format_, GetCommitteeCongressChamberCommitteeCodeFormat
            ),
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteeModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        chamber: str | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None
    ) -> 'CommitteesModel':
        """Search for committees using the universal search system."""
        # CUSTOM: universal search delegation
        from congressgov.services.core.search import search as universal_search

        return universal_search(
            'committee',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
