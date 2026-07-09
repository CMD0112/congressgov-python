# API reference

Condensed reference for **congressgov**. For a minimal runnable sample, see [`examples/quickstart.py`](../examples/quickstart.py).

Caching, export, and batch symbols require optional extras (`pip install congressgov[all]`). See [ARCHITECTURE.md](ARCHITECTURE.md).

## HTTP client

Low-level access uses the generated `congressgov._client` package (import via `congressgov.client` for `Client` types):

```python
from congressgov.client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://api.congress.gov/v3",
    token="YOUR_API_KEY",
)
```

Or use the environment helper (recommended):

```python
from congressgov import get_client_from_env

client = get_client_from_env()  # reads CONGRESS_API_KEY
```

## Services

Import high-level services from `congressgov` (2.0+). Legacy `import middleware` was removed; use 1.5.x if you still need it:

| Service | Typical `get()` identifiers |
|---------|----------------------------|
| `Bill` | `congress`, `bill_type`, `bill_number` |
| `Member` | `bioguide_id` |
| `Committee` | `chamber`, `committee_code` |
| `Amendment` | `congress`, `amendment_type`, `amendment_number` |
| `Congress` | `congress` |
| `CommitteeMeeting` | `congress`, `chamber`, `event_id` |
| `CommitteePrint` | `congress`, `chamber`, `print_number` |
| `CommitteeReport` | `congress`, `report_type`, `report_number` |
| `CongressionalRecord` | varies by endpoint |
| `BoundCongressionalRecord` | `year`, `month`, `day` |
| `CRSReport` | `report_number` |
| `Hearing` | `congress`, `chamber`, `jacket_number` |
| `HouseCommunication` | `congress`, `communication_type`, `communication_number` |
| `HouseRequirement` | `congress`, `requirement_number` |
| `HouseVote` | `congress`, `session`, `vote_number` (see extensions for `members()` beta endpoint) |
| `Nomination` | `congress`, `nomination_number` |
| `SenateCommunication` | `congress`, `communication_type`, `communication_number` |
| `Summaries` | search parameters |
| `Treaty` | `congress`, `treaty_number` |

### Services vs data models

`import congressgov as cg` exposes **service** classes (`cg.Bill`, `cg.Summaries`, …). Pydantic **models** for parsed API data live under `congressgov.models`, with one exception on the facade:

| Layer | Plural | Singular |
|-------|--------|----------|
| Service (`cg.*`) | `Summaries` | *(no `Summary` service — list-only API)* |
| Model | `from congressgov.models import Summaries` | `from congressgov import Summary` or `from congressgov.models import Summary` |

There is no `cg.Summary(client)` — fetch bill summaries via `Summaries(client).search(...)`, `Bill(client).get(...).get_summaries()`, or related bill sub-resources.

### Common patterns

```python
from congressgov import Bill, Member, Committee

bill_service = Bill(client=client)
bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)

# Search (resource-specific kwargs)
bills = bill_service.search(congress=118, bill_type="hr", limit=10)

# Extension methods on returned models
actions = bill.get_actions()
cosponsors = bill.get_cosponsors()
```

Pass `client=` to the constructor, set `service.client`, or pass `client=` per call.

### Async services

```python
from congressgov.async_api import AsyncBill

async_bill = AsyncBill(client=client)
bill = await async_bill.get(congress=118, bill_type="hr", bill_number=1)
```

Async services use the same stored client from `get_client_from_env()` — no separate cached wrapper is required. See [REQUEST_STORE.md](REQUEST_STORE.md).

## Models

Pydantic models live under `congressgov.models`. They validate API payloads and support lazy loaders such as `get_actions()` on instances returned from services.

```python
from congressgov.models.entities import Bill, Member
```

Most users interact with models via `congressgov` services rather than constructing them directly.

## Query extensions

Extension methods are registered at import time (`congressgov.services.extensions`). There is no top-level `congressgov.services/actions.py` — **Actions** are extension-only on bill/amendment models. **HouseVote** roll-call members use `house_votes` extensions and `HouseVote.members()` (beta API).

Collection query helpers: [MEMBERS_QUERY.md](MEMBERS_QUERY.md).

On **instances**:

- `bill.get_actions()`, `bill.get_cosponsors()`, …
- `member.get_sponsored_legislation()` — load sponsorship list on the member; `item.fetch()` — resolve one stub to a full `Bill`/`Amendment` (see [URL_FETCH.md](URL_FETCH.md))

On **collections** returned from `search()`:

- `bills.filter(...)`, `bills.group_by(...)`, `bills.by_type("hr")`
- Chainable query builder: `members.query().filter(state="CA").all()`

Async `*_async` expansion helpers exist for Bill, Amendment, Member, Committee, Nomination, and Treaty.

## Errors

| Exception | When |
|-----------|------|
| `congressgov.ClientNotFoundError` | No API client available |
| `congressgov.ValidationError` | Invalid parameters |
| `congressgov.APIError` | Congress.gov API error response |
| `congressgov.RateLimitError` | Rate limit exceeded |

## Breaking changes

See [CHANGELOG.md](../CHANGELOG.md) for API migrations (e.g. `HouseVote.get()` kwargs, `Hearing.get()` parameters).
