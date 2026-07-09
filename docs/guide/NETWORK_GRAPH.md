# Sponsor/cosponsor network graphs

Build filtered, aggregated sponsor/cosponsor graph projections from `Bill` and `Cosponsor` models. This module implements the **data and projection layer** described in the network graph design plan: store raw events, aggregate member-pair edges, and export slices for Sigma.js/Graphology or downstream FastAPI apps.

**Construction reference:** For a complete catalog of build methods (`ingest_bill_events`, `build_graph_slice`, `CongressGraphStore`, live scripts, synthetic data, and workflow selection), see [GRAPH_CONSTRUCTION.md](GRAPH_CONSTRUCTION.md).

Install the optional graph extra for spring layouts via NetworkX (SciPy recommended for large graphs):

```bash
pip install congressgov[graph]
# or: pip install congressgov[export,graph]
```

Without NetworkX, layouts fall back to a circular placement. Without SciPy, spring layouts fall back to party-shell or circular placement.

## Core workflow

```plain text
Congress members (nodes) + bills over time → sponsorship events → filtered projection → graph slice
```

Two complementary graph kinds:

1. **Network graph** (ephemeral slice) — expand a bill batch into events and build a graph in one pass (members appear only when they have edges). Example: `examples/network_graph_live.py` → `examples/output/network_graph/`.
2. **Congress roster graph** (persistent dataset) — seed the full member roster for a Congress, then add bills incrementally. Events and bill IDs are deduplicated on disk. Example: `examples/congress_roster_graph_live.py` → `examples/output/congress_roster_graph/`.

```plain text
seed members → save → add bills → save → add more bills → build slice (full roster + edges)
```

Recommended exploration sequence:

```plain text
Filter → aggregate → render overview → select member → ego network → edge evidence
```

## Quick start

```python
from congressgov import Bill, AuthenticatedClient
from congressgov.services.export.graph import (
    GraphExploreConfig,
    build_graph_slice,
    export_graph_slice_json,
    graph_slice_to_sigma_payload,
    sponsorship_events_from_bill,
)

client = AuthenticatedClient(token="your-api-key")
bill_service = Bill(client=client)
bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
cosponsors = bill.get_cosponsors(limit=250)

events = sponsorship_events_from_bill(bill, cosponsors)
graph = build_graph_slice(
    events,
    GraphExploreConfig(congress=118, min_weight=1, max_edges=3000),
)

payload = graph_slice_to_sigma_payload(graph)
export_graph_slice_json(graph, "overview.json", format="sigma")
```

## Data layers

### Raw event layer

Each `SponsorshipEvent` represents one sponsor/cosponsor pair on one bill. Events are **not** deduplicated prematurely so drill-down, temporal views, and alternate projections stay auditable.

### Member-pair projection (default)

`GraphProjectionType.SPONSOR_TO_COSPONSOR` aggregates directed sponsor → cosponsor edges with weights for:

- total, active, original, late, and withdrawn cosponsorships
- cross-party relationships
- first/last relationship dates
- distinct bill counts

### Collaboration projection

`GraphProjectionType.COLLABORATION` collapses direction into sorted member pairs for social-network-style views.

## Filters

`GraphExploreConfig` supports the MVP filters from the design plan:

| Field | Purpose |
|-------|---------|
| `congress` | Restrict to one Congress |
| `bill_type` | Optional bill type (`hr`, `s`, etc.) |
| `chamber` | `all`, `house`, or `senate` |
| `policy_area` | Optional policy-area name |
| `min_weight` | Minimum active relationship count |
| `max_edges` | Top-N edge cap with truncation metadata |
| `cross_party_only` | Keep only cross-party ties |
| `original_only` | Keep only original cosponsorships |
| `include_withdrawn` | Include withdrawn cosponsorships (excluded by default) |

Withdrawn cosponsors are excluded from active edge weights by default.

## Drill-down helpers

```python
from congressgov.services.export.graph import (
    EgoNetworkConfig,
    build_ego_graph,
    build_member_summary,
    get_edge_evidence,
    rank_relationships,
    build_matrix,
)

summary = build_member_summary(events, "B001230", GraphExploreConfig(congress=118))
evidence = get_edge_evidence(events, "B001230", "C001111", GraphExploreConfig(congress=118))
ego = build_ego_graph(events, "B001230", EgoNetworkConfig(congress=118, direction="outgoing"))
matrix = build_matrix(events, GraphExploreConfig(congress=118), sort="party")
ranked = rank_relationships(events, GraphExploreConfig(congress=118), top_n=25)
```

## Ingestion helpers

For one Congress and bill type:

```python
from congressgov.services.export.graph import GraphIngestionConfig, ingest_bill_events

events = ingest_bill_events(
    bill_service,
    GraphIngestionConfig(congress=118, bill_type="hr"),
    fetch_cosponsors=True,
)
```

Async ingestion mirrors sync behavior via `ingest_bill_events_async`.

### Congress roster graph (member-first, persistent)

Seed all members who served in a Congress, then add bills over time:

```python
from pathlib import Path

from congressgov import Bill, Member, get_client_from_env
from congressgov.services.export.graph import (
    CongressGraphStore,
    GraphExploreConfig,
    export_interactive_html,
)

client = get_client_from_env()
store_path = Path(".congressgov/datasets/graphs/118.json")
store = CongressGraphStore.open(store_path, congress=118)

if store.member_count == 0:
    store.seed_members_from_service(Member(client=client))
    store.save()

bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)
cosponsors = bill.get_cosponsors(limit=250)
store.add_bill(bill, cosponsors, save=True)

graph = store.build_slice(
    GraphExploreConfig(congress=118, include_all_members=True, min_weight=1),
)
export_interactive_html(graph, "118_network.html")
```

Each `add_bill` call skips bills already recorded in the store. Re-open the same path later, ingest additional bills, and call `build_slice` again — member nodes persist even when they have no sponsorship ties yet.

**Live roster graph script** — fetches real bills using `CONGRESS_API_KEY` from `.env`.
Full flag reference: [GRAPH_CONSTRUCTION.md §6](GRAPH_CONSTRUCTION.md#6-cli-reference).

```bash
cp .env.example .env   # set your API key
poetry run python examples/congress_roster_graph_live.py --congress 118 --bill-type hr --max-bills 25
poetry run python examples/congress_roster_graph_live.py --max-bills 10
poetry run python examples/congress_roster_graph_live.py --help
```

The roster script seeds the full member roster, saves to `.congressgov/datasets/graphs/{congress}.json`, and merges new bills on each run.

Pass `--workspace-exports` to write HTML/JSON artifacts into the workspace `exports/` lane (see [STORAGE.md](STORAGE.md)):

```bash
poetry run python examples/congress_roster_graph_live.py --workspace-exports --max-bills 10
```

Writes `examples/output/congress_roster_graph/roster_graph_explorer.html` plus JSON summaries.

### Ephemeral network graph (bill batch)

For a one-shot graph from a fetched bill batch (no full roster), use
Full flag reference: [GRAPH_CONSTRUCTION.md §6](GRAPH_CONSTRUCTION.md#6-cli-reference).

```bash
poetry run python examples/network_graph_live.py --congress 118 --bill-type hr --max-bills 25
poetry run python examples/network_graph_live.py --help
```

Writes `examples/output/network_graph/live_network_explorer.html` plus JSON summaries.

### Workspace offline replay

When `CONGRESS_WORKSPACE` (or `.congressgov/`) is configured, open the graph record lane instead of ad-hoc paths:

```python
from congressgov.storage import open_workspace
from congressgov.services.export.graph import CongressGraphStore, GraphExploreConfig, export_interactive_html

workspace = open_workspace()
store = CongressGraphStore.open_for_workspace(workspace, congress=118)
graph = store.build_slice(GraphExploreConfig(congress=118, include_all_members=True))
export_interactive_html(graph, workspace.write_export("roster_graph_explorer.html"))
```

The notebook [`examples/network_graph_exploration.ipynb`](../../examples/network_graph_exploration.ipynb) includes a **Workspace offline replay** section that rebuilds a roster graph slice from a persisted dataset without live API calls.

## Export formats

- `graph_slice_to_sigma_payload()` — Graphology/Sigma.js node/edge attributes
- `graph_slice_to_api_payload()` — overview API response shape from the design doc
- `matrix_slice_to_api_payload()` — sparse adjacency matrix payload
- `export_graph_slice_json()` / `export_matrix_slice_json()` — write JSON files
- `export_interactive_html()` — standalone browser explorer (**Sigma.js 2 + Graphology**, WebGL)
- `GraphVisualizer` — matplotlib node-link and matrix heatmap rendering
- `export_graph_slice_csv()` / `export_graph_slice_graphml()` / `export_graph_slice_gexf()` — analysis exports

## Layouts and metrics

`GraphExploreConfig` now supports richer graph preparation:

| Field | Purpose |
|-------|---------|
| `layout_algorithm` | `spring`, `force_directed`, `kamada_kawai`, `circular`, `shell_party` |
| `node_color_mode` | Default coloring hint for renderers (`party`, `community`, `centrality`) |
| `compute_communities` | Greedy modularity community detection |
| `compute_advanced_metrics` | Betweenness and PageRank on graphs up to `advanced_metrics_max_nodes` |

Each graph slice also includes a deterministic `layout_key` for stable precomputed coordinates.

Member node labels use the congressional display format
`Rep./Sen. Last, First [Party-State-District]` (Senate labels omit the district segment).
Labels are resolved from Congress.gov `fullName` values when present, with fallbacks from
`firstName`, `lastName`, party, state, and district fields.

## Large and dense graphs

Use density assessment helpers before rendering very connected slices:

```python
from congressgov.services.export.graph import (
    assess_graph_slice,
    generate_dense_sponsorship_events,
    profile_graph_rendering,
    recommend_explore_config,
)

events = generate_dense_sponsorship_events(member_count=120, bills_per_sponsor=20, cosponsors_per_bill=40)
graph = build_graph_slice(events, GraphExploreConfig(congress=118, max_edges=3000))
assessment = assess_graph_slice(graph)
safer_config = recommend_explore_config(GraphExploreConfig(congress=118), assessment)
profile = profile_graph_rendering(graph)
```

Size tiers (`small`, `medium`, `large`, `very_large`) follow the design thresholds and recommend
when to prefer matrix/table/ego views over a full node-link overview. Sigma HTML exports embed
these warnings and disable expensive hover highlighting on large graphs.

The standalone HTML explorer includes client-side controls:

### View modes

Switch between five reorganized views (sidebar tabs or keys **1–5**):

| View | Purpose |
|------|---------|
| **Graph** | Sigma.js node-link overview with layout switcher |
| **Matrix** | Canvas heatmap of top members sorted by party (sparse adjacency) |
| **Ranked** | Scrollable table of strongest sponsor→cosponsor ties |
| **Ego** | Neighborhood subgraph around a chosen member (1–3 hops) |
| **Members** | Leaderboard by total degree; click a row to jump to ego view |

Graph and ego views support **layout presets** (11 options in grouped categories):

| Layout | Purpose |
|--------|---------|
| Server | Precomputed spring/force coordinates from export |
| Party shells / columns | Concentric rings or vertical party bands |
| State clusters | Mini-clusters grouped by state |
| Chamber split | House left, Senate right |
| Degree rings | Concentric activity bands by total degree |
| Sponsor flow | Sponsors (out-degree) left, cosponsors (in-degree) right |
| Circular / alphabetical / spiral / grid | Geometric arrangements |

The sidebar **legend panel** updates with the active node color mode and documents node size, edge color/thickness, and focus states.

### Filters and tools

| Control | Purpose |
|---------|---------|
| Live member search | Filter and jump to members by name or bioguide ID (`/` focuses search) |
| Fit graph / Clear focus | Frame visible nodes or reset pinned selection (`f` / `Esc`) |
| Filter presets | Readable, cross-party, or reset all filters |
| Minimum edge weight | Hide weaker ties without re-fetching data |
| Edge opacity | Adjust hairball readability on dense slices |
| Party filters | Show/hide Democrats, Republicans, etc. |
| Cross-party only | Isolate bipartisan ties |
| Show labels / neighbor highlight | Toggle label density and ego highlighting |
| Top relationships table | Click ranked pairs to focus an edge in the graph |
| Export filtered JSON | Download the currently visible slice as JSON |
| Ego center + hops | Pick a member and hop depth for ego view |

## Interpretation safeguards

When presenting graphs to users:

- Cosponsorship is not the same as ideological agreement.
- High counts may reflect popularity, leadership strategy, or symbolic legislation.
- Cross-party ties are useful but incomplete measures of bipartisanship.
- Original and late cosponsorships carry different meaning.
- Withdrawn cosponsorships should remain visible in evidence views.
- Displayed graphs may be filtered or truncated for readability.

## Related docs

- [GRAPH_CONSTRUCTION.md](GRAPH_CONSTRUCTION.md) — all graph construction methods and live script reference
- [ADVANCED.md](ADVANCED.md) — optional extras (`export`, `graph`, `batch`)
- [REFERENCE.md](REFERENCE.md) — services and extensions
- Bill cosponsor fetching — `Bill.get_cosponsors(...)`
- Interactive notebook — [`examples/network_graph_exploration.ipynb`](../../examples/network_graph_exploration.ipynb)
- Ephemeral network graph — [`examples/network_graph_live.py`](../../examples/network_graph_live.py)
- Congress roster graph — [`examples/congress_roster_graph_live.py`](../../examples/congress_roster_graph_live.py)
