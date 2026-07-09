from __future__ import annotations
import json
from typing import Any, TYPE_CHECKING
from congressgov.services.api_format import resolve_response_format
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.config import MAX_PAGINATION_LIMIT
from congressgov.services.core.expansion_helpers import propagate_client_to_items
from congressgov.services.core.member_list_pagination import paginate_members_async
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.validation import validate_bioguide_id, validate_congress
from congressgov._client.models.get_member_format import GetMemberFormat

# Import types for type hints only (avoids circular imports at runtime)
if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov._client.api.member import (
    member_congress_list_async,
    member_cosponsorship_list_async,
    member_details_async,
    member_list_by_congress_state_district_async,
    member_list_by_state_and_district_async,
    member_list_by_state_async,
    member_list_async,
    member_sponsorship_list_async,
)

from congressgov.models.base.model import ApiEnvelope

# NOTE: Import Members directly to get extension methods
# The ModelRegistry pattern is used for other models, but Members needs
# the direct import to get dynamically-registered query methods
from congressgov.models.entities.member import Member as MemberModel, Members as MembersModel

# Use ModelRegistry for other models
CosponsoredLegislationModel = ModelRegistry.get_model("CosponsoredLegislation")
SponsoredLegislationModel = ModelRegistry.get_model("SponsoredLegislation")

ASYNC_MEMBER_MAPPINGS = {
    "sponsoredLegislation": {member_sponsorship_list_async: SponsoredLegislationModel},
    "cosponsoredLegislation": {member_cosponsorship_list_async: CosponsoredLegislationModel},
}

ASYNC_MEMBER_PARAMETERS = {
    "bioguide_id": ["bioguideId", "bioguide_id"],
}

# NOTE: Export service class and configuration
__all__ = ['AsyncMember', 'ASYNC_MEMBER_MAPPINGS', 'ASYNC_MEMBER_PARAMETERS']


class AsyncMember(AsyncApiService):
    """
    Member service provides API access for fetching Congressional member data.
    
    This service class handles API interactions for fetching member information from the
    Congress.gov API. Once a member is fetched, instance methods on the Member model
    (registered in congressgov.services.extensions.members) provide additional functionality
    like fetching sponsored/cosponsored legislation.
    
    Separation of Concerns:
    - This service class: Fetches data from API (get, search, get_current_roster)
    - Member model extensions: Operate on fetched data (get_sponsored_legislation, etc.)
    - Members model extensions: Query and filter collections (filter, by_state, etc.)
    
    USAGE EXAMPLES:
        # Basic usage - fetch a member
        member_service = Member(client=my_client)
        member = member_service.get(bioguide_id="A000374")
        
        # Now use extension methods on the member instance
        sponsored = member.get_sponsored_legislation()
        cosponsored = member.get_cosponsored_legislation()
        
        # Search for members
        members = member_service.search(state="CA", limit=10)
        
        # Use extension methods on Members collection
        democrats = members.democrats()
        by_state = members.group_by("state")
        
        # Get current roster
        roster = member_service.get_current_roster()
        house_members = roster['house_members']
        senate_members = roster['senate_members']
    """
    
    def __init__(self, client: 'AuthenticatedClient | None' = None) -> None:
        """
        Initialize Member service.
        
        Args:
            client: Optional API client instance. Can also be provided per-method.
        """
        self.client = client
        self._last_result: 'MemberModel | None' = None  # Store last fetched member

    async def get(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        bioguide_id: str,
        format_: str | None = None
    ) -> 'MemberModel':
        """
        Get detailed information about a specific member from the API.
        
        Args:
            client: The API client instance. If None, will use self.client if available.
            bioguide_id: The member's Bioguide ID (e.g., "A000374").
            format_: Response format (default: json).
            
        Returns:
            Member: The member details with client attached.
            
        Raises:
            ValidationError: If parameters are invalid (includes suggestions)
            APIError: If API request fails
            ClientNotFoundError: If no client is available
            
        Example:
            >>> member_service = Member(client=my_client)
            >>> member = member_service.get(bioguide_id="A000374")
            >>> # Now use extension methods
            >>> sponsored = member.get_sponsored_legislation()
        """
        # --- <VALIDATE PARAMETERS> ---
        validate_bioguide_id(bioguide_id)
        
        # --- <RESOLVE CLIENT> ---
        resolved_client = await AsyncApiService._resolve_client(self, client)
        resolved_format = resolve_response_format(format_, GetMemberFormat)
        
        # --- <MAKE API CALL> ---
        response = await member_details_async(
            client=resolved_client, bioguide_id=bioguide_id, format_=resolved_format
        )
        response_json = json.loads(response.content)
        
        # --- <VALIDATE AND PARSE RESPONSE> ---
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = MemberModel.model_validate(api_envelope.data)
        
        # --- <ATTACH CLIENT TO RESULT> ---
        # NOTE: This allows extension methods to access the client without explicitly passing it
        result.client = resolved_client
        
        # --- <STORE FOR POTENTIAL CONVENIENCE> ---
        self._last_result = result
        
        return result

    async def _fetch_members(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        state: str | None = None,
        district: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        current_member: str | bool | None = None,
    ) -> 'MembersModel':
        """List members via the appropriate member API endpoint."""
        resolved_client = await AsyncApiService._resolve_client(self, client)
        resolved_format = resolve_response_format(format_, GetMemberFormat)

        if congress is not None and state is not None and district is not None:
            response = await member_list_by_congress_state_district_async(
                client=resolved_client,
                congress=congress,
                state_code=state,
                district=district,
                format_=resolved_format,
                limit=limit,
            )
        elif state is not None and district is not None:
            response = await member_list_by_state_and_district_async(
                client=resolved_client,
                state_code=state,
                district=district,
                format_=resolved_format,
                current_member=current_member,
            )
        elif state is not None:
            response = await member_list_by_state_async(
                client=resolved_client,
                state_code=state,
                format_=resolved_format,
                limit=limit,
                current_member=current_member,
            )
        else:
            response = await member_list_async(
                client=resolved_client,
                format_=resolved_format,
                offset=offset,
                limit=limit,
                from_date_time=from_date_time,
                to_date_time=to_date_time,
                current_member=current_member,
            )

        api_envelope = ApiEnvelope.model_validate(json.loads(response.content))
        result = MembersModel.model_validate(api_envelope.data)
        result.client = resolved_client
        propagate_client_to_items(result, "members", resolved_client)
        return result

    async def search(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int | None = None,
        state: str | None = None,
        district: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        current_member: str | None = None
    ) -> 'MembersModel':
        """
        Search for members with optional filters using the universal search system.

        Args:
            client: The API client instance. If None, will use self.client if available.
            congress: The Congress number (e.g., 117, 118). Optional.
            state: The state abbreviation (e.g., "CA", "NY"). Optional.
            district: The district number. Optional.
            format_: Response format (default: json).
            offset: Number of records to skip. Optional.
            limit: Maximum number of records to return. Optional.
            from_date_time: Return members updated after this datetime (ISO format). Optional.
            to_date_time: Return members updated before this datetime (ISO format). Optional.
            current_member: Filter for current members ("true" or "false"). Optional.

        Returns:
            Members: List of members matching the search criteria.
            
        Example:
            >>> member_service = Member(client=my_client)
            >>> members = member_service.search(state="CA", current_member="true")
            >>> # Now use collection extension methods
            >>> democrats = members.democrats()
            >>> by_party = members.group_by("partyName")
        """
        return await self._fetch_members(
            client=client,
            congress=congress,
            state=state,
            district=district,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
            current_member=current_member,
        )

    async def _list_by_congress_page(
        self,
        *,
        client: 'AuthenticatedClient',
        congress: int,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        current_member: bool | None = None,
    ) -> 'MembersModel':
        response = await member_congress_list_async(
            client=client,
            congress=congress,
            format_=format_,
            offset=offset,
            limit=limit,
            current_member=current_member,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = MembersModel.model_validate(api_envelope.data)
        result.client = client
        propagate_client_to_items(result, "members", client)
        return result

    async def list_by_congress(
        self,
        *,
        client: 'AuthenticatedClient | None' = None,
        congress: int,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        current_member: bool | None = None,
        fetch_all: bool = False,
    ) -> 'MembersModel':
        """List members who served in a specific Congress.

        When ``fetch_all`` is True, requests pages of up to 250 members until the
        API returns a short or empty page. ``offset`` is ignored in that mode;
        ``limit`` sets the per-request page size (default 250).
        """
        validate_congress(congress)

        resolved_client = await AsyncApiService._resolve_client(self, client)
        if not fetch_all:
            return await self._list_by_congress_page(
                client=resolved_client,
                congress=congress,
                format_=format_,
                offset=offset,
                limit=limit,
                current_member=current_member,
            )

        page_size = limit if limit is not None else MAX_PAGINATION_LIMIT
        return await paginate_members_async(
            lambda off, lim: self._list_by_congress_page(
                client=resolved_client,
                congress=congress,
                format_=format_,
                offset=off,
                limit=lim,
                current_member=current_member,
            ),
            page_size=page_size,
        )

    async def get_current_roster(
        self,
        *,
        client: Any = None
    ) -> dict[str, MembersModel]:
        """
        Get the current roster of members, separated by House and Senate.
        
        This method fetches all current members and separates them into House and Senate
        based on their most recent term.

        Args:
            client: The API client instance. If None, will use self.client if available.

        Returns:
            dict: Dictionary with keys 'house_members' and 'senate_members',
                  each containing a Members model with the respective members.
                  
        Example:
            >>> member_service = Member(client=my_client)
            >>> roster = member_service.get_current_roster()
            >>> house = roster['house_members']  # Members object
            >>> senate = roster['senate_members']  # Members object
            >>> print(f"House: {len(house)}, Senate: {len(senate)}")
        """
        # --- <RESOLVE CLIENT> ---
        resolved_client = await AsyncApiService._resolve_client(self, client)

        house_members = []
        senate_members = []

        # --- <COLLECT ALL CURRENT MEMBERS> ---
        # NOTE: Paginate to completion (like list_by_congress(fetch_all=True))
        # instead of hard-capping at a fixed number of pages.
        all_members = await paginate_members_async(
            lambda off, lim: self._fetch_members(
                client=resolved_client,
                current_member="true",
                offset=off,
                limit=lim,
            ),
            page_size=MAX_PAGINATION_LIMIT,
        )
        member_list = all_members.members or []

        # --- <SEPARATE BY CHAMBER> ---
        for member in member_list:
            # Handle possible edge cases if terms or terms.item is missing
            if not member.terms or not getattr(member.terms, "item", None):
                continue
                
            # Defensive: handle if item is not a list
            terms_items = getattr(member.terms, "item", [])
            if not isinstance(terms_items, list):
                terms_items = [terms_items] if terms_items is not None else []
            if not terms_items:
                continue
                
            # Get latest term by startYear (fall back to -inf if not present)
            latest_term = max(terms_items, key=lambda t: getattr(t, "startYear", float('-inf')) or float('-inf'))
            chamber = getattr(latest_term, "chamber", None)
            
            if chamber == "House of Representatives":
                house_members.append(member)
            elif chamber == "Senate":
                senate_members.append(member)
            # If chamber is something else or None, skip

        # --- <RETURN SEPARATED ROSTERS> ---
        house = MembersModel.model_validate(dict(members=house_members))
        senate = MembersModel.model_validate(dict(members=senate_members))
        house.client = resolved_client
        senate.client = resolved_client
        propagate_client_to_items(house, "members", resolved_client)
        propagate_client_to_items(senate, "members", resolved_client)
        return dict(house_members=house, senate_members=senate)
