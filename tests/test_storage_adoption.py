"""Tests for storage adoption: skip-if-loaded, migration, provenance, exports."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch


from congressgov.models.entities.bill import Bill
from congressgov.services.core.model_registry import ModelRegistry
from congressgov.services.core.workspace import Workspace, migrate_legacy_blob_if_needed
from congressgov.services.export.graph.store import CongressGraphStore


ActionsModel = ModelRegistry.get_model("Actions")


def test_migrate_legacy_blob_if_needed(tmp_path: Path) -> None:
    workspace = Workspace.open(tmp_path / "ws", ensure_dirs=False)
    paths = workspace.paths
    paths.root.mkdir(parents=True)
    legacy = paths.legacy_api_db()
    legacy.write_bytes(b"legacy-sqlite")
    assert migrate_legacy_blob_if_needed(paths) is True
    assert paths.api_db.exists()
    assert paths.api_db.read_bytes() == b"legacy-sqlite"


def test_migrate_legacy_blob_skips_when_api_exists(tmp_path: Path) -> None:
    workspace = Workspace.open(tmp_path / "ws")
    paths = workspace.paths
    paths.legacy_api_db().write_bytes(b"legacy")
    paths.api_db.write_bytes(b"canonical")
    assert migrate_legacy_blob_if_needed(paths) is False
    assert paths.api_db.read_bytes() == b"canonical"


def test_bill_get_actions_skips_when_loaded() -> None:
    bill = Bill(congress=118, type="HR", number=1)
    bill.actions = ActionsModel(actions=[])
    client = MagicMock()

    with patch("congressgov.services.extensions.bill.bill_actions_sync") as mock_api:
        result = bill.get_actions(client=client)

    mock_api.assert_not_called()
    assert result is bill.actions


def test_bill_get_actions_refetches_when_refresh() -> None:
    bill = Bill(congress=118, type="HR", number=1)
    bill.actions = ActionsModel(actions=[])
    client = MagicMock()
    response = MagicMock()
    response.content = json.dumps({"data": {"actions": []}})
    client_mock = MagicMock(return_value=response)

    with patch("congressgov.services.extensions.bill.bill_actions_sync", client_mock):
        bill.get_actions(client=client, refresh=True)

    client_mock.assert_called_once()


def test_api_service_expand_skips_loaded_attribute() -> None:
    from congressgov.services.bill import BILL_MAPPINGS, BILL_PARAMETERS
    from congressgov.services.core.api_service import ApiService

    bill = Bill(congress=118, type="HR", number=1)
    bill.actions = ActionsModel(actions=[])
    client = MagicMock()

    with patch("congressgov.services.core.api_service.json.loads") as mock_loads:
        ApiService().expand(
            target=bill,
            client=client,
            mapping={"actions": BILL_MAPPINGS["actions"]},
            parameters=BILL_PARAMETERS,
            attributes=["actions"],
            normalize_params=["bill_type"],
        )

    mock_loads.assert_not_called()


def test_graph_store_save_populates_provenance(tmp_path: Path) -> None:
    path = tmp_path / "118.json"
    store = CongressGraphStore.open(path, congress=118)
    store.save()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["provenance"]["bill_count"] == 0
    assert payload["provenance"]["schema"] == "congress_graph/v1"
    assert "built_at" in payload["provenance"]


def test_graph_store_add_bills_skips_before_cosponsor_fetch(tmp_path: Path) -> None:
    from congressgov.models.entities.sponsor import Cosponsor, Sponsor

    path = tmp_path / "118.json"
    store = CongressGraphStore.open(path, congress=118)
    bill = Bill(congress=118, type="HR", number=1)
    # Give the bill an actual sponsor + cosponsor so add_bill records at
    # least one event and genuinely marks it ingested (a bill with zero
    # events must NOT be marked ingested -- see add_bill's docstring/NOTE --
    # so that it can be revisited once cosponsor data becomes available).
    bill.sponsors = [
        Sponsor(bioguideId="S000001", fullName="Sponsor One", url="https://api.congress.gov/v3/member/S000001")
    ]
    cosponsors = [
        Cosponsor(bioguideId="C000001", fullName="Cosponsor One", url="https://api.congress.gov/v3/member/C000001")
    ]
    store.add_bill(bill, cosponsors, save=True)

    bill2 = Bill(congress=118, type="HR", number=1)
    bill2.get_cosponsors = MagicMock(side_effect=AssertionError("should not fetch"))  # type: ignore[method-assign]

    results = store.add_bills([bill2], fetch_cosponsors=True)
    assert results[0].skipped_reason == "already_ingested"
    bill2.get_cosponsors.assert_not_called()


def test_count_ref_fetch_skips_when_parent_loaded() -> None:
    from congressgov.models.base.types import CountRef
    from congressgov.services.core.expansion_helpers import PARENT_ENTITY_ATTR, PARENT_FIELD_ATTR
    from congressgov.services.extensions.url_follow import _fetch_url_field

    bill = Bill(congress=118, type="HR", number=1)
    bill.actions = ActionsModel(actions=[])
    stub = CountRef(count=1, url="https://api.congress.gov/v3/bill/118/hr/1/actions")
    setattr(stub, PARENT_ENTITY_ATTR, bill)
    setattr(stub, PARENT_FIELD_ATTR, "actions")

    with patch("congressgov.services.extensions.url_follow.fetch_from_url") as mock_fetch:
        result = _fetch_url_field(stub, client=MagicMock())

    mock_fetch.assert_not_called()
    assert result is bill.actions


def test_export_graph_slice_to_workspace(tmp_path: Path) -> None:
    from congressgov.services.export.graph import (
        GraphSlice,
        export_graph_slice_to_workspace,
    )
    from congressgov.services.export.graph.models import GraphLimits, GraphProjectionType

    workspace = Workspace.open(tmp_path / "ws")
    graph = GraphSlice(
        graph_key="test",
        layout_key="test",
        projection=GraphProjectionType.SPONSOR_TO_COSPONSOR,
        nodes=[],
        edges=[],
        limits=GraphLimits(
            max_edges=0,
            edge_count_before_limit=0,
            was_truncated=False,
            shown_edges=0,
        ),
    )
    paths = export_graph_slice_to_workspace(graph, workspace, prefix="demo")
    assert Path(paths["html"]).exists()
    assert Path(paths["json"]).exists()
    assert (workspace.paths.exports_dir / "demo").exists()


def test_workspace_write_export(tmp_path: Path) -> None:
    workspace = Workspace.open(tmp_path / "ws")
    out = workspace.write_export("graphs/test.json", '{"ok": true}')
    assert Path(out).exists()
    assert "exports" in registry_names(workspace)


def registry_names(workspace: Workspace) -> list[str]:
    return workspace.registry().names()
