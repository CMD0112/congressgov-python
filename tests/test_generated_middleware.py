"""Smoke tests for hand-maintained middleware services (protected from codegen overwrite)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND_SERVICES = (
    "committee.py",
    "amendment.py",
    "member.py",
    "bill.py",
)


def test_hand_maintained_services_exist() -> None:
    for name in HAND_SERVICES:
        assert (REPO_ROOT / "src" / "congressgov" / "services" / name).is_file()


def test_hand_maintained_services_importable() -> None:
    from congressgov.services.amendment import Amendment
    from congressgov.services.bill import Bill
    from congressgov.services.committee import Committee
    from congressgov.services.member import Member

    assert Bill.__name__ == "Bill"
    assert Member.__name__ == "Member"
    assert Committee.__name__ == "Committee"
    assert Amendment.__name__ == "Amendment"


def test_member_custom_api_surface() -> None:
    member_src = (REPO_ROOT / "src" / "congressgov" / "services" / "member.py").read_text(encoding="utf-8")
    assert "def get_current_roster" in member_src
    assert "def search" in member_src


def test_model_registry_generated_exists() -> None:
    path = REPO_ROOT / "src" / "congressgov" / "services" / "core" / "model_registry_generated.py"
    assert path.is_file(), "Run poetry run generate-registry"


def test_no_review_sidecar_files_committed() -> None:
    sidecars = list((REPO_ROOT / "src" / "congressgov" / "services").rglob("*.generated.py"))
    assert not sidecars, f"Remove review sidecars: {sidecars[:5]}"
