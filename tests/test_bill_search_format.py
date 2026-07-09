"""Bill list search must not pass unsupported sort= to generated clients."""

from unittest.mock import MagicMock, patch

import pytest

from congressgov._client.models.get_bill_congress_bill_type_format import (
    GetBillCongressBillTypeFormat,
)
from congressgov.services.core.search import billsearch


def test_billsearch_by_congress_and_type_omits_sort_and_resolves_format() -> None:
    with patch(
        "congressgov._client.api.bill.bill_list_by_type_sync",
        return_value=MagicMock(
            status_code=200,
            content=b'{"bills": [], "pagination": {"count": 0}}',
        ),
    ) as list_by_type:
        billsearch(
            None,
            client=MagicMock(),
            congress=119,
            bill_type="hr",
            format_=None,
        )

    _, kwargs = list_by_type.call_args
    assert "sort" not in kwargs
    assert kwargs["format_"] == GetBillCongressBillTypeFormat.JSON


def test_billsearch_rejects_explicit_sort() -> None:
    with pytest.raises(ValueError, match="sort is not supported"):
        billsearch(None, client=MagicMock(), congress=119, bill_type="hr", sort="updateDate")
