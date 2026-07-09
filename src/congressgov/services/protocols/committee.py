"""
Protocol classes for Committee and Committees entities.

These protocols declare all extension method signatures to provide IDE support
for autocomplete and type checking without changing the @register_method system.
"""

from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from congressgov.models.committees.committee import Committee, Committees
    from congressgov.models.entities.bill import Bills
    from congressgov.models.documents.reports import CommitteeReports
    from congressgov.models.communications.house_communication import HouseCommunications
    from congressgov.models.communications.senate_communication import SenateCommunications
    from congressgov.models.nominations.nomination import Nominations
    from congressgov.services.extensions.committees import CommitteesQuery


class CommitteeProtocol(Protocol):
    """Protocol declaring all extension methods available on Committee instances."""
    
    def expand(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any
    ) -> 'Committee':
        """Expand attributes by fetching additional data from API."""
        ...
    
    def expand_specific_attributes(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any
    ) -> 'Committee':
        """Expand only specific attributes using varargs."""
        ...
    
    def get_available_attributes(self) -> list[str]:
        """Get list of all available attributes that can be expanded."""
        ...
    
    def get_bills(
        self,
        client: Any = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'Bills':
        """Get all bills for this committee."""
        ...
    
    def get_reports(
        self,
        client: Any = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'CommitteeReports':
        """Get all reports for this committee."""
        ...
    
    def get_house_communications(
        self,
        client: Any = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'HouseCommunications':
        """Get all House communications for this committee."""
        ...
    
    def get_senate_communications(
        self,
        client: Any = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'SenateCommunications':
        """Get all Senate communications for this committee."""
        ...
    
    def get_nominations(
        self,
        client: Any = None,
        congress: int | None = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date_time: str | None = None,
        to_date_time: str | None = None,
        sort: str | None = None,
        **kwargs: Any
    ) -> 'Nominations':
        """Get all nominations for this committee."""
        ...


class CommitteesProtocol(Protocol):
    """Protocol declaring all extension methods available on Committees collections."""
    
    def query(self) -> 'CommitteesQuery':
        """Get query builder for chaining operations."""
        ...
    
    def filter(
        self, 
        *, 
        lazy: bool = False, 
        **kwargs
    ) -> 'Committees | CommitteesQuery':
        """Filter committees by field values."""
        ...
    
    def by_chamber(self, chamber: str) -> 'Committees':
        """Get committees from a specific chamber."""
        ...
    
    def by_congress(self, congress: int) -> 'Committees':
        """Get committees from a specific Congress."""
        ...
    
    def house_committees(self) -> 'Committees':
        """Get all House committees."""
        ...
    
    def senate_committees(self) -> 'Committees':
        """Get all Senate committees."""
        ...
    
    def joint_committees(self) -> 'Committees':
        """Get all joint committees."""
        ...
    
    def by_type(self, committee_type: str) -> 'Committees':
        """Get committees of a specific type."""
        ...
    
    def standing_committees(self) -> 'Committees':
        """Get all standing committees."""
        ...
    
    def select_committees(self) -> 'Committees':
        """Get all select committees."""
        ...
    
    def subcommittees(self) -> 'Committees':
        """Get all subcommittees."""
        ...
    
    def group_by(self, field: str) -> dict[str, 'Committees']:
        """Group committees by field."""
        ...
    
    def __iter__(self) -> 'Committees':
        """Allow iteration over committees."""
        ...
    
    def __len__(self) -> int:
        """Support len() function."""
        ...
    
    def __getitem__(self, key: int | slice) -> 'Committee | Committees':
        """Support indexing and slicing."""
        ...
    
    def __bool__(self) -> bool:
        """Support truthiness checks."""
        ...
