"""Post-regen congress envelope parser patches."""

from pathlib import Path

from codegen.scripts.patch_client_parse_response import (
    BROKEN_200_BLOCK,
    _fixed_200_block,
    patch_all_envelope_parsers,
    patch_congress_envelope_parsers,
)

BROKEN_HEARING_ONELINE = """    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_hearings_item_data in _response_200:
            componentsschemas_hearings_item = Hearing.from_dict(componentsschemas_hearings_item_data)

            response_200.append(componentsschemas_hearings_item)

        return response_200"""

REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT_ROOT = REPO_ROOT / "src" / "congressgov" / "_client"


def test_congress_modules_use_envelope_safe_parse_response() -> None:
    patched = patch_congress_envelope_parsers(CLIENT_ROOT)
    assert len(patched) == 0, "committed client should already be patched"

    for rel in (
        "api/congress/get_congress.py",
        "api/congress/get_congress_congress.py",
        "api/congress/get_congress_current.py",
    ):
        text = (CLIENT_ROOT / rel).read_text(encoding="utf-8")
        assert "return None" in text
        assert "congressgov.services" in text
        assert BROKEN_200_BLOCK not in text, f"{rel} still has list-iteration parser"


def test_patch_replaces_broken_block() -> None:
    text = f"before\n{BROKEN_200_BLOCK}\nafter"
    patched = text.replace(BROKEN_200_BLOCK, _fixed_200_block("congress"), 1)
    assert "return None" in patched
    assert BROKEN_200_BLOCK not in patched


def test_hearing_and_summaries_modules_use_envelope_safe_parse_response() -> None:
    assert patch_all_envelope_parsers(CLIENT_ROOT) == []

    for rel in (
        "api/hearing/get_hearing.py",
        "api/summaries/get_summaries.py",
        "api/treaty/get_treaty.py",
        "api/house_vote/get_house_vote.py",
    ):
        text = (CLIENT_ROOT / rel).read_text(encoding="utf-8")
        assert "return None" in text
        assert "Generated list iteration fails" in text or "Generated eager from_dict fails" in text


def test_patch_replaces_single_line_list_iteration() -> None:
    from codegen.scripts.patch_client_parse_response import patch_list_iteration_envelope_parsers

    text = f"def _parse_response():\n{BROKEN_HEARING_ONELINE}\n"
    module = CLIENT_ROOT / "api" / "hearing" / "get_patch_test_hearing.py"
    module.write_text(text, encoding="utf-8")
    try:
        patched = patch_list_iteration_envelope_parsers(CLIENT_ROOT)
        assert module in patched
        assert "return None" in module.read_text(encoding="utf-8")
    finally:
        if module.exists():
            module.unlink()
