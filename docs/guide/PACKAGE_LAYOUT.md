# Package layout

How the **congressgov** distribution is organized on disk, what we consider public API, and how packaging evolved across releases.

## Goals

| Goal | Rationale |
|------|-----------|
| **Install name = import name** | PyPI package `congressgov` → `import congressgov` |
| **Single product namespace** | Users discover one tree, not multiple top-level packages |
| **Private generated code** | HTTP client is an implementation detail, not a second product |
| **Maintainer tooling outside wheels** | `codegen/` only in sdists / git clones |
| **Typed public surface** | `py.typed` on the facade package |
| **`src/` layout** | Avoid accidental imports from a dirty repo root during development |

## Current layout (2.0.x)

```
src/
  congressgov/               # Only public namespace in the wheel
    __init__.py              # Bill, Member, get_client_from_env, …
    py.typed
    services/                # API services
    models/                  # Pydantic domain models
    client/                  # → congressgov._client (public re-export)
    _client/                 # Generated HTTP client
    async_api/               # → congressgov.services.async_api

codegen/                     # Maintainer CLI (sdist only, not in wheel)
```

Legacy top-level packages **`middleware`**, **`models`**, and **`congress_gov_api_client`** were removed in **2.0.0** (they were deprecation shims in 1.3–1.5).

## Recommended imports

```python
from congressgov import Bill, get_client_from_env
from congressgov.services import Bill          # explicit
from congressgov.models import Bill as BillModel
from congressgov.client import AuthenticatedClient
from congressgov.async_api import AsyncBill
```

## Wheel contents (policy)

| Path | Wheel | sdist | Notes |
|------|-------|-------|-------|
| `src/congressgov/` (as `congressgov` on import) | Yes | Yes | Only guaranteed public namespace |
| `congressgov.services` | Yes | Yes | Bill, Member, core, extensions, async_api, optional extras |
| `congressgov.models` | Yes | Yes | Pydantic domain models |
| `congressgov._client` | Yes | Yes | Generated client; prefer `congressgov.client` for types |
| `middleware` / `models` / `congress_gov_api_client` | No | No | Removed in 2.0 |
| `codegen/` | No | Yes | `format = "sdist"` in `pyproject.toml` |

## Migration phases

| Release | Packaging work |
|---------|----------------|
| **1.1.0** | `congressgov` facade; `codegen` excluded from wheel |
| **1.2.0** | `congressgov.services`, `congressgov.models`, `congressgov.client` |
| **1.3.0** | Generated client at `congressgov/_client/`; `congress_gov_api_client` shim |
| **1.4.0** | Domain models at `congressgov/models/`; top-level `models` shim |
| **1.5.0** | Services at `congressgov/services/`; top-level `middleware` shim |
| **2.0.0** | `src/` layout; drop legacy top-level shims |

See [MIGRATION.md](MIGRATION.md) and [VERSIONING.md](VERSIONING.md).
