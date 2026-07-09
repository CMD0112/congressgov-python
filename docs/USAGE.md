# Usage guide

End-user guide for **congressgov**. For API tables and extension lists, see [REFERENCE.md](REFERENCE.md). For maintainers, see [CODEGEN.md](CODEGEN.md).

## Getting started

1. Install: `pip install congressgov`
2. Get a free [Congress.gov API key](https://api.congress.gov/sign-up/)
3. Set `CONGRESS_API_KEY` in your environment (or use a `.env` file — see `.env.example`)

```python
from congressgov import Bill, get_client_from_env

client = get_client_from_env()
bill = Bill(client=client).get(congress=118, bill_type="hr", bill_number=1)

print(bill.title)
actions = bill.get_actions()
print(len(actions) if actions else 0, "actions")
```

Search with filters:

```python
bills = Bill(client=client).search(congress=118, bill_type="hr", limit=10)
```

Omitting `format_` on `.search()` defaults to **JSON** for handlers that resolve format (bills, hearings, treaties, house votes, committee prints, etc.). You can still pass `format_="json"` explicitly.

For CRS bill summary **data**, use `from congressgov import Summary` (model) or `Summaries(client).search(...)` (service). There is no `Summary` service class.

Runnable sample: [`examples/quickstart.py`](../examples/quickstart.py).

## Async usage

Async services live under `congressgov.async_api` and mirror sync method names (`get`, `search`, sub-endpoints). Pass the same `AuthenticatedClient` (httpx async-capable).

```python
import asyncio
from congressgov import get_client_from_env
from congressgov.async_api import AsyncBill

async def main() -> None:
    client = get_client_from_env()
    bill = await AsyncBill(client=client).get(
        congress=118, bill_type="hr", bill_number=1
    )
    actions = await bill.get_actions_async()
    print(bill.title, len(actions) if actions else 0)

asyncio.run(main())
```

See [`examples/quickstart_async.py`](../examples/quickstart_async.py). Parity between sync and async public methods is enforced in CI (`tests/test_async_service_parity.py`).

## Authentication

| Approach | Example |
|----------|---------|
| Environment (recommended) | `export CONGRESS_API_KEY=...` then `get_client_from_env()` (uses **X-API-Key**; loads `.env` if `python-dotenv` is installed) |
| Explicit client | `from congressgov import create_api_client` or `from congressgov.client import AuthenticatedClient` with `auth_header_name="X-API-Key"`, `prefix=""` |
| Per call | `Bill(client=client).get(..., client=other_client)` |

If no client is available, services raise `congressgov.ClientNotFoundError`.

## Rate limits

Congress.gov returns rate-limit headers on responses (`X-RateLimit-Limit`, `X-RateLimit-Remaining`). The optional gateway layer can raise `congressgov.RateLimitError` when limits are exceeded.

Client-side throttling is **optional** (extras `cache` / rate-limiting modules). Core installs do not throttle by default. See [ADVANCED.md](ADVANCED.md) for `RateLimiter` and cached services.

## Errors

| Exception | Typical cause |
|-----------|----------------|
| `congressgov.ClientNotFoundError` | No `client` on service and none passed to the method |
| `congressgov.ValidationError` | Invalid `congress`, `chamber`, `bioguide_id`, etc. |
| `congressgov.APIError` | HTTP error from Congress.gov |
| `congressgov.RateLimitError` | Rate limit exceeded (when using gateway/rate-limit helpers) |

Catch `congressgov.MiddlewareError` for all middleware-specific errors.

## Beta endpoints

Some Congress.gov paths are marked beta in the official spec. Notable SDK surface:

- **`HouseVote.members(congress, session, vote_number)`** — per-member roll call positions. Documented as beta in the API; use for analysis, not as a guaranteed-stable contract until Congress.gov graduates the endpoint.

## Congressional record types

Congress.gov exposes three related surfaces. Pick the service that matches your URL shape:

| Service | Methods | Use when |
|---------|---------|----------|
| `CongressionalRecord` | `search(year=..., month=..., day=..., ...)` | Listing/searching via `/congressional-record` (universal search) |
| `DailyCongressionalRecord` | `search()`, `get_volume()`, `get_issue()`, `get_articles()` | Daily Record volumes, issues, and articles (`/daily-congressional-record/...`) |
| `BoundCongressionalRecord` | `search()`, `get_by_year()`, `get_by_year_month()`, `get_by_date()` | Bound volumes by calendar date (`/bound-congressional-record/...`) |

`CongressionalRecord` and `DailyCongressionalRecord` use different models and routes; do not assume one replaces the other. See [ARCHITECTURE.md](ARCHITECTURE.md) for registry aliases.

Example (daily issue articles):

```python
from congressgov import DailyCongressionalRecord, get_client_from_env

client = get_client_from_env()
daily = DailyCongressionalRecord(client=client)
articles = daily.get_articles(volume_number=170, issue_number=1, limit=5)
```

## Member collection queries

`Members` collections support filter/query helpers registered via extensions. See [MEMBERS_QUERY.md](MEMBERS_QUERY.md).

## Versioning

Public API stability and deprecation rules: [VERSIONING.md](VERSIONING.md). Release history: [CHANGELOG.md](../CHANGELOG.md).
