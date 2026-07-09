from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_chamber, validate_committee_code, validate_congress

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.committee import Committee as CommitteeModel, Committees as CommitteesModel
    from congressgov._client import AuthenticatedClient
from congressgov._client.api.committee import (
    committee_bills_list_async,
    committee_details_async,
    committee_reports_by_committee_async,
    house_communications_by_committee_async,
    nomination_by_committee_async,
    senate_communications_by_committee_async,
)
from congressgov._client.api.committee.get_committee_congress_chamber_committee_code import (
    asyncio_detailed as committee_by_congress_detailed,
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
ASYNC_COMMITTEE_MAPPINGS = {
    "bills": {committee_bills_list_async: BillsModel},
    "reports": {committee_reports_by_committee_async: CommitteeReportsModel},
    "houseCommunications": {house_communications_by_committee_async: HouseCommunicationsModel},
    "senateCommunications": {senate_communications_by_committee_async: SenateCommunicationsModel},
    "nominations": {nomination_by_committee_async: NominationsModel}
}

ASYNC_COMMITTEE_PARAMETERS = {
    "chamber": "chamber",
    "committee_code": ["committee_code", "committeeCode"]
}

__all__ = ['AsyncCommittee', 'ASYNC_COMMITTEE_MAPPINGS', 'ASYNC_COMMITTEE_PARAMETERS']


class AsyncCommittee(AsyncApiService):
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

    async def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        chamber: str,
        committee_code: str,
        format_: str | None = None
    ) -> 'CommitteeModel':
        """Get detailed information about a specific committee."""
        # --- <VALIDATE PARAMETERS> ---
        validate_chamber(chamber)
        validate_committee_code(committee_code)
        
        resolved_client = await AsyncApiService._resolve_client(self, client)
        chamber_param = GetCommitteeChamberCommitteeCodeChamber(chamber.lower())

        response = await committee_details_async(
            client=resolved_client,
            chamber=chamber_param,
            committee_code=committee_code,
            format_=resolve_response_format(format_, GetCommitteeChamberCommitteeCodeFormat),
        )
        response_json = json.loads(response.content)
        
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteeModel.model_validate(api_envelope.data)
        
        result.client = resolved_client
        self._last_result = result
        
        return result

    async def get_by_congress(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        chamber: str,
        committee_code: str,
        format_: str | None = None,
    ) -> 'CommitteeModel':
        """Get committee detail scoped to a specific Congress."""
        validate_congress(congress)
        validate_chamber(chamber)
        validate_committee_code(committee_code)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        chamber_param = GetCommitteeCongressChamberCommitteeCodeChamber(chamber)
        response = await committee_by_congress_detailed(
            client=resolved_client,
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
        result.client = resolved_client
        self._last_result = result
        return result

    async def search(
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
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'committee',
            self,
            client=client,
            congress=congress,
            chamber=chamber,
            format_=format_,
            offset=offset,
            limit=limit
        )
