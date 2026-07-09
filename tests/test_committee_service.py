"""Committee middleware pilot: hand service."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "committee.py"


def test_hand_committee_has_validation_and_mappings() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class Committee" in src
    assert "# CUSTOM: validation" in src
    assert "# CUSTOM: universal search delegation" in src
    assert "validate_chamber" in src
    assert "validate_committee_code" in src
    assert "COMMITTEE_MAPPINGS" in src
    assert "committee_details_sync" in src
    assert '"bills"' in src or "'bills'" in src



def test_hand_committee_import_and_mappings_keys() -> None:
    from congressgov.services.committee import COMMITTEE_MAPPINGS, Committee

    assert Committee.__name__ == "Committee"
    assert set(COMMITTEE_MAPPINGS) == {
        "bills",
        "reports",
        "houseCommunications",
        "senateCommunications",
        "nominations",
    }
