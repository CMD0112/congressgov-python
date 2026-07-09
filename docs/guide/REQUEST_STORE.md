# Request store

Persistent deduplication for every Congress.gov API request. The store is the **blob lane**
of the project workspace — see **[STORAGE.md](STORAGE.md)** for the full storage model.

If you've ever re-run a script and watched it re-fetch the same bill or member you already
pulled minutes ago, this is the layer that fixes that: every request gets its response
recorded locally, keyed by URL and query parameters, so an identical call later is served
from disk instead of hitting Congress.gov again. It also means you can develop and test
offline once a workspace has been populated.

The store is enabled by default when you call `get_client_from_env()`.

## Quick start

```python
from congressgov import Bill, get_client_from_env, fetch_options

client = get_client_from_env()
bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)
```

Repeat calls with the same URL and query parameters are served from storage unless
`force_fetch=True`.

## Configuration

| Variable / parameter | Default | Purpose |
|---------------------|---------|---------|
| `CONGRESS_REQUEST_STORE` | `sqlite:///.congressgov/api/request_store.db` | Backend connection string |
| `CONGRESS_WORKSPACE` | `.congressgov` | Workspace root directory |
| `request_store=False` | — | Disable store on `get_client_from_env()` |
| `store_fail=True` | `False` | Fall through to network on store errors |
| `offline=True` | `False` | Serve only from store (no API key required) |

### Backends

- `sqlite:///path/to/store.db` — default, stdlib SQLite with schema migrations
- `file:///path/to/dir` — one JSON file per request
- `redis://host:port/db` — shared store (`pip install congressgov[cache]`)
- `:memory:` — ephemeral (tests)

## Async

The same stored client works with async services:

```python
from congressgov import get_client_from_env
from congressgov.async_api import AsyncBill

client = get_client_from_env()
bill = await AsyncBill(client=client).get(congress=118, bill_type="hr", bill_number=1)
```

## Offline mode

After an online run populates the store:

```python
from congressgov import Bill, get_client_from_env

client = get_client_from_env(offline=True)
bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)
```

## CLI

```bash
congressgov-store stats
congressgov-store list --prefix /bill
congressgov-store purge-stale
```

Or via module:

```bash
poetry run python -m congressgov.services.core.request_store stats
poetry run python -m congressgov.services.core.request_store list --prefix /bill
poetry run python -m congressgov.services.core.request_store purge-stale
```

## URL fetch

``BillRef.fetch()``, ``URL.fetch()``, and :func:`fetch_from_url` honor the request
store. Pass ``force_fetch=True`` (or ``refresh=True``) to bypass cached responses:

```python
bill = ref.fetch(force_fetch=True)
```

## Policies

Bundled rules live in
[`default_policies.json`](../../src/congressgov/services/core/request_store/data/default_policies.json).
Override with a JSON or YAML file:

```python
from congressgov.services.core.request_store import RequestStore, load_policy_config

store = RequestStore("sqlite:///.congressgov/store.db")
store.config.policy = load_policy_config("my_policies.yaml")
```

Policy highlights:

- **Closed Congress permanence** — paths for congresses before the current minus one
  use `permanent` (never auto-refetch)
- **Response timestamps** — `updateDate` / `updateDateTime` from API JSON inform staleness
- **TTL tiers** — `volatile` (1m) through `static` (7d); see `estimate_staleness()`

## Introspection

```python
from congressgov import get_attached_store, print_store_stats

print_store_stats(get_attached_store(client))
```

See also [ADVANCED.md](ADVANCED.md).
