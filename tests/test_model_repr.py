"""Tests for Model.__repr__ safety and collection display."""

from __future__ import annotations

from unittest.mock import MagicMock

import congressgov.services.extensions  # noqa: F401
from congressgov.models.base.model import Model
from congressgov.models.entities.member import Members
from congressgov.models.entities.sponsor import Cosponsors
from congressgov.services.core.expansion_helpers import propagate_client_to_items


def test_member_repr_ignores_parent_collection_link() -> None:
    client = MagicMock()
    members = Members.model_validate({"members": [{"bioguideId": "A000374"}]})
    propagate_client_to_items(members, "members", client)

    text = repr(members.members[0])

    assert "_parent_collection" not in text
    assert "client" not in text
    assert "bioguideId='A000374'" in text


def test_members_model_repr_does_not_recursion_error_with_parent_links() -> None:
    client = MagicMock()
    members = Members.model_validate(
        {"members": [{"bioguideId": "A000374"}, {"bioguideId": "B000001"}]}
    )
    propagate_client_to_items(members, "members", client)

    original_repr = Members.__repr__
    try:
        Members.__repr__ = Model.__repr__
        text = repr(members)
    finally:
        Members.__repr__ = original_repr

    assert text.startswith("Members(")
    assert "_parent_collection" not in text


def test_cosponsors_model_repr_still_shows_items_field() -> None:
    cosponsors = Cosponsors.model_validate(
        {
            "cosponsors": [
                {
                    "bioguideId": "A000374",
                    "url": "https://api.congress.gov/v3/member/A000374",
                }
            ]
        }
    )
    text = repr(cosponsors)
    assert "cosponsors=" in text
    assert "A000374" in text
