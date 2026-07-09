"""
Protocol classes for Amendment and Amendments entities.

These protocols declare all extension method signatures to provide IDE support
for autocomplete and type checking without changing the @register_method system.
"""

from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from congressgov.models.entities.amendment import Amendment, Amendments
    from congressgov.models.actions.action import Actions
    from congressgov.models.entities.amendment import Amendments as RelatedAmendments
    from congressgov.models.entities.sponsor import Cosponsors
    from congressgov.models.entities.bill import TextVersions
    from congressgov.services.extensions.amendments import AmendmentsQuery


class AmendmentProtocol(Protocol):
    """Protocol declaring all extension methods available on Amendment instances."""
    
    def expand(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any
    ) -> 'Amendment':
        """Expand attributes by fetching additional data from API."""
        ...
    
    def expand_specific_attributes(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any
    ) -> 'Amendment':
        """Expand only specific attributes using varargs."""
        ...
    
    def get_available_attributes(self) -> list[str]:
        """Get list of all available attributes that can be expanded."""
        ...
    
    def get_actions(
        self,
        client: Any = None,
        format_: str | None = None,
        **kwargs: Any
    ) -> 'Actions':
        """Get all actions for this amendment."""
        ...
    
    def get_amendments(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'RelatedAmendments':
        """Get all related amendments for this amendment."""
        ...
    
    def get_cosponsors(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'Cosponsors':
        """Get all cosponsors for this amendment."""
        ...
    
    def get_text_versions(
        self,
        client: Any = None,
        format_: str | None = None,
        **kwargs: Any
    ) -> 'TextVersions':
        """Get all text versions for this amendment."""
        ...


class AmendmentsProtocol(Protocol):
    """Protocol declaring all extension methods available on Amendments collections."""
    
    def query(self) -> 'AmendmentsQuery':
        """Get query builder for chaining operations."""
        ...
    
    def filter(
        self, 
        *, 
        lazy: bool = False, 
        **kwargs
    ) -> 'Amendments | AmendmentsQuery':
        """Filter amendments by field values."""
        ...
    
    def by_type(self, amendment_type: str) -> 'Amendments':
        """Get amendments of a specific type."""
        ...
    
    def by_congress(self, congress: int) -> 'Amendments':
        """Get amendments from a specific Congress."""
        ...
    
    def by_chamber(self, chamber: str) -> 'Amendments':
        """Get amendments by originating chamber."""
        ...
    
    def house_amendments(self) -> 'Amendments':
        """Get all House amendments (hamdt)."""
        ...
    
    def senate_amendments(self) -> 'Amendments':
        """Get all Senate amendments (samdt)."""
        ...
    
    def with_actions(self) -> 'Amendments':
        """Get amendments that have actions recorded."""
        ...
    
    def by_sponsor(self, sponsor_name: str) -> 'Amendments':
        """Get amendments by sponsor name (partial match, case-insensitive)."""
        ...
    
    def group_by(self, field: str) -> dict[str, 'Amendments']:
        """Group amendments by field."""
        ...
    
    def __iter__(self) -> 'Amendments':
        """Allow iteration over amendments."""
        ...
    
    def __len__(self) -> int:
        """Support len() function."""
        ...
    
    def __getitem__(self, key: int | slice) -> 'Amendment | Amendments':
        """Support indexing and slicing."""
        ...
    
    def __bool__(self) -> bool:
        """Support truthiness checks."""
        ...
