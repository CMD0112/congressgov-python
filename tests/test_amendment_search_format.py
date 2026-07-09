"""Amendment search must resolve format_=None for the generated client."""

from unittest.mock import MagicMock, patch

import pytest

from congressgov._client.models.get_amendment_congress_amendment_type_format import (
    GetAmendmentCongressAmendmentTypeFormat,
)
from congressgov._client.models.get_amendment_format import GetAmendmentFormat
from congressgov.services.core.search import amendmentsearch


def test_amendmentsearch_list_resolves_format() -> None:
    with patch(
        "congressgov._client.api.amendments.amendment_sync",
        return_value=MagicMock(content=b'{"data": {"amendments": []}}'),
    ) as list_all:
        amendmentsearch(None, client=MagicMock(), format_=None)

    _, kwargs = list_all.call_args
    assert kwargs["format_"] == GetAmendmentFormat.JSON


def test_amendmentsearch_by_congress_and_type_resolves_format() -> None:
    with patch(
        "congressgov._client.api.amendments.amendment_list_sync",
        return_value=MagicMock(content=b'{"data": {"amendments": []}}'),
    ) as list_by_type:
        amendmentsearch(
            None,
            client=MagicMock(),
            congress=118,
            amendment_type="hamdt",
            format_=None,
        )

    _, kwargs = list_by_type.call_args
    assert kwargs["format_"] == GetAmendmentCongressAmendmentTypeFormat.JSON
    assert kwargs["amendment_type"] == "hamdt"


def test_amendmentsearch_type_without_congress_raises() -> None:
    with pytest.raises(ValueError, match="amendment_type requires congress"):
        amendmentsearch(None, client=MagicMock(), amendment_type="hamdt")
