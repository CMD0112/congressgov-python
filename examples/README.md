# Examples

Runnable scripts and notebooks for **congressgov**. Everything here expects a
`CONGRESS_API_KEY` in the environment or a repo-root `.env` (copy from
[`.env.example`](../.env.example); get a free key at
[api.congress.gov/sign-up](https://api.congress.gov/sign-up/)).

## Scripts

| Script | What it does | Requires |
|--------|---------------|----------|
| [`quickstart.py`](quickstart.py) | Fetch a bill and its actions, print request-store stats | core |
| [`quickstart_async.py`](quickstart_async.py) | Same as above, using the async API | core |
| [`network_graph_live.py`](network_graph_live.py) | Build an ephemeral sponsor/cosponsor graph from a live bill batch; writes `output/network_graph/live_network_explorer.html` | `congressgov[export,graph,viz]` |
| [`congress_roster_graph_live.py`](congress_roster_graph_live.py) | Seed the full member roster for a Congress, then grow sponsorship edges over time (dataset persists under `.congressgov/`); writes `output/congress_roster_graph/roster_graph_explorer.html` | `congressgov[export,graph,viz]` |
| [`_graph_live_common.py`](_graph_live_common.py) | Shared argparse/CLI helpers for the two graph-live scripts above (not run directly) | — |

Run any script with `poetry run python examples/<script>.py`. Both graph-live
scripts accept `--max-bills`, `--max-edges`, `--min-weight`, and other flags —
run with `--help` for the full list.

### `scripts/` (maintainer / debugging aids)

These support graph development and aren't part of the primary walkthrough:

| Script | What it does |
|--------|---------------|
| [`scripts/stress_dense_graphs.py`](scripts/stress_dense_graphs.py) | Profiles rendering on large synthetic graphs (perf work) |
| [`scripts/reexport_explorer_from_json.py`](scripts/reexport_explorer_from_json.py) | Re-renders the interactive HTML explorer from a previously saved Sigma JSON, without re-fetching from the API |
| [`scripts/debug_labels.py`](scripts/debug_labels.py) | Inspects member label resolution while iterating on graph rendering |
| [`scripts/check_html_labels.py`](scripts/check_html_labels.py) | Sanity-checks label strings inside a generated HTML explorer file |

## Notebooks

| Notebook | What it covers | Requires |
|----------|-----------------|----------|
| [`network_graph_exploration.ipynb`](network_graph_exploration.ipynb) | Building graph slices from sample data, drill-down evidence, Sigma.js export, and workspace offline replay | `congressgov[export,graph]` |
| [`visualization_export.ipynb`](visualization_export.ipynb) | `VisualizationExporter` chart types (bill types, timelines, member counts, vote breakdowns) over sample and pandas data | `congressgov[export,viz]` |

Open with `poetry run jupyter lab` (or your notebook front end of choice) from
the repo root so the relative `congressgov` import resolves against the local
`.venv`.

## Output

Scripts and notebooks write generated artifacts (HTML explorers, exported
charts) under `examples/output/`, which is gitignored — safe to delete anytime.

## See also

- [docs/USAGE.md](../docs/USAGE.md) — install, API key setup, sync/async basics
- [docs/NETWORK_GRAPH.md](../docs/NETWORK_GRAPH.md) and [docs/GRAPH_CONSTRUCTION.md](../docs/GRAPH_CONSTRUCTION.md) — graph construction reference
- [docs/ADVANCED.md](../docs/ADVANCED.md) — caching, batch, export, rate limiting extras
