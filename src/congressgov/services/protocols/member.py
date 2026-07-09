"""
Protocol classes for Member and Members entities.

These protocols declare all extension method signatures to provide IDE support
for autocomplete and type checking without changing the @register_method system.
"""

from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from congressgov.models.entities.member import (
        Member,
        Members,
        SponsoredLegislation,
        CosponsoredLegislation,
    )
    from congressgov.services.extensions.members import MembersQuery


class MemberProtocol(Protocol):
    """Protocol declaring all extension methods available on Member instances."""

    def expand(
        self,
        client: Any = None,
        attributes: list[str] | None = None,
        **kwargs: Any,
    ) -> 'Member':
        """Expand related attributes on this member."""
        ...

    def expand_specific_attributes(
        self,
        *attributes: str,
        client: Any = None,
        **kwargs: Any,
    ) -> 'Member':
        """Expand only the given attributes."""
        ...

    def get_available_attributes(self) -> list[str]:
        """List expandable attribute names."""
        ...
    
    def get_sponsored_legislation(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        refresh: bool = False,
        **kwargs: Any,
    ) -> 'SponsoredLegislation':
        """Load sponsored legislation into ``sponsoredLegislation``."""
        ...

    def get_cosponsored_legislation(
        self,
        client: Any = None,
        format_: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        refresh: bool = False,
        **kwargs: Any,
    ) -> 'CosponsoredLegislation':
        """Load cosponsored legislation into ``cosponsoredLegislation``."""
        ...


class MembersProtocol(Protocol):
    """Protocol declaring all extension methods available on Members collections."""
    
    def query(self) -> 'MembersQuery':
        """Get query builder for chaining operations."""
        ...
    
    def filter(
        self, 
        *, 
        lazy: bool = False, 
        **kwargs
    ) -> 'Members | MembersQuery':
        """Filter members by field values."""
        ...
    
    def by_state(self, state: str) -> 'Members':
        """Get members from a specific state."""
        ...
    
    def by_party(self, party: str) -> 'Members':
        """Get members from a specific party."""
        ...
    
    def by_chamber(self, chamber: str) -> 'Members':
        """Get members from a specific chamber."""
        ...
    
    def house_members(self) -> 'Members':
        """Get all House members."""
        ...
    
    def senate_members(self) -> 'Members':
        """Get all Senate members."""
        ...
    
    def democrats(self) -> 'Members':
        """Get all Democratic members."""
        ...
    
    def republicans(self) -> 'Members':
        """Get all Republican members."""
        ...
    
    def independents(self) -> 'Members':
        """Get all Independent members."""
        ...
    
    def current_members(self) -> 'Members':
        """Get all current members."""
        ...
    
    def by_district(self, district: int) -> 'Members':
        """Get members from a specific district."""
        ...
    
    def by_congress(self, congress: int) -> 'Members':
        """Get members from a specific Congress."""
        ...
    
    def group_by(self, field: str) -> dict[str, 'Members']:
        """Group members by field."""
        ...
    
    def __iter__(self) -> 'Members':
        """Allow iteration over members."""
        ...
    
    def __len__(self) -> int:
        """Support len() function."""
        ...
    
    def __getitem__(self, key: int | slice) -> 'Member | Members':
        """Support indexing and slicing."""
        ...
    
    def __bool__(self) -> bool:
        """Support truthiness checks."""
        ...
