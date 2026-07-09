"""Congress.gov client factory and compat export smoke tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from congressgov._client.api.bill import bill_details_sync
from congressgov._client.api.bill.get_bill_congress_bill_type_bill_number import (
    sync_detailed as bill_details_sync_impl,
)
from congressgov import create_api_client, get_client_from_env
from congressgov.services.client_factory import CONGRESS_API_AUTH_HEADER


def test_create_api_client_uses_x_api_key_header() -> None:
    client = create_api_client(api_key="test-key-123")
    assert client.auth_header_name == CONGRESS_API_AUTH_HEADER
    assert client.prefix == ""
    httpx_client = client.get_httpx_client()
    assert httpx_client.headers[CONGRESS_API_AUTH_HEADER] == "test-key-123"


def test_get_client_from_env_reads_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONGRESS_API_KEY", "env-key")
    client = get_client_from_env(load_dotenv=False, request_store=False)
    assert client.get_httpx_client().headers[CONGRESS_API_AUTH_HEADER] == "env-key"


def test_get_client_from_env_attaches_request_store_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("CONGRESS_API_KEY", "env-key")
    store_path = tmp_path / "store.db"
    monkeypatch.setenv("CONGRESS_REQUEST_STORE", f"sqlite:///{store_path}")
    client = get_client_from_env(load_dotenv=False)
    from congressgov import get_attached_store

    assert get_attached_store(client) is not None


def test_create_stored_api_client_attaches_store() -> None:
    from congressgov import create_stored_api_client, get_attached_store

    client = create_stored_api_client(api_key="k", request_store=":memory:")
    assert get_attached_store(client) is not None


def test_create_api_client_store_disabled_by_default() -> None:
    from congressgov import create_api_client, get_attached_store

    client = create_api_client(api_key="k")
    assert get_attached_store(client) is None


def test_bill_details_sync_is_sync_detailed() -> None:
    """Compat exports must be sync_detailed so middleware can read .content."""
    assert bill_details_sync is bill_details_sync_impl


def test_bill_get_without_monkeypatch() -> None:
    from congressgov._client.models.get_bill_congress_bill_type_bill_number_format import (
        GetBillCongressBillTypeBillNumberFormat,
    )
    from congressgov.services.bill import Bill

    envelope = {
        "data": {
            "congress": 118,
            "type": "HR",
            "number": "1",
            "title": "Test Bill",
        }
    }
    mock_response = MagicMock()
    mock_response.content = json.dumps(envelope).encode()

    client = create_api_client(api_key="k")
    with patch(
        "congressgov.services.bill.bill_details_sync",
        return_value=mock_response,
    ) as mock_sync:
        bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)
        mock_sync.assert_called_once()
        _, kwargs = mock_sync.call_args
        assert kwargs["format_"] == GetBillCongressBillTypeBillNumberFormat.JSON

    assert bill.title == "Test Bill"


def test_congress_get_without_monkeypatch() -> None:
    from congressgov._client.models.get_congress_congress_format import (
        GetCongressCongressFormat,
    )
    from congressgov.services.congress import Congress

    envelope = {
        "congress": {
            "name": "117th Congress",
            "number": 117,
            "startYear": "2021",
            "endYear": "2022",
        }
    }
    mock_response = MagicMock()
    mock_response.content = json.dumps(envelope).encode()

    client = create_api_client(api_key="k")
    with patch(
        "congressgov.services.congress.congress_details_sync",
        return_value=mock_response,
    ) as mock_sync:
        congress = Congress(client=client).get(congress=117)
        mock_sync.assert_called_once()
        _, kwargs = mock_sync.call_args
        assert kwargs["format_"] == GetCongressCongressFormat.JSON

    assert congress.name == "117th Congress"
    assert congress.number == 117


def test_congress_details_sync_parses_envelope_without_error() -> None:
    """Generated client must not iterate envelope keys as congress rows."""
    import httpx

    from congressgov._client.api.congress.get_congress_congress import sync_detailed
    from congressgov._client.models.get_congress_congress_format import (
        GetCongressCongressFormat,
    )

    envelope = {
        "congress": {"name": "117th Congress", "number": 117},
        "request": {"contentType": "application/json"},
    }
    mock_client = MagicMock()
    mock_client.raise_on_unexpected_status = False
    mock_httpx = MagicMock()
    mock_httpx.request.return_value = httpx.Response(
        200,
        json=envelope,
        request=httpx.Request("GET", "https://api.congress.gov/v3/congress/117"),
    )
    mock_client.get_httpx_client.return_value = mock_httpx

    response = sync_detailed(
        117,
        client=mock_client,
        format_=GetCongressCongressFormat.JSON,
    )

    assert response.status_code == 200
    assert response.parsed is None
    assert json.loads(response.content) == envelope


def test_member_search_without_core_search_module() -> None:
    from congressgov._client.models.get_member_format import GetMemberFormat
    from congressgov.services.member import Member

    envelope = {"members": [{"bioguideId": "A000374", "firstName": "Test"}]}
    mock_response = MagicMock()
    mock_response.content = json.dumps(envelope).encode()

    client = create_api_client(api_key="k")
    with patch(
        "congressgov.services.member.member_list_sync",
        return_value=mock_response,
    ) as mock_sync:
        members = Member(client=client).search(current_member="true", limit=10)
        mock_sync.assert_called_once()
        _, kwargs = mock_sync.call_args
        assert kwargs["format_"] == GetMemberFormat.JSON
        assert kwargs["current_member"] == "true"

    assert members.members[0].bioguideId == "A000374"
