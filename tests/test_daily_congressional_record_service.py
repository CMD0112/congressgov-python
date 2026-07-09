"""DailyCongressionalRecord middleware: hand service."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HAND = REPO_ROOT / "src" / "congressgov" / "services" / "daily_congressional_record.py"


def test_hand_daily_record_has_custom_hooks() -> None:
    src = HAND.read_text(encoding="utf-8")
    assert "class DailyCongressionalRecord" in src
    assert "# CUSTOM: direct list via ApiEnvelope" in src
    assert "# CUSTOM: volume sub-endpoint" in src
    assert "# CUSTOM: issue sub-endpoint" in src
    assert "# CUSTOM: articles sub-endpoint" in src
    assert "def list(" not in src
    assert "def search(" in src
    assert "def get_volume(" in src
    assert "def get_issue(" in src
    assert "def get_articles(" in src

