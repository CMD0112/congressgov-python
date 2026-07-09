# Advanced features

Optional capabilities beyond basic `get` / `search` — reach for these once you're doing more
than fetching a handful of records: bulk backfills across thousands of bills, exporting to
pandas or a database, or layering your own caching and rate-limit handling on top of the
request store. None of this is required for typical use; the core install covers `get()` and
`search()` on every service without any extras. Install the matching extra first:

```bash
pip install congressgov[cache]   # caching and rate limiting
pip install congressgov[export]  # pandas / file export
pip install congressgov[batch]   # batch processing
# or: pip install congressgov[all]
```

Symbols are lazy-imported from `congressgov` (see [ARCHITECTURE.md](ARCHITECTURE.md)).

## Request store (deduplicated API persistence)

See **[REQUEST_STORE.md](REQUEST_STORE.md)** for the full guide.

`get_client_from_env()` enables the store by default (SQLite at
`.congressgov/request_store.db`). Override with `CONGRESS_REQUEST_STORE` or
`request_store=False`.

```python
from congressgov import Bill, get_attached_store, get_client_from_env, fetch_options, print_store_stats

client = get_client_from_env()
bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)

with fetch_options(force_fetch=True):
    bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)

print_store_stats(get_attached_store(client))
```

**Async** — the same stored client works with `AsyncBill`, `AsyncMember`, etc.

**Offline** — `get_client_from_env(offline=True)` serves only from the store.

**CLI** — `congressgov-store stats` (or `python -m congressgov.services.core.request_store stats`)

## Caching and rate limiting (optional extras)

TTL caches (`MultiLevelCache`, `RedisCache`) remain available for custom layers.
Use the request store as the primary deduplication mechanism.

```python
from congressgov import RateLimiter, RateLimitConfig

limiter = RateLimiter(RateLimitConfig(requests_per_hour=5000))
```

Integrate with `congressgov.services.rate_limiting` monitoring utilities when calling many endpoints in a loop.

## Batch processing

Process many items with concurrency and retries:

```python
from congressgov import BatchProcessor, BatchConfig

processor = BatchProcessor(BatchConfig(max_concurrent=10))
# processor.run(items, fetch_fn, ...)
```

Submodules include streaming, circuit breaker, checkpointing, and reporting under `congressgov.services.batch`.

## Data export

Export models to files, pandas, or databases:

```python
from congressgov import DataExporter, ExportConfig, PandasIntegration

exporter = DataExporter(ExportConfig(output_dir="./output"))
pandas = PandasIntegration()
```

Visualization helpers live in `congressgov.services.export.visualization` (requires optional `viz` extra: `pip install congressgov[viz]`).

## Network graphs

Build filtered sponsor/cosponsor graph projections and export Sigma.js/Graphology JSON:

```python
from congressgov.services.export.graph import (
    GraphExploreConfig,
    build_graph_slice,
    sponsorship_events_from_bill,
)

events = sponsorship_events_from_bill(bill, bill.get_cosponsors(limit=250))
graph = build_graph_slice(events, GraphExploreConfig(congress=118, min_weight=2))
```

See [NETWORK_GRAPH.md](NETWORK_GRAPH.md). Optional spring layouts use NetworkX: `pip install congressgov[graph]`.

## Storage backends

`congressgov.services.core.storage` provides file, memory, and SQL adapters for caching layers. Example SQL URL: `sqlite:///congressgov_cache.db`.

## Custom extensions

Add methods under `congressgov/services/extensions/` and register them in `congressgov/services/extensions/__init__.py`. Use `# CUSTOM:` markers in generated files so codegen preserves your edits (see [CODEGEN.md](../maintainers/CODEGEN.md), a maintainer doc).

## Performance tips

- Reuse one `AuthenticatedClient` across services.
- Prefer `search(..., limit=N)` over unbounded lists.
- Use `get_client_from_env()` — responses persist locally by default.
- Use `fetch_options(force_fetch=True)` when you need fresh data.
- For large backfills, use `BatchProcessor` with conservative `max_concurrent`.
