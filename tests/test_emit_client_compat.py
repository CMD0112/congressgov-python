"""Tests for legacy client compat helpers."""

from codegen.scripts.emit_client_compat import alias_signature, path_signature


def test_path_signature_round_trip() -> None:
    cases = [
        "/bill/{congress}/{billType}/{billNumber}",
        "/bill/{congress}/{billType}/{billNumber}/actions",
        "/member/{bioguideId}",
        "/member/{bioguideId}/sponsored-legislation",
        "/committee/{chamber}/{committeeCode}",
    ]
    for url in cases:
        assert path_signature(url) == path_signature(path_signature(url))


def test_alias_signature_from_url_path() -> None:
    url = "/bill/{congress}/{billType}/{billNumber}/actions"
    alias = {"url_path": url}
    assert alias_signature(alias) == path_signature(url)


def test_path_signature_preserves_param_names() -> None:
    assert path_signature("/member/{bioguideId}") == "/member/{bioguideId}"
    assert path_signature("/member/{state_code}") == "/member/{state_code}"
    assert (
        path_signature("/committee/{chamber}")
        != path_signature("/committee/{congress}")
    )
