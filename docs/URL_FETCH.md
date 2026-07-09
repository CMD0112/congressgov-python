# URL-based entity fetch

Load typed models from Congress.gov **API** URLs embedded in API responses (`url` fields, `CountRef`, and reference types).

## Requirements

- URL must target `api.congress.gov` under the `/v3` prefix (with or without scheme).
- An `AuthenticatedClient` must be available via `client=`, `self.client`, or a parent collection’s `client`.
- Extensions register on import: `import congressgov.services.extensions` (or `from congressgov import Bill`).

## Core API

```python
from congressgov.services.core.url_resolver import fetch_from_url

bill = fetch_from_url(
    "https://api.congress.gov/v3/bill/119/hr/5054?format=json",
    client=my_client,
)
```

Async:

```python
from congressgov.services.core.url_resolver import fetch_from_url_async

bill = await fetch_from_url_async("/v3/bill/119/hr/5054", client=my_client)
```

## Instance methods

| Type | Method | Notes |
|------|--------|--------|
| `URL`, `CountRef` | `.fetch()` | Uses `.url`; on a `Bill`, updates the matching attribute (e.g. `cosponsors`) |
| `BillRef`, `MemberRef`, `AmendmentRef`, … | `.fetch()` | Uses `.url` or ID fields |
| `SponsoredLegislationItem`, `CosponsoredLegislationItem` | `.fetch()` | Bill or amendment URL/IDs → full model |
| `Sponsor`, `Cosponsor` | `.fetch_member()` | Member detail URL (polymorphic return) |

### Naming: `get_*()` vs `.fetch()`

- **`get_*()` / `expand()`** — load a **known sub-resource** onto a parent entity (e.g. `member.get_sponsored_legislation()` → list of stubs).
- **`.fetch()`** — resolve a **stub, ref, or URL** into a full model (e.g. `item.fetch()` → `Bill` or `Amendment`).

Example (sponsored legislation):

```python
member = Member(client).get(bioguide_id="A000374")
sponsored = member.get_sponsored_legislation()  # list of stubs on the member
bill = sponsored.sponsoredLegislation[0].fetch()  # stub → full Bill/Amendment
```

Same pattern elsewhere:

```python
bill_ref.fetch()           # BillRef → Bill
count_stub.fetch()         # CountRef → Actions, Cosponsors, etc.
sponsor.fetch_member()     # Sponsor → Member (named because return type differs)
```

On a bill detail, `CountRef` stubs are linked to the parent bill. Fetching a sub-resource stores the result on the bill and returns the same object:

```python
bill = item.fetch(client=client)
cosponsors = bill.cosponsors.fetch(client=client, limit=250)
assert bill.cosponsors is cosponsors  # Cosponsors(cosponsors=[...], pagination=...)
```

Use `limit=250` (or paginate with `offset`) when the default page size (20) is not enough.

## Skip-if-loaded and refresh

Extension fetch paths avoid duplicate HTTP when a parent entity already holds hydrated data:

- `Bill.get_*()` helpers accept `refresh=True` to force a new request.
- `Bill.expand()` and `ApiService` expansion skip attributes that are already loaded unless `force_fetch=True` is passed in fetch options.
- `CountRef.fetch()` on a bill returns the stored collection when the parent field is hydrated; pass `force_fetch=True` to refetch.

URL fetch helpers accept the same flag:

```python
bill = fetch_from_url(url, client=client, force_fetch=True)
cosponsors = bill.cosponsors.fetch(client=client, force_fetch=True, limit=250)
```

Deprecated: `fetch_legislation()` / `fetch_legislation_async()` on sponsorship items (use `.fetch()` / `.fetch_async()`).

## Regenerating routes

Route table: `src/congressgov/services/core/url_routes_generated.py`

```bash
poetry run python -m codegen.scripts.generate_url_routes
# or
poetry run python -m codegen generate-url-routes
```

Source: `codegen/config/legacy_client_aliases.yaml` (sync with client `get_*` exports).

## Errors

- `ValueError` — non-API URL or missing `url`/IDs
- `UnsupportedApiUrlError` — path not in route table
- `ClientNotFoundError` — no client resolved
