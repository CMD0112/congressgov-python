"""
Protocol classes for IDE type hinting and autocomplete support.

These Protocol classes declare all extension method signatures without changing
the runtime behavior of the @register_method system. They provide IDE support
for autocomplete and type checking while maintaining the existing architecture.

Usage:
    from congressgov.services.protocols import BillProtocol, BillsProtocol
    # These are used internally for type hints only
"""

from .bill import BillProtocol, BillsProtocol
from .amendment import AmendmentProtocol, AmendmentsProtocol
from .member import MemberProtocol, MembersProtocol
from .committee import CommitteeProtocol, CommitteesProtocol
from .async_bill import AsyncBillProtocol
from .async_amendment import AsyncAmendmentProtocol
from .async_member import AsyncMemberProtocol
from .async_committee import AsyncCommitteeProtocol

__all__ = [
    'BillProtocol',
    'BillsProtocol',
    'AmendmentProtocol',
    'AmendmentsProtocol',
    'MemberProtocol',
    'MembersProtocol',
    'CommitteeProtocol',
    'CommitteesProtocol',
    'AsyncBillProtocol',
    'AsyncAmendmentProtocol',
    'AsyncMemberProtocol',
    'AsyncCommitteeProtocol',
]
