"""Member sponsored/cosponsored legislation extension parsing."""

import json
from unittest.mock import MagicMock, patch

import pytest

from congressgov.models.base.model import ApiEnvelope
from congressgov.models.base.types import CountRef
from congressgov.models.entities.member import (
    CosponsoredLegislation,
    Member,
    Members,
    SponsoredLegislation,
    SponsoredLegislationItem,
)
from congressgov.services.core.model_registry import ModelRegistry


def test_registry_resolves_sponsorship_models() -> None:
    assert ModelRegistry.get_model("SponsoredLegislation") is SponsoredLegislation
    assert ModelRegistry.get_model("CosponsoredLegislation") is CosponsoredLegislation


def test_sponsored_legislation_parses_api_envelope() -> None:
    # Import extensions so @register_method runs
    import congressgov.services.extensions.members  # noqa: F401

    payload = {
        "sponsoredLegislation": [
            {
                "congress": 119,
                "type": "HR",
                "number": "5054",
                "latestTitle": "Example Act",
                "url": "https://api.congress.gov/v3/bill/119/hr/5054",
            },
            {
                "congress": 119,
                "amendmentNumber": "563",
                "type": "HAMDT",
                "latestTitle": "Example amendment",
                "url": "https://api.congress.gov/v3/amendment/119/hamdt/563",
            },
        ],
        "pagination": {"count": 2},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()

    member = Member.model_validate({"bioguideId": "A000374"})
    with patch(
        "congressgov.services.extensions.members.member_sponsorship_list_sync",
        return_value=response,
    ):
        result = member.get_sponsored_legislation(client=MagicMock())

    assert isinstance(result, SponsoredLegislation)
    assert member.sponsoredLegislation is result
    assert result.client is not None
    assert result.sponsoredLegislation is not None
    assert len(result.sponsoredLegislation) == 2
    assert result.sponsoredLegislation[1].amendmentNumber == "563"


def test_cosponsored_legislation_parses_api_envelope() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    payload = {
        "cosponsoredLegislation": [
            {
                "congress": 118,
                "type": "S",
                "number": "1",
                "latestTitle": "Cosponsored bill",
            }
        ],
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()

    member = Member.model_validate({"bioguideId": "B001234"})
    with patch(
        "congressgov.services.extensions.members.member_cosponsorship_list_sync",
        return_value=response,
    ):
        result = member.get_cosponsored_legislation(client=MagicMock())

    assert isinstance(result, CosponsoredLegislation)
    assert member.cosponsoredLegislation is result
    assert result.cosponsoredLegislation is not None
    assert len(result.cosponsoredLegislation) == 1


def test_get_cosponsored_legislation_limit_max() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    from congressgov.services.config import MAX_PAGINATION_LIMIT

    payload = {"cosponsoredLegislation": []}
    response = MagicMock()
    response.content = json.dumps(payload).encode()

    member = Member.model_validate({"bioguideId": "A000374"})
    with patch(
        "congressgov.services.extensions.members.member_cosponsorship_list_sync",
        return_value=response,
    ) as api_mock:
        member.get_cosponsored_legislation(client=MagicMock(), limit="max")

    assert api_mock.call_args.kwargs["limit"] == MAX_PAGINATION_LIMIT


def test_sponsored_legislation_inherits_client_from_members_collection() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    payload = {
        "sponsoredLegislation": [
            {"congress": 119, "type": "HR", "number": "1", "latestTitle": "Act"},
        ],
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    client = MagicMock()

    members = Members.model_validate(
        {"members": [{"bioguideId": "A000374"}]},
    )
    members.client = client
    from congressgov.services.core.expansion_helpers import propagate_client_to_items

    propagate_client_to_items(members, "members", client)
    member = members.members[0]

    with patch(
        "congressgov.services.extensions.members.member_sponsorship_list_sync",
        return_value=response,
    ) as mock_api:
        result = member.get_sponsored_legislation()

    mock_api.assert_called_once()
    assert mock_api.call_args.kwargs["client"] is client
    assert member.sponsoredLegislation is result


def test_sponsored_legislation_skips_refetch_when_loaded() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    existing = SponsoredLegislation.model_validate(
        {"sponsoredLegislation": [{"congress": 119, "type": "HR", "number": "9"}]},
    )
    member = Member.model_validate({"bioguideId": "A000374"})
    member.sponsoredLegislation = existing
    member.client = MagicMock()

    with patch(
        "congressgov.services.extensions.members.member_sponsorship_list_sync",
    ) as mock_api:
        result = member.get_sponsored_legislation()

    mock_api.assert_not_called()
    assert result is existing


def test_sponsored_legislation_refetches_count_stub() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    member = Member.model_validate(
        {
            "bioguideId": "A000374",
            "sponsoredLegislation": CountRef(count=10, url="https://example.com"),
        },
    )
    member.client = MagicMock()
    payload = {"sponsoredLegislation": [{"congress": 119, "type": "HR", "number": "1"}]}
    response = MagicMock()
    response.content = json.dumps(payload).encode()

    with patch(
        "congressgov.services.extensions.members.member_sponsorship_list_sync",
        return_value=response,
    ) as mock_api:
        result = member.get_sponsored_legislation()

    mock_api.assert_called_once()
    assert isinstance(member.sponsoredLegislation, SponsoredLegislation)
    assert member.sponsoredLegislation is result


def test_member_mappings_defined() -> None:
    from congressgov.services.member import MEMBER_MAPPINGS, MEMBER_PARAMETERS

    assert set(MEMBER_MAPPINGS) == {"sponsoredLegislation", "cosponsoredLegislation"}
    assert MEMBER_PARAMETERS["bioguide_id"] == ["bioguideId", "bioguide_id"]


def test_get_available_attributes() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    member = Member.model_validate({"bioguideId": "A000374"})
    assert set(member.get_available_attributes()) == {
        "sponsoredLegislation",
        "cosponsoredLegislation",
    }


def test_expand_sponsored_legislation() -> None:
    import congressgov.services.extensions.members  # noqa: F401
    from congressgov.services.member import MEMBER_MAPPINGS, SponsoredLegislationModel

    payload = {
        "sponsoredLegislation": [
            {"congress": 119, "type": "HR", "number": "1", "latestTitle": "Act"},
        ],
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    fake_api = MagicMock(return_value=response)

    member = Member.model_validate({"bioguideId": "A000374"})
    with patch.dict(
        MEMBER_MAPPINGS,
        {"sponsoredLegislation": {fake_api: SponsoredLegislationModel}},
    ):
        expanded = member.expand(
            client=MagicMock(),
            attributes=["sponsoredLegislation"],
        )
    fake_api.assert_called_once()
    assert fake_api.call_args.kwargs["bioguide_id"] == "A000374"

    assert expanded is not member
    assert isinstance(expanded.sponsoredLegislation, SponsoredLegislation)
    assert expanded.sponsoredLegislation.sponsoredLegislation
    assert expanded.sponsoredLegislation.sponsoredLegislation[0].number == "1"


def test_expand_requires_bioguide_id() -> None:
    import congressgov.services.extensions.members  # noqa: F401

    member = Member.model_validate({})
    with pytest.raises(ValueError, match="bioguide"):
        member.expand(client=MagicMock())


def test_sponsored_item_fetch_from_url() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {
        "bill": {"congress": 119, "type": "HR", "number": "5054", "title": "Act"},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    from congressgov.models.entities.bill import Bill  # noqa: F811

    item = SponsoredLegislationItem.model_validate(
        {
            "url": "https://api.congress.gov/v3/bill/119/hr/5054",
            "congress": 119,
            "type": "HR",
            "number": "5054",
        }
    )
    item.client = MagicMock()
    with patch(
        "congressgov._client.api.bill.bill_details_sync",
        return_value=response,
    ):
        result = item.fetch()

    assert isinstance(result, Bill)
    assert result.number == 5054


def test_sponsored_item_fetch_from_ids() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    payload = {
        "bill": {"congress": 119, "type": "HR", "number": "5054", "title": "Act"},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    from congressgov.models.entities.bill import Bill  # noqa: F811

    item = SponsoredLegislationItem.model_validate(
        {
            "congress": 119,
            "type": "HR",
            "number": "5054",
        }
    )
    item.client = MagicMock()
    with patch(
        "congressgov.services.bill.bill_details_sync",
        return_value=response,
    ):
        result = item.fetch()

    assert isinstance(result, Bill)
    assert result.number == 5054


def test_cosponsored_item_fetch_from_url() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    from congressgov.models.entities.member import CosponsoredLegislationItem

    payload = {
        "bill": {"congress": 118, "type": "S", "number": "1", "title": "Cosponsored"},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    from congressgov.models.entities.bill import Bill  # noqa: F811

    item = CosponsoredLegislationItem.model_validate(
        {
            "url": "https://api.congress.gov/v3/bill/118/s/1",
            "congress": 118,
            "type": "S",
            "number": "1",
        }
    )
    item.client = MagicMock()
    with patch(
        "congressgov._client.api.bill.bill_details_sync",
        return_value=response,
    ):
        result = item.fetch()

    assert isinstance(result, Bill)
    assert result.number == 1


def test_fetch_legislation_deprecated() -> None:
    import congressgov.services.extensions.url_follow  # noqa: F401

    item = SponsoredLegislationItem.model_validate(
        {
            "url": "https://api.congress.gov/v3/bill/119/hr/5054",
            "congress": 119,
            "type": "HR",
            "number": "5054",
        }
    )
    item.client = MagicMock()
    payload = {
        "bill": {"congress": 119, "type": "HR", "number": "5054", "title": "Act"},
    }
    response = MagicMock()
    response.content = json.dumps(payload).encode()
    from congressgov.models.entities.bill import Bill  # noqa: F811

    with patch(
        "congressgov._client.api.bill.bill_details_sync",
        return_value=response,
    ):
        with pytest.warns(DeprecationWarning, match="fetch_legislation"):
            result = item.fetch_legislation()

    assert isinstance(result, Bill)


def test_sponsored_legislation_via_api_envelope_data() -> None:
    """Regression: Bills.model_validate fails on sponsoredLegislation list payloads."""
    envelope = ApiEnvelope.model_validate(
        {
            "sponsoredLegislation": [{"congress": 119, "type": "HR", "number": "1"}],
        }
    )
    result = SponsoredLegislation.model_validate(envelope.data)
    assert result.sponsoredLegislation and result.sponsoredLegislation[0].number == "1"
