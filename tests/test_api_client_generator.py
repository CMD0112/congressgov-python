"""API client generator fail-safe (staging) tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from codegen.generators.api_client_generator import ApiClientGenerator


def test_failed_regen_does_not_modify_existing_client(tmp_path: Path) -> None:
    client_dir = tmp_path / "congressgov._client"
    api_pkg = client_dir / "api" / "bill"
    api_pkg.mkdir(parents=True)
    sentinel = api_pkg / "bill_details.py"
    sentinel.write_text("# keep me\n", encoding="utf-8")

    config = {
        "output": {"api_client": str(client_dir)},
        "api_client": {"config_path": "codegen/config/openapi_client_config.yaml"},
        "spec_path": "codegen/config/openapi_spec.yaml",
        "generation": {},
    }
    gen = ApiClientGenerator(config, MagicMock(), file_manager=MagicMock())

    with patch.object(gen, "_run_openapi_client", return_value=(False, "", ["boom"])):
        result = gen.generate()

    assert not result.success
    assert sentinel.read_text(encoding="utf-8") == "# keep me\n"
