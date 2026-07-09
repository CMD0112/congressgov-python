"""Actions entity: extension-driven only (no hand middleware/actions.py)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND_ACTIONS = REPO_ROOT / "src" / "congressgov" / "services" / "actions.py"
EXTENSIONS = REPO_ROOT / "src" / "congressgov" / "services" / "extensions" / "actions.py"


def test_no_hand_middleware_actions_module() -> None:
    assert not HAND_ACTIONS.is_file(), "Actions should remain extension-driven, not a hand service"


def test_actions_extension_module_exists() -> None:
    assert EXTENSIONS.is_file()


def test_no_actions_generated_sidecar() -> None:
    sidecar = REPO_ROOT / "src" / "congressgov" / "services" / "actions.generated.py"
    assert not sidecar.is_file()
