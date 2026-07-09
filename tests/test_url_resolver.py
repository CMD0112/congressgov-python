"""Tests for API URL parsing, routing, and fetch_from_url."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from congressgov.models.base.references import BillRef
from congressgov.models.base.types import CountRef, URL
from congressgov.models.entities.bill import Bill
from congressgov.models.entities.sponsor import Cosponsors
from congressgov.models.entities.member import SponsoredLegislationItem
from congressgov.services.core.url_resolver import (
    fetch_from_url,
    match_url,
    parse_api_url,
)
from congressgov.services.exceptions import UnsupportedApiUrlError


def test_parse_api_url_full() -> None:
    parsed = parse_api_url("https://api.congress.gov/v3/bill/119/hr/1?format=json")
    assert parsed.path == "/bill/119/hr/1"
    assert parsed.query["format"] == ["json"]


def test_parse_api_url_path_only() -> None:
    parsed = parse_api_url("/v3/member/A000374")
    assert parsed.path == "/member/A000374"


def test_parse_api_url_rejects_external_host() -> None:
    with pytest.raises(ValueError, match="Unsupported URL host"):
        parse_api_url("https://www.congress.gov/bill/119/hr/1")


def test_match_url_prefers_subresource_over_detail() -> None:
    detail = match_url("https://api.congress.gov/v3/bill/119/hr/1")
    actions = match_url("https://api.congress.gov/v3/bill/119/hr/1/actions")
    assert detail.route["sync"] == "bill_details_sync"
    assert actions.route["sync"] == "bill_actions_sync"
    assert actions.route["model"] == "Actions"


def test_match_url_extracts_params() -> None:
    match = match_url("/v3/bill/119/hr/5054")
    assert match.params["congress"] == 119
    assert match.params["bill_type"] == "hr"
    assert match.params["bill_number"] == 5054


def test_match_url_unsupported() -> None:
    with pytest.raises(UnsupportedApiUrlError):
        match_url("https://api.congress.gov/v3/not-a-real/endpoint")


def test_fetch_from_url_bill_detail() -> None:
    payload = {
        "bill": {
            "congress": 119,
            "type": "HR",
            "number": 5054,
            "title": "Example",
        }
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    client = MagicMock()
    parent = MagicMock()
    parent.client = client

    with patch(
        "congressgov._client.api.bill.bill_details_sync",
        return_value=response,
    ):
        result = fetch_from_url(
            "https://api.congress.gov/v3/bill/119/hr/5054",
            client=client,
        )

    assert isinstance(result, Bill)
    assert result.congress == 119
    assert result.client is client


def test_bill_ref_fetch_uses_url() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {"bill": {"congress": 118, "type": "HR", "number": 1}}
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    ref = BillRef.model_validate(
        {
            "url": "https://api.congress.gov/v3/bill/118/hr/1",
            "congress": 118,
            "type": "HR",
            "number": 1,
        }
    )
    ref.client = MagicMock()

    with patch(
        "congressgov._client.api.bill.bill_details_sync",
        return_value=response,
    ):
        bill = ref.fetch()

    assert isinstance(bill, Bill)
    assert bill.number == 1


def test_count_ref_fetch() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {"actions": [{"actionDate": "2024-01-01", "text": "Introduced"}]}
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    stub = CountRef(count=1, url="https://api.congress.gov/v3/bill/119/hr/1/actions")
    stub.client = MagicMock()

    with patch(
        "congressgov._client.api.bill.bill_actions_sync",
        return_value=response,
    ):
        actions = stub.fetch()

    assert actions is not None


def test_bill_cosponsors_count_ref_fetch_binds_parent() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {
        "cosponsors": [
            {
                "bioguideId": "A000374",
                "fullName": "Example Member",
                "sponsorshipDate": "2024-01-01",
                "url": "https://api.congress.gov/v3/member/A000374",
            }
        ],
        "pagination": {"count": 1},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    bill = Bill.model_validate(
        {
            "congress": 119,
            "type": "HR",
            "number": 1,
            "cosponsors": {
                "count": 1,
                "url": "https://api.congress.gov/v3/bill/119/hr/1/cosponsors",
            },
        }
    )
    bill.client = MagicMock()
    assert isinstance(bill.cosponsors, CountRef)

    with patch(
        "congressgov._client.api.bill.bill_cosponsors_sync",
        return_value=response,
    ):
        result = bill.cosponsors.fetch(client=bill.client)

    assert isinstance(result, Cosponsors)
    assert bill.cosponsors is result
    assert "cosponsors=" in repr(result)
    assert not repr(result).startswith("<Cosponsors:")


def test_url_model_fetch() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {"member": {"bioguideId": "A000374"}}
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    url = URL.model_validate("https://api.congress.gov/v3/member/A000374")
    url.client = MagicMock()

    with patch(
        "congressgov._client.api.member.member_details_sync",
        return_value=response,
    ):
        from congressgov.models.entities.member import Member

        member = url.fetch()

    assert isinstance(member, Member)
    assert member.bioguideId == "A000374"


def test_sponsored_item_fetch_legislation_amendment_path() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {
        "amendment": {
            "congress": 119,
            "type": "HAMDT",
            "number": "563",
        }
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    item = SponsoredLegislationItem.model_validate(
        {
            "url": "https://api.congress.gov/v3/amendment/119/hamdt/563",
            "congress": 119,
            "type": "HAMDT",
            "amendmentNumber": "563",
        }
    )
    item.client = MagicMock()

    with patch(
        "congressgov._client.api.amendments.amendment_details_sync",
        return_value=response,
    ):
        from congressgov.models.entities.amendment import Amendment

        result = item.fetch()

    assert isinstance(result, Amendment)


def test_fetch_from_url_force_fetch_uses_fetch_options() -> None:
    payload = {"bill": {"congress": 119, "type": "HR", "number": 5054, "title": "Example"}}
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    client = MagicMock()

    with (
        patch(
            "congressgov._client.api.bill.bill_details_sync",
            return_value=response,
        ) as mock_api,
        patch(
            "congressgov.services.core.request_store.fetch_options",
        ) as mock_fetch_options,
    ):
        mock_fetch_options.return_value.__enter__ = MagicMock(return_value=None)
        mock_fetch_options.return_value.__exit__ = MagicMock(return_value=False)
        result = fetch_from_url(
            "https://api.congress.gov/v3/bill/119/hr/5054",
            client=client,
            force_fetch=True,
        )

    assert isinstance(result, Bill)
    mock_fetch_options.assert_called_once_with(force_fetch=True)
    mock_api.assert_called_once()
    assert "force_fetch" not in mock_api.call_args.kwargs
