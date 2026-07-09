"""Tests for PandasIntegration collection handling."""

from __future__ import annotations

from congressgov.models.base.enums import LegislationType
from congressgov.models.entities.bill import Bill, Bills
from congressgov.services.export.base import ExportConfig
from congressgov.services.export.pandas_integration import PandasIntegration


def test_to_dataframe_expands_bills_collection() -> None:
    bills = Bills(
        bills=[
            Bill(congress=118, number=1, type=LegislationType.HR, title="A"),
            Bill(congress=118, number=2, type=LegislationType.S, title="B"),
        ]
    )

    df = PandasIntegration(ExportConfig(flatten_nested=True)).to_dataframe(bills)

    assert len(df) == 2
    assert "type" in df.columns
    assert set(df["type"].astype(str).str.lower().tolist()) == {"hr", "s"}
