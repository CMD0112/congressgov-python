"""
Summary-related classes for congressgov models

This module contains classes for bill summaries and related text.
Note: Summary and Summaries classes have been moved to bill.py to avoid circular imports.
"""

from ..entities.bill import Summary, Summaries

__all__ = [
    "Summary",
    "Summaries",
]
