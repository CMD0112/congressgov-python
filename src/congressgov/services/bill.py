from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.expansion_helpers import propagate_client_to_items
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_bill_type, validate_congress
from congressgov._client.models.get_bill_congress_bill_type_bill_number_format import (
    GetBillCongressBillTypeBillNumberFormat,
)

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bill as BillModel, Bills as BillsModel
    from congressgov._client import AuthenticatedClient
from congressgov._client.api.bill import (
    bill_actions_sync,
    bill_amendments_sync,
    bill_committees_sync,
    bill_cosponsors_sync,
    bill_details_sync,
    bill_relatedbills_sync,
    bill_subjects_sync,
    bill_summaries_sync,
    bill_text_sync,
    bill_titles_sync,
    law_list_by_congress_sync,
    law_list_by_congress_and_law_type_sync,
    law_list_by_congress_law_type_and_law_number_sync
)

from congressgov.models.base.model import ApiEnvelope

# NOTE: Using ModelRegistry for loose coupling (✅ Sprint 2 improvement)
# Models are resolved dynamically instead of direct imports
BillModel = ModelRegistry.get_model("Bill")
BillsModel = ModelRegistry.get_model("Bills")
ActionsModel = ModelRegistry.get_model("Actions")
AmendmentsModel = ModelRegistry.get_model("Amendments")
CommitteesModel = ModelRegistry.get_model("Committees")
CosponsorsModel = ModelRegistry.get_model("Cosponsors")
SubjectModel = ModelRegistry.get_model("Subject")
SummariesModel = ModelRegistry.get_model("Summaries")
TextVersionsModel = ModelRegistry.get_model("TextVersions")
TitlesModel = ModelRegistry.get_model("Titles")

# ✅ Expansion mappings now use registry-resolved models
# NOTE: Exported for use by extension methods on Bill model instances
BILL_MAPPINGS = {
    "actions": {bill_actions_sync: ActionsModel},
    "amendments": {bill_amendments_sync: AmendmentsModel},
    "committees": {bill_committees_sync: CommitteesModel},
    "cosponsors": {bill_cosponsors_sync: CosponsorsModel},
    "relatedBills": {bill_relatedbills_sync: BillsModel},
    "subjects": {bill_subjects_sync: SubjectModel},
    "summaries": {bill_summaries_sync: SummariesModel},
    "textVersions": {bill_text_sync: TextVersionsModel},
    "titles": {bill_titles_sync: TitlesModel}
}

# NOTE: Exported for use by extension methods on Bill model instances
BILL_PARAMETERS = {
    "congress": "congress",
    "bill_type": ["bill_type", "type"],
    "bill_number": ["bill_number", "number"]
}

# NOTE: Export service class and configuration for use by extensions
__all__ = ['Bill', 'BILL_MAPPINGS', 'BILL_PARAMETERS']


class Bill(ApiService):
    """
    Bill service provides API access for fetching Congressional bill data.
    
    This service class handles API interactions for fetching bills from the
    Congress.gov API. Once a bill is fetched, instance methods on the Bill model
    (registered in congressgov.services.extensions.bill) provide additional functionality
    like expanding attributes and fetching related data.
    
    Separation of Concerns:
    - This service class: Fetches data from API (get, search)
    - Bill model extensions: Operate on fetched data (expand, get_actions, etc.)
    - Bills model extensions: Query and filter collections (filter, by_type, etc.)
    
    USAGE EXAMPLES:
        # Basic usage - fetch a bill
        bill_service = Bill(client=my_client)
        bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
        
        # Now use extension methods on the bill instance
        expanded_bill = bill.expand(attributes=['actions', 'cosponsors'])
        actions = bill.get_actions()
        
        # Search for bills
        bills = bill_service.search(congress=118, bill_type="hr", limit=10)
        
        # Use extension methods on Bills collection
        house_bills = bills.by_type("hr")
        enacted = bills.enacted()
    """
    
    def __init__(self, client: 'AuthenticatedClient | None' = None) -> None:
        """
        Initialize Bill service.
        
        Args:
            client: Optional API client instance. Can also be provided per-method.
        """
        self.client = client
        self._last_result: 'BillModel | None' = None  # Store last fetched bill for potential convenience patterns

    def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        bill_type: str,
        bill_number: int,
        format_: str | None = None
    ) -> 'BillModel':
        """
        Retrieve a single bill's details from the API.

        Args:
            client: The API client instance. If None, will use self.client if available.
            congress: Congress number (e.g., 118 for 118th Congress).
            bill_type: Bill type (e.g., 'hr', 's', 'hjres', 'sjres').
            bill_number: Bill number.
            format_: Response format (default: json).

        Returns:
            Bill: Parsed Bill model instance from API response with client attached.
            
        Raises:
            ValidationError: If parameters are invalid (includes suggestions)
            APIError: If API request fails
            ClientNotFoundError: If no client is available
            
        Example:
            >>> bill_service = Bill(client=my_client)
            >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
            >>> # Now use extension methods
            >>> expanded_bill = bill.expand()
            >>> actions = bill.get_actions()
        """
        # CUSTOM: validation
        validate_congress(congress)
        validate_bill_type(bill_type)
        
        # --- <RESOLVE CLIENT PARAMETER> ---
        resolved_client = ApiService._resolve_client(self, client)
        
        # --- <CALL API> ---
        resp = bill_details_sync(
            client=resolved_client,
            congress=congress,
            bill_type=bill_type,
            bill_number=bill_number,
            format_=resolve_response_format(format_, GetBillCongressBillTypeBillNumberFormat),
        )
        
        # --- <PARSE RESPONSE> ---
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        result = BillModel.model_validate(api_env.data)
        
        # --- <ATTACH CLIENT TO RESULT> ---
        # NOTE: This allows extension methods to access the client without explicitly passing it
        result.client = resolved_client
        
        # --- <STORE RESULT> ---
        self._last_result = result
        
        return result

    def search(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        bill_type: str | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None
    ) -> 'BillsModel':
        """
        Search for bills using the universal search system.

        This method provides flexible searching across bills with optional filters.
        It delegates to the universal search system for maintainability.

        Args:
            client: The API client instance. If None, will use self.client if available.
            congress: Congress number to filter by (e.g., 118 for 118th Congress).
            bill_type: Bill type to filter by. Valid values:
                - 'hr': House Bill
                - 's': Senate Bill
                - 'hjres': House Joint Resolution
                - 'sjres': Senate Joint Resolution
                - 'hconres': House Concurrent Resolution
                - 'sconres': Senate Concurrent Resolution
                - 'hres': House Simple Resolution
                - 'sres': Senate Simple Resolution
            format_: Response format (default: json).
            offset: Number of records to skip for pagination.
            limit: Maximum number of records to return (default: 20).
            from_date_time: Return bills updated after this datetime (ISO format).
            to_date_time: Return bills updated before this datetime (ISO format).
            sort: Sort order for results.

        Returns:
            Bills: Collection of bills matching the search criteria with attached client
            for extension methods.
            
        Raises:
            ValidationError: If parameters are invalid (includes suggestions)
            APIError: If API request fails
            ClientNotFoundError: If no client is available
            
        Example:
            >>> from congressgov import Bill
            >>> from congressgov._client import AuthenticatedClient
            >>> 
            >>> client = AuthenticatedClient(token="your-api-key")
            >>> bill_service = Bill(client=client)
            >>> 
            >>> # Search for House bills from 118th Congress
            >>> bills = bill_service.search(congress=118, bill_type="hr", limit=50)
            >>> print(f"Found {len(bills)} House bills")
            >>> 
            >>> # Use collection extension methods
            >>> enacted_bills = bills.enacted()
            >>> by_type = bills.group_by("type")
            >>> 
            >>> # Search with date filters
            >>> recent_bills = bill_service.search(
            ...     from_date_time="2023-01-01T00:00:00Z",
            ...     to_date_time="2023-12-31T23:59:59Z",
            ...     limit=100
            ... )
        """
        # CUSTOM: universal search delegation
        from congressgov.services.core.search import search as universal_search

        return universal_search(
            'bill',
            self,
            client=client,
            congress=congress,
            bill_type=bill_type,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            sort=sort
        )

    def search_by_laws(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        law_type: str | None = None,
        law_number: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> 'BillModel | BillsModel':
        """
        Search for laws using the appropriate API endpoint.

        This function chooses the correct endpoint based on which arguments are provided:
        - If congress, law_type, and law_number: fetch a specific law (returns Bill).
        - If congress and law_type: fetch all laws for that congress and type (returns Bills).
        - If only congress: fetch all laws for that congress (returns Bills).
        - If none: raises ValueError.

        Args:
            client: The API client instance. If None, will use self.client if available.
            congress: Congress number to filter by (optional).
            law_type: Law type to filter by (e.g., 'pub', 'pri') (optional).
            law_number: Law number to filter by (optional).
            format_: Response format (default: json).
            offset: Offset for pagination.
            limit: Limit for pagination.

        Returns:
            Bills or Bill: Parsed model from API response.
                - If searching for a specific law (all three arguments), returns a Bill.
                - Otherwise, returns Bills (list of bills/laws).
                
        Example:
            >>> bill_service = Bill(client=my_client)
            >>> # Get all public laws from 118th Congress
            >>> laws = bill_service.search_by_laws(congress=118, law_type="pub")
            >>> # Get a specific law
            >>> law = bill_service.search_by_laws(congress=118, law_type="pub", law_number=1)
        """
        # CUSTOM: law list endpoints
        resolved_client = ApiService._resolve_client(self, client)
        
        # --- <CHOOSE ENDPOINT BASED ON PROVIDED ARGUMENTS> ---
        if congress is not None:
            if law_type is not None:
                if law_number is not None:
                    # --- <CASE: Specific Law> ---
                    # All three provided: get a specific law (returns a single Bill)
                    resp = law_list_by_congress_law_type_and_law_number_sync(
                        client=resolved_client,
                        congress=congress,
                        law_type=law_type,
                        law_number=law_number,
                        format_=format_,
                        offset=offset,
                        limit=limit,
                    )
                    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
                    result = BillModel.model_validate(api_env.data)
                    result.client = resolved_client
                    return result
                else:
                    # --- <CASE: Laws by Congress and Type> ---
                    # Congress and law_type: get all laws for that congress and type (returns Bills)
                    resp = law_list_by_congress_and_law_type_sync(
                        client=resolved_client,
                        congress=congress,
                        law_type=law_type,
                        format_=format_,
                        offset=offset,
                        limit=limit,
                    )
                    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
                    result = BillsModel.model_validate(api_env.data)
                    result.client = resolved_client
                    propagate_client_to_items(result, "bills", resolved_client)
                    return result
            else:
                # --- <CASE: Laws by Congress> ---
                # Only congress: get all laws for that congress (returns Bills)
                resp = law_list_by_congress_sync(
                    client=resolved_client,
                    congress=congress,
                    format_=format_,
                    offset=offset,
                    limit=limit,
                )
                api_env = ApiEnvelope.model_validate(json.loads(resp.content))
                result = BillsModel.model_validate(api_env.data)
                result.client = resolved_client
                propagate_client_to_items(result, "bills", resolved_client)
                return result
        else:
            # --- <ERROR: No Congress Provided> ---
            # No endpoint for "all laws" without congress, so raise error
            raise ValueError("At least 'congress' must be specified to search laws.")
