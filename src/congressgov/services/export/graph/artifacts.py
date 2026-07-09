"""Write graph exports through the workspace artifact lane."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .interactive import export_interactive_html
from .models import GraphRenderConfig, GraphSlice
from .render import export_graph_slice_json, graph_slice_to_api_payload

if TYPE_CHECKING:
    from congressgov.services.core.workspace import Workspace


def export_graph_slice_to_workspace(
    graph_slice: GraphSlice,
    workspace: "Workspace",
    *,
    prefix: str = "network_graph",
    title: str | None = None,
    render_config: GraphRenderConfig | None = None,
    json_format: str = "api",
) -> dict[str, str]:
    """
    Export HTML explorer and JSON payloads into ``workspace`` exports lane.

    Returns a mapping of artifact kind to resolved filesystem path.
    """
    config = render_config or GraphRenderConfig(title=title or "Congress network graph")
    metadata_base: dict[str, Any] = {
        "graph_key": graph_slice.graph_key,
        "node_count": len(graph_slice.nodes),
        "edge_count": len(graph_slice.edges),
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        html_tmp = tmp / "explorer.html"
        json_tmp = tmp / "graph.json"
        export_interactive_html(graph_slice, html_tmp, render_config=config)
        if json_format == "sigma":
            export_graph_slice_json(graph_slice, json_tmp, format="sigma")
        else:
            json_tmp.write_text(
                json.dumps(graph_slice_to_api_payload(graph_slice), indent=2),
                encoding="utf-8",
            )
        html_path = workspace.write_export(
            f"{prefix}/explorer.html",
            html_tmp.read_text(encoding="utf-8"),
            metadata={**metadata_base, "kind": "interactive_html"},
        )
        json_path = workspace.write_export(
            f"{prefix}/graph.json",
            json_tmp.read_text(encoding="utf-8"),
            metadata={**metadata_base, "kind": "graph_json", "format": json_format},
        )

    return {"html": html_path, "json": json_path}
