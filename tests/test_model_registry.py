"""Model registry: codegen MODEL_PATH_MAP wired into hand-maintained registry."""

from congressgov.services.core.model_registry import HAND_MODEL_OVERRIDES, ModelRegistry
from congressgov.services.core.model_registry_generated import MODEL_PATH_MAP


def test_codegen_entity_paths_resolve() -> None:
    assert ModelRegistry.get_model("CommitteeMeeting").__name__ == "CommitteeMeeting"
    assert ModelRegistry.get_model("Congress").__name__ == "Congress"


def test_hand_overrides_take_precedence() -> None:
    assert HAND_MODEL_OVERRIDES["CommitteeReports"] == "congressgov.models.documents.reports"
    assert ModelRegistry.get_model("Sponsor").__name__ == "Sponsor"
    assert ModelRegistry.get_model("RecordedVote").__name__ == "RecordedVote"


def test_congressional_record_alias_resolves() -> None:
    cls = ModelRegistry.get_model("CongressionalRecord")
    assert cls.__name__ in ("CongressionalRecord", "DailyCongressionalRecord")


def test_model_path_map_includes_codegen_entities() -> None:
    assert "HouseRequirement" in MODEL_PATH_MAP
    assert "BoundCongressionalRecord" in MODEL_PATH_MAP
