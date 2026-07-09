"""Debug network graph node labels."""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from congressgov import Bill, Member, get_client_from_env
from congressgov.services.export.graph import (
    GraphExploreConfig,
    GraphIngestionConfig,
    GraphRenderConfig,
    build_graph_slice,
    create_member_label_resolver,
    ingest_bill_events,
    prepare_sigma_render_payload,
)
from congressgov.services.export.graph.render import graph_slice_to_sigma_payload

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

client = get_client_from_env(load_dotenv=False)
bill_service = Bill(client=client)
member_service = Member(client=client)
events = ingest_bill_events(
    bill_service,
    GraphIngestionConfig(congress=118, bill_type="hr", batch_size=5),
    fetch_cosponsors=True,
)
resolver = create_member_label_resolver(member_service, congress=118, client=client)
graph = build_graph_slice(
    events,
    GraphExploreConfig(congress=118, max_edges=500),
    member_resolver=resolver,
)

lines = ["=== graph slice labels (first 12) ==="]
for node in graph.nodes[:12]:
    lines.append(f"{node.id} | {node.label}")

raw = graph_slice_to_sigma_payload(graph)
lines.append("\n=== raw sigma label (first node) ===")
lines.append(str(raw["nodes"][0]["attributes"].get("label")))

payload = prepare_sigma_render_payload(graph, GraphRenderConfig())
first_attrs = payload["graph"]["nodes"][0]["attributes"]
lines.append(f"\nhas_fullLabel_key={'fullLabel' in first_attrs}")
lines.append(f"fullLabel_value={first_attrs.get('fullLabel')!r}")

empty = sum(1 for n in payload["graph"]["nodes"] if not n["attributes"].get("label"))
lines.append(f"\n=== sigma payload: {empty}/{len(payload['graph']['nodes'])} nodes with empty render label ===")
for node in payload["graph"]["nodes"][:12]:
    attrs = node["attributes"]
    lines.append(
        f"{node['key']} | fullLabel={attrs.get('fullLabel')!r} | render_label={attrs.get('label')!r}"
    )

out = REPO_ROOT / "examples" / "output" / "label_debug.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print(out)
