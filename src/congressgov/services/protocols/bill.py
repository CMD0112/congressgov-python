"""
Protocol classes for Bill and Bills entities.

These protocols declare all extension method signatures to provide IDE support
for autocomplete and type checking without changing the @register_method system.
"""

from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from congressgov.models.entities.bill import Bill, Bills
    from congressgov.models.actions.action import Actions
    from congressgov.models.entities.amendment import Amendments
    from congressgov.models.committees.committee import Committees
    from congressgov.models.entities.sponsor import Cosponsors
    from congressgov.models.entities.bill import Bills as RelatedBills
    from congressgov.models.core.core import Subject
    from congressgov.models.entities.bill import Summaries
    from congressgov.models.entities.bill import TextVersions
    from congressgov.models.core.core import Titles
    from congressgov.services.extensions.bill import BillsQuery


class BillProtocol(Protocol):
    """Protocol declaring all extension methods available on Bill instances."""
    
    def expand(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any
    ) -> 'Bill':
        """Expand attributes by fetching additional data from API."""
        ...
    
    def expand_specific_attributes(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any
    ) -> 'Bill':
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
        """Get all actions for this bill."""
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
    ) -> 'Amendments':
        """Get all amendments for this bill."""
        ...
    
    def get_committees(
        self,
        client: Any = None,
        format_: str | None = None,
        **kwargs: Any
    ) -> 'Committees':
        """Get all committees for this bill."""
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
        """Get all cosponsors for this bill."""
        ...
    
    def get_related_bills(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'RelatedBills':
        """Get all related bills for this bill."""
        ...
    
    def get_subjects(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'Subject':
        """Get all subjects for this bill."""
        ...
    
    def get_summaries(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'Summaries':
        """Get all summaries for this bill."""
        ...
    
    def get_text_versions(
        self,
        client: Any = None,
        format_: str | None = None,
        **kwargs: Any
    ) -> 'TextVersions':
        """Get all text versions for this bill."""
        ...
    
    def get_titles(
        self,
        client: Any = None,
        format_: str | None = None,
        **kwargs: Any
    ) -> 'Titles':
        """Get all titles for this bill."""
        ...


class BillsProtocol(Protocol):
    """Protocol declaring all extension methods available on Bills collections."""
    
    def query(self) -> 'BillsQuery':
        """Get query builder for chaining operations."""
        ...
    
    def filter(
        self, 
        *, 
        lazy: bool = False, 
        **kwargs
    ) -> 'Bills | BillsQuery':
        """Filter bills by field values."""
        ...
    
    def by_type(self, bill_type: str) -> 'Bills':
        """Get bills of a specific type."""
        ...
    
    def by_congress(self, congress: int) -> 'Bills':
        """Get bills from a specific Congress."""
        ...
    
    def by_chamber(self, chamber: str) -> 'Bills':
        """Get bills by originating chamber."""
        ...
    
    def house_bills(self) -> 'Bills':
        """Get all House bills (hr, hres, hjres, hconres)."""
        ...
    
    def senate_bills(self) -> 'Bills':
        """Get all Senate bills (s, sres, sjres, sconres)."""
        ...
    
    def resolutions(self) -> 'Bills':
        """Get all resolutions (hres, sres, hjres, sjres, hconres, sconres)."""
        ...
    
    def joint_resolutions(self) -> 'Bills':
        """Get joint resolutions only (hjres, sjres)."""
        ...
    
    def enacted(self) -> 'Bills':
        """Get bills that became law."""
        ...
    
    def with_actions(self) -> 'Bills':
        """Get bills that have actions recorded."""
        ...
    
    def by_sponsor(self, sponsor_name: str) -> 'Bills':
        """Get bills by sponsor name (partial match, case-insensitive)."""
        ...
    
    def group_by(self, field: str) -> dict[str, 'Bills']:
        """Group bills by field."""
        ...
    
    def __iter__(self) -> 'Bills':
        """Allow iteration over bills."""
        ...
    
    def __len__(self) -> int:
        """Support len() function."""
        ...
    
    def __getitem__(self, key: int | slice) -> 'Bill | Bills':
        """Support indexing and slicing."""
        ...
    
    def __bool__(self) -> bool:
        """Support truthiness checks."""
        ...
