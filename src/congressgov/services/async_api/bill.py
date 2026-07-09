from __future__ import annotations
import json
from typing import Any, TYPE_CHECKING, AsyncIterator
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.expansion_helpers import propagate_client_to_items
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_bill_type, validate_congress

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bill as BillModel, Bills as BillsModel
    from congressgov._client import AuthenticatedClient

# Import async versions of API functions
from congressgov._client.api.bill import (
    bill_actions_async,
    bill_amendments_async,
    bill_committees_async,
    bill_cosponsors_async,
    bill_details_async,
    bill_list_all_async,
    bill_list_by_congress_async,
    bill_list_by_type_async,
    bill_relatedbills_async,
    bill_subjects_async,
    bill_summaries_async,
    bill_text_async,
    bill_titles_async,
    law_list_by_congress_async,
    law_list_by_congress_and_law_type_async,
    law_list_by_congress_law_type_and_law_number_async,
)

from congressgov.models.base.model import ApiEnvelope

# NOTE: Using ModelRegistry for loose coupling (same as sync version)
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

# ✅ Async expansion mappings using async API functions
# NOTE: Exported for use by async extension methods on Bill model instances
ASYNC_BILL_MAPPINGS = {
    "actions": {bill_actions_async: ActionsModel},
    "amendments": {bill_amendments_async: AmendmentsModel},
    "committees": {bill_committees_async: CommitteesModel},
    "cosponsors": {bill_cosponsors_async: CosponsorsModel},
    "relatedBills": {bill_relatedbills_async: BillsModel},
    "subjects": {bill_subjects_async: SubjectModel},
    "summaries": {bill_summaries_async: SummariesModel},
    "textVersions": {bill_text_async: TextVersionsModel},
    "titles": {bill_titles_async: TitlesModel}
}

# NOTE: Same parameters as sync version
ASYNC_BILL_PARAMETERS = {
    "congress": "congress",
    "bill_type": ["bill_type", "type"],
    "bill_number": ["bill_number", "number"]
}

# NOTE: Export service class and configuration for use by extensions
__all__ = ['AsyncBill', 'ASYNC_BILL_MAPPINGS', 'ASYNC_BILL_PARAMETERS']


class AsyncBill(AsyncApiService):
    """
    Async Bill service provides non-blocking API access for fetching Congressional bill data.
    
    This async service class mirrors the sync Bill service but uses async/await for
    non-blocking operations. It handles API interactions asynchronously for fetching bills
    from the Congress.gov API.
    
    Separation of Concerns:
    - This service class: Fetches data from API asynchronously (get, search)
    - Bill model extensions: Operate on fetched data (expand_async, get_actions_async, etc.)
    - Bills model extensions: Query and filter collections (filter, by_type, etc.)
    
    Key Benefits:
    - Non-blocking API calls allow concurrent operations
    - Efficient batch processing with asyncio.gather()
    - Streaming support for large datasets
    - Full compatibility with async frameworks (FastAPI, Django async)
    
    USAGE EXAMPLES:
        # Basic async usage - fetch a bill
        async_bill_service = AsyncBill(client=my_client)
        bill = await async_bill_service.get(congress=118, bill_type="hr", bill_number=1)
        
        # Fetch multiple bills concurrently
        tasks = [
            async_bill_service.get(congress=118, bill_type="hr", bill_number=i)
            for i in range(1, 11)
        ]
        bills = await asyncio.gather(*tasks)
        
        # Search for bills
        bills = await async_bill_service.search(congress=118, bill_type="hr", limit=10)
        
        # Stream large datasets
        async for batch in async_bill_service.search_stream(congress=118, batch_size=50):
            for bill in batch.bills:
                # Process each bill without loading all into memory
                await process_bill(bill)
    """
    
    def __init__(self, client: 'AuthenticatedClient | None' = None) -> None:
        """
        Initialize AsyncBill service.
        
        Args:
            client: Optional API client instance. Can also be provided per-method.
        """
        self.client = client
        self._last_result: 'BillModel | None' = None  # Store last fetched bill

    async def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        bill_type: str,
        bill_number: int,
        format_: str | None = None
    ) -> 'BillModel':
        """
        Retrieve a single bill's details from the API asynchronously.

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
            >>> async_bill_service = AsyncBill(client=my_client)
            >>> bill = await async_bill_service.get(congress=118, bill_type="hr", bill_number=1)
            >>> # Now use async extension methods
            >>> expanded_bill = await bill.expand_async()
            >>> actions = await bill.get_actions_async()
        """
        # --- <VALIDATE PARAMETERS> ---
        validate_congress(congress)
        validate_bill_type(bill_type)
        
        # --- <RESOLVE CLIENT PARAMETER> ---
        resolved_client = await AsyncApiService._resolve_client(self, client)
        
        # --- <CALL ASYNC API> ---
        resp = await bill_details_async(
            congress=congress,
            bill_type=bill_type,
            bill_number=bill_number,
            client=resolved_client,
            format_=format_ or 'json'
        )
        
        # --- <PARSE AND RETURN> ---
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        bill = BillModel.model_validate(api_env.data)
        
        # Attach client for extension methods
        bill.client = resolved_client
        
        # Store last result
        self._last_result = bill
        
        return bill

    async def search(
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
        Search for bills using the universal search system asynchronously.
        
        This method provides flexible searching across bills with optional filters.
        
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
            offset: Pagination offset (number of records to skip).
            limit: Maximum number of results to return (default: 20).
            from_date_time: Start date/time for filtering (ISO 8601 format).
            to_date_time: End date/time for filtering (ISO 8601 format).
            sort: Sort order (e.g., 'updateDate+desc').
            
        Returns:
            Bills: Collection of bills matching the search criteria with attached client
            for extension methods.
            
        Raises:
            ValidationError: If parameters are invalid (includes suggestions)
            APIError: If API request fails
            ClientNotFoundError: If no client is available
            
        Example:
            >>> async_bill_service = AsyncBill(client=my_client)
            >>> 
            >>> # Search for House bills from 118th Congress
            >>> bills = await async_bill_service.search(congress=118, bill_type="hr", limit=50)
            >>> print(f"Found {len(bills.bills)} House bills")
            >>> 
            >>> # Search with date filters
            >>> bills = await async_bill_service.search(
            ...     congress=118,
            ...     from_date_time="2023-01-01T00:00:00Z",
            ...     to_date_time="2023-12-31T23:59:59Z",
            ...     limit=100
            ... )
        """
        # --- <VALIDATE PARAMETERS> ---
        if congress is not None:
            validate_congress(congress)
        if bill_type is not None:
            validate_bill_type(bill_type)
        
        # --- <RESOLVE CLIENT PARAMETER> ---
        resolved_client = await AsyncApiService._resolve_client(self, client)
        
        # --- <DETERMINE WHICH SEARCH FUNCTION TO USE> ---
        if congress and bill_type:
            # Search by both congress and type
            resp = await bill_list_by_type_async(
                congress=congress,
                bill_type=bill_type,
                client=resolved_client,
                format_=format_ or 'json',
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
                sort=sort
            )
        elif congress:
            # Search by congress only
            resp = await bill_list_by_congress_async(
                congress=congress,
                client=resolved_client,
                format_=format_ or 'json',
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
                sort=sort
            )
        else:
            # Search all bills
            resp = await bill_list_all_async(
                client=resolved_client,
                format_=format_ or 'json',
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
                sort=sort
            )
        
        # --- <PARSE AND RETURN> ---
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        bills = BillsModel.model_validate(api_env.data)
        
        # Attach client for extension methods
        bills.client = resolved_client
        propagate_client_to_items(bills, "bills", resolved_client)
        
        return bills

    async def search_stream(
        self,
        *,
        congress: int | None = None,
        bill_type: str | None = None,
        batch_size: int = 100,
        **kwargs: Any
    ) -> AsyncIterator['BillsModel']:
        """
        Stream bills in batches for memory-efficient processing of large datasets.
        
        This method yields batches of bills without loading the entire result set
        into memory at once. Ideal for processing thousands of bills.
        
        Args:
            congress: Congress number to filter by.
            bill_type: Bill type to filter by.
            batch_size: Number of bills per batch (default: 100).
            **kwargs: Additional search parameters (from_date_time, to_date_time, etc.)
            
        Yields:
            BillsModel: Batches of bills
            
        Example:
            >>> async_bill_service = AsyncBill(client=my_client)
            >>> 
            >>> # Stream and process bills in batches
            >>> async for batch in async_bill_service.search_stream(
            ...     congress=118,
            ...     batch_size=50
            ... ):
            ...     for bill in batch.bills:
            ...         # Process each bill
            ...         await process_bill(bill)
            ...     print(f"Processed batch of {len(batch.bills)} bills")
        """
        offset = 0
        stream_kwargs = dict(kwargs)
        stream_kwargs.pop("limit", None)
        while True:
            batch = await self.search(
                congress=congress,
                bill_type=bill_type,
                offset=offset,
                limit=batch_size,
                **stream_kwargs,
            )
            
            if not batch.bills or len(batch.bills) == 0:
                break
            
            yield batch
            if len(batch.bills) < batch_size:
                break
            offset += batch_size

    async def search_by_laws(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        law_type: str | None = None,
        law_number: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None
    ) -> 'BillModel | BillsModel':
        """
        Search for bills by public or private law asynchronously.
        
        Args:
            client: The API client instance.
            congress: Congress number.
            law_type: Law type ('pub' or 'priv').
            law_number: Specific law number.
            format_: Response format.
            offset: Pagination offset.
            limit: Maximum results.
            
        Returns:
            BillModel or BillsModel depending on search specificity.
            
        Example:
            >>> # Get specific public law
            >>> bill = await async_bill_service.search_by_laws(
            ...     congress=117,
            ...     law_type="pub",
            ...     law_number=108
            ... )
        """
        # --- <VALIDATE PARAMETERS> ---
        if congress is not None:
            validate_congress(congress)
        
        # --- <RESOLVE CLIENT> ---
        resolved_client = await AsyncApiService._resolve_client(self, client)
        
        # --- <CALL ASYNC API> ---
        if congress and law_type and law_number:
            # Specific law
            resp = await law_list_by_congress_law_type_and_law_number_async(
                congress=congress,
                law_type=law_type,
                law_number=law_number,
                client=resolved_client,
                format_=format_ or 'json'
            )
            api_env = ApiEnvelope.model_validate(json.loads(resp.content))
            bill = BillModel.model_validate(api_env.data)
            bill.client = resolved_client
            return bill
        elif congress and law_type:
            # By congress and law type
            resp = await law_list_by_congress_and_law_type_async(
                congress=congress,
                law_type=law_type,
                client=resolved_client,
                format_=format_ or 'json',
                offset=offset,
                limit=limit
            )
        elif congress:
            # By congress only
            resp = await law_list_by_congress_async(
                congress=congress,
                client=resolved_client,
                format_=format_ or 'json',
                offset=offset,
                limit=limit
            )
        else:
            raise ValueError("At least 'congress' parameter must be provided")
        
        # --- <PARSE AND RETURN> ---
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        bills = BillsModel.model_validate(api_env.data)
        bills.client = resolved_client
        propagate_client_to_items(bills, "bills", resolved_client)
        return bills