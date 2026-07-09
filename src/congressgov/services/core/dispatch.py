"""
Dispatch module for congressgov.services endpoint management.

This module provides:
- Dispatch: Primary user-facing class for accessing API service endpoints
- Helper functions for dynamic service class loading

Best Practices:
- Lazy loading of service classes to avoid circular imports
- Caching for performance
- Clear error messages for invalid endpoints
"""

from __future__ import annotations

from typing import Any, Optional

# NOTE: Global cache to prevent repeated imports
_classes_dict_cache: Optional[dict[str, Any]] = None


def _get_classes_dict() -> dict[str, Any]:
    """
    Lazy-load service classes to avoid circular imports.
    
    NOTE: Imports are performed at function call time, not module load time.
    This prevents circular import issues that would occur if these were
    imported at the top of the module.
    
    Returns:
        Dictionary mapping endpoint names to service classes
    """
    # NOTE: Import service classes locally to avoid circular dependencies
    from congressgov.services.bill import Bill
    from congressgov.services.amendment import Amendment
    from congressgov.services.summaries import Summaries
    from congressgov.services.congress import Congress
    from congressgov.services.member import Member
    from congressgov.services.house_vote import HouseVote
    from congressgov.services.committee import Committee
    from congressgov.services.committee_report import CommitteeReport
    from congressgov.services.committee_print import CommitteePrint
    from congressgov.services.committee_meeting import CommitteeMeeting
    from congressgov.services.hearing import Hearing
    from congressgov.services.congressional_record import CongressionalRecord
    from congressgov.services.bound_congressional_record import BoundCongressionalRecord
    from congressgov.services.house_communication import HouseCommunication
    from congressgov.services.house_requirement import HouseRequirement
    from congressgov.services.senate_communication import SenateCommunication
    from congressgov.services.nomination import Nomination
    from congressgov.services.crsreport import CRSReport
    from congressgov.services.treaty import Treaty

    return {
        "bill": Bill,
        "amendment": Amendment,
        "summaries": Summaries,
        "congress": Congress,
        "member": Member,
        "house-vote": HouseVote,
        "committee": Committee,
        "committee-report": CommitteeReport,
        "committee-print": CommitteePrint,
        "committee-meeting": CommitteeMeeting,
        "hearing": Hearing,
        "congressional-record": CongressionalRecord,
        "bound-congressional-record": BoundCongressionalRecord,
        "house-communication": HouseCommunication,
        "house-requirement": HouseRequirement,
        "senate-communication": SenateCommunication,
        "nomination": Nomination,
        "crsreport": CRSReport,
        "treaty": Treaty
    }


def get_classes_dict() -> dict[str, Any]:
    """
    Get service classes dictionary with caching.
    
    NOTE: First call loads all classes, subsequent calls return cached dict.
    This provides a good balance between lazy loading and performance.
    
    Returns:
        Dictionary mapping endpoint names to service classes
    """
    global _classes_dict_cache
    if _classes_dict_cache is None:
        _classes_dict_cache = _get_classes_dict()
    return _classes_dict_cache


class Dispatch:
    """
    Primary user-facing class for accessing API service endpoints.
    
    Provides dynamic endpoint access with automatic client injection.
    This class serves as the main entry point for working with the congressgov.services layer.
    
    Attributes:
        client: API client instance injected into all endpoint services
    
    Examples:
        Basic usage with API gateway:
        
        >>> from congressgov.services.core.gateway import ApiGateway
        >>> from congressgov.services.core.dispatch import Dispatch
        >>> 
        >>> # Create client and dispatcher
        >>> client = ApiGateway("https://api.congress.gov/v3", api_key="your-key")
        >>> dispatch = Dispatch(client=client)
        >>> 
        >>> # Access services and fetch data
        >>> bill_service = dispatch.endpoint("bill")
        >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
        >>> 
        >>> # Access multiple services
        >>> member_service = dispatch.endpoint("member")
        >>> committee_service = dispatch.endpoint("committee")
        
        Common endpoint names:
        - "bill", "amendment", "member", "congress"
        - "committee", "committee-meeting", "committee-report", "committee-print"
        - "hearing", "nomination", "treaty"
        - "house-communication", "senate-communication"
        - "congressional-record", "bound-congressional-record", "crsreport"
    """
    
    def __init__(self, client: Any) -> None:
        """
        Initialize dispatcher with API client.
        
        The client will be automatically injected into all endpoint services
        accessed through this dispatcher.
        
        Args:
            client: API client instance to inject into endpoint services.
                   Typically an instance of ApiGateway or congressgov._client.Client
                   
        Example:
            >>> client = ApiGateway("https://api.congress.gov/v3", api_key="key")
            >>> dispatch = Dispatch(client=client)
        """
        self.client = client

    def endpoint(self, endpoint_name: str) -> Any:
        """
        Get an API service by endpoint name.
        
        Dynamically loads and instantiates the requested service class
        with the configured client.
        
        Args:
            endpoint_name: Name of endpoint (e.g., "bill", "congress", "member").
                          Use lowercase with hyphens for multi-word names
                          (e.g., "committee-report", "house-communication")
            
        Returns:
            Service instance with client injected
            
        Raises:
            KeyError: If endpoint name is not recognized. The error message
                     includes a list of all available endpoints.
            
        Example:
            >>> # Get bill service
            >>> bill_service = dispatch.endpoint("bill")
            >>> bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
            >>> 
            >>> # Get committee service
            >>> committee_service = dispatch.endpoint("committee")
        """
        classes = get_classes_dict()
        
        if endpoint_name not in classes:
            # NOTE: Provide helpful error message with available options
            available = ', '.join(sorted(classes.keys()))
            raise KeyError(
                f"Endpoint '{endpoint_name}' is not recognized. "
                f"Available endpoints: {available}"
            )
        
        # NOTE: Instantiate service class with client
        return classes[endpoint_name](client=self.client)

