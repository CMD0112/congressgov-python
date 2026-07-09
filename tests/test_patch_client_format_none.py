"""Generated client must coerce format_=None before accessing .value."""

from pathlib import Path

from congressgov._client.api.committee.get_committee_chamber_committee_code import (
    GetCommitteeChamberCommitteeCodeFormat,
    _get_kwargs,
)
from congressgov._client.models.get_committee_chamber_committee_code_chamber import (
    GetCommitteeChamberCommitteeCodeChamber,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT_API_ROOT = REPO_ROOT / "src" / "congressgov" / "_client" / "api"
GET_COMMITTEE_DETAIL = CLIENT_API_ROOT / "committee" / "get_committee_chamber_committee_code.py"

_UNPATCHED_FORMAT_BLOCK = """    json_format_: Union[Unset, str] = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value"""


def test_get_kwargs_includes_format_none_coercion() -> None:
    assert GET_COMMITTEE_DETAIL.is_file(), "Run patch_client_format_none after generate-client"
    text = GET_COMMITTEE_DETAIL.read_text(encoding="utf-8")
    assert "if format_ is None:" in text
    assert "GetCommitteeChamberCommitteeCodeFormat.JSON" in text


def test_all_get_modules_patched_for_format_none() -> None:
    """CI generate-client runs patch_client_format_none; committed tree must match."""
    unpatched = [
        path.relative_to(REPO_ROOT)
        for path in sorted(CLIENT_API_ROOT.rglob("get_*.py"))
        if _UNPATCHED_FORMAT_BLOCK in path.read_text(encoding="utf-8")
    ]
    assert not unpatched, (
        "Run: poetry run python codegen/scripts/patch_client_format_none.py — "
        f"unpatched: {unpatched[:5]}{'...' if len(unpatched) > 5 else ''}"
    )


def test_get_kwargs_coerces_none_format_to_json_enum() -> None:
    kwargs = _get_kwargs(
        chamber=GetCommitteeChamberCommitteeCodeChamber.HOUSE,
        committee_code="HSGOV",
        format_=None,
    )
    assert kwargs["params"]["format"] == GetCommitteeChamberCommitteeCodeFormat.JSON.value
