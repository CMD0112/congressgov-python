# Migration guide

How import paths evolve across **congressgov** releases. This document describes **historical** import paths; current code uses the `congressgov` namespace only (see [PACKAGE_LAYOUT.md](PACKAGE_LAYOUT.md)).

## 1.5.0 — services under `congressgov.services`

| Use case | Import |
|----------|--------|
| Services (canonical) | `from congressgov import Bill, get_client_from_env` |
| Services (explicit) | `from congressgov.services import Bill, Member` |
| Async | `from congressgov.async_api import AsyncBill` (re-exports `congressgov.services.async_api`) |

**Removed in 2.0:** `from middleware import …` — use `congressgov` / `congressgov.services` (shim existed in 1.5.x only).

## 1.4.0 — domain models under `congressgov.models`

| Use case | Import |
|----------|--------|
| Models (canonical) | `from congressgov.models import Bill, Member` |
| Models (submodule) | `from congressgov.models.entities.bill import Bill` |

**Removed in 2.0:** `from models import …` — use `congressgov.models` (shim existed in 1.4.x–1.5.x only).

## 1.3.0 — HTTP client under `congressgov._client`

| Use case | Import |
|----------|--------|
| HTTP client (public) | `from congressgov.client import AuthenticatedClient` |
| HTTP client (advanced / generated modules) | `from congressgov._client.api.<resource> import …` |

**Removed in 2.0:** `from congress_gov_api_client import …` — use `congressgov.client` / `congressgov._client` (shim existed in 1.3.x–1.5.x only).

Maintainer codegen output path: `src/congressgov/_client/` (see `generator_config.yaml`).

## 1.2.0 — nested public namespaces

Additive paths aligned with the PyPI distribution name (see [PACKAGE_LAYOUT.md](PACKAGE_LAYOUT.md)):

| Use case | Import |
|----------|--------|
| Services (explicit) | `from congressgov.services import Bill, get_client_from_env` |
| Models (explicit) | `from congressgov.models import Bill` |
| HTTP client | `from congressgov.client import AuthenticatedClient` |

`from congressgov import Bill` remains the recommended default. Legacy top-level `middleware` and `models` still ship in 1.x wheels; `congress_gov_api_client` is a shim only (see 1.3.0).

## 1.1.0 — canonical `congressgov` facade

**Install name unchanged:** `pip install congressgov`

### Recommended imports (new)

| Use case | Import |
|----------|--------|
| Services | `from congressgov import Bill, Member, get_client_from_env` |
| Async | `from congressgov.async_api import AsyncBill` |
| HTTP client | `from congressgov.client import AuthenticatedClient` |
| Optional extras | `from congressgov import CacheConfig, DataExporter, BatchProcessor, RequestStore` |

### Legacy imports (still work in 1.x)

| Legacy | Status |
|--------|--------|
| `from middleware import Bill` | Deprecated in 1.5 — use `congressgov` / `congressgov.services` |
| `from middleware.async_api import AsyncBill` | Deprecated in 1.5 — use `congressgov.async_api` |
| `from models import Bill` | Deprecated in 1.4 — use `congressgov.models` |
| `from congress_gov_api_client import AuthenticatedClient` | Deprecated in 1.3 — use `congressgov.client` |

Suppress the legacy warning when migrating gradually:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="middleware")
```

Or import via the facade first in the process: `import congressgov` sets `CONGRESSGOV_FACADE_IMPORT` before loading `middleware`.

### Codegen (maintainers)

| Before 1.1 | After 1.1 |
|------------|-----------|
| `poetry run generate-all` | `poetry run python -m codegen generate-all` |
| `poetry run validate-spec` | `poetry run python -m codegen validate-spec` |
| `poetry run merge-openapi-spec` | `poetry run python -m codegen.scripts.merge_openapi_annotations` |

**PyPI wheels** no longer ship the `codegen` package or console scripts. Clone the repository (or install from **sdist**) and use `poetry install --with codegen` for regeneration work.

## 2.0.0 — `src/` layout; legacy shims removed

**Breaking.** Pin `congressgov<2` if you still use legacy top-level imports.

| 1.x | 2.0 |
|-----|-----|
| `from congressgov import Bill` | Unchanged (backed by `congressgov.services`) |
| `from middleware import Bill` | **Removed** — use `congressgov` or `congressgov.services` |
| `from models import Bill` | **Removed** — use `congressgov.models` |
| `from congress_gov_api_client import …` | **Removed** — use `congressgov.client` / `congressgov._client` |
| Repo / codegen paths | `src/congressgov/…` (import name still `congressgov`) |

Maintainer codegen output paths use the `src/congressgov/` prefix in `generator_config.yaml`.

See [VERSIONING.md](VERSIONING.md) for semver policy.
