"""Bill adoption: hand service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "bill.py"

EXPECTED_BILL_MAPPING_KEYS = {
    "actions",
    "amendments",
    "committees",
    "cosponsors",
    "relatedBills",
    "subjects",
    "summaries",
    "textVersions",
    "titles",
}


def test_hand_bill_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Bill" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "# CUSTOM: law list endpoints" in src
    assert "validate_bill_type" in src
    assert "BILL_MAPPINGS" in src
    assert "search_by_laws" in src
    assert "bill_details_sync" in src



def test_bill_search_delegates_to_universal_search() -> None:
    from congressgov.services.bill import Bill

    bills = MagicMock()
    with patch("congressgov.services.core.search.search", return_value=bills) as mock_search:
        service = Bill()
        result = service.search(congress=118, bill_type="hr")

    assert result is bills
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    assert args[0] == "bill"
    assert args[1] is service
    assert kwargs["congress"] == 118
    assert kwargs["bill_type"] == "hr"


def test_bill_get_validates_bill_type() -> None:
    from congressgov.services.exceptions import ValidationError
    from congressgov.services.bill import Bill

    service = Bill(client=MagicMock())
    with pytest.raises(ValidationError):
        service.get(congress=118, bill_type="invalid", bill_number=1)


def test_hand_bill_mappings_keys() -> None:
    from congressgov.services.bill import BILL_MAPPINGS

    assert set(BILL_MAPPINGS) == EXPECTED_BILL_MAPPING_KEYS
