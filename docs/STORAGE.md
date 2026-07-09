# Unified storage

The SDK uses a **workspace** (default: `./.congressgov`) as the single root for all
persistent data. Storage is organized into **lanes** by abstraction level.

## Workspace layout

```
.congressgov/
  config.yaml              # optional named store registry
  api/
    request_store.db       # blob lane — raw API responses
  datasets/
    graphs/
      118.json             # record lane — congress graph datasets
  exports/                 # artifact lane — HTML, CSV, GraphML, etc.
  cache/                   # optional TTL overlay (future)
```

Configure the root with `CONGRESS_WORKSPACE` or pass `Workspace.open("/path")`.

## Storage lanes

| Lane | Purpose | Example |
|------|---------|---------|
| **blob** | Raw HTTP responses, deduplicated | Request store (`api`) |
| **record** | Versioned JSON documents | `CongressGraphStore` |
| **table** | Queryable model collections | `UnifiedStorage` |
| **artifact** | Immutable export outputs | `FileArtifactLane` |
| **cache** | Ephemeral TTL overlay | `MultiLevelCache` |

### Which lane do I use?

- **Fetching from Congress.gov** → blob lane (automatic via `get_client_from_env()`)
- **Incremental graph datasets** → record lane (`workspace.open_graph(118)`)
- **Analytics tables** → table lane (`UnifiedStorage`)
- **Published exports** → artifact lane (`registry.artifact("exports")`)

## Quick start

```python
from congressgov import get_client_from_env
from congressgov.storage import Workspace, StoreRegistry

workspace = Workspace.open()
client = get_client_from_env(request_store=workspace.blob_connection())

graph = workspace.open_graph(118)
registry = StoreRegistry.from_workspace(workspace)
api_store = registry.blob("api")
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONGRESS_WORKSPACE` | `.congressgov` | Workspace root directory |
| `CONGRESS_REQUEST_STORE` | (workspace blob path) | Override blob backend connection |

`CONGRESS_REQUEST_STORE` still takes precedence over the workspace default when set.

## Named store registry

Optional `.congressgov/config.yaml`:

```yaml
version: 1
stores:
  api:
    lane: blob
    backend: sqlite:///api/request_store.db
    policy: default

  graphs/118:
    lane: record
    backend: file:///datasets/graphs/118.json
    schema: congress_graph/v1
    options:
      congress: 118
```

When no config file exists, a default `api` blob store is synthesized.

## CLI

```bash
congressgov-store workspace-summary
congressgov-store stats
congressgov-store list --prefix /bill
congressgov-store purge-stale
congressgov-store record-info graphs/118
```

Use `--workspace /path` to target a non-default workspace.

## Data lineage

The recommended flow:

```
Congress.gov API → blob lane (request store) → Pydantic models → record/table lanes → artifacts
```

Record stores may include optional `provenance` metadata describing source request keys
and build timestamps.

## Related docs

- [REQUEST_STORE.md](./REQUEST_STORE.md) — HTTP-layer deduplication and policies
- [STORAGE_AUDIT.md](./STORAGE_AUDIT.md) — Adoption audit matrix (criteria A/B/C)
- [NETWORK_GRAPH.md](./NETWORK_GRAPH.md) — record lane graph datasets
- [ADVANCED.md](./ADVANCED.md) — optional export extras

## Legacy cache layers (deprecated)

The unified workspace uses the **blob lane** (`StoringTransport` + request store) as the
single authoritative HTTP cache. These older types remain for backward compatibility but
are **not** used on the default client path:

| Type | Status | Use instead |
|------|--------|-------------|
| `CachedApiService` | Deprecated | `get_client_from_env()` request store |
| `MultiLevelCache` | Deprecated | Blob lane policies + in-flight dedup |
| `UnifiedStorage` (TABLE lane) | Registry-only | Record lane or pandas export |

The **CACHE** and **TABLE** registry lanes are reserved for future work; opening them
raises `NotImplementedError` or returns legacy adapters. Do not instantiate TABLE/CACHE
stores for new code.
