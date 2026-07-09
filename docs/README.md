# Documentation index

Guides for **congressgov** (Python SDK for the [Congress.gov API v3](https://api.congress.gov/)). The installable package lives under [`src/congressgov/`](../src/congressgov/) — there is no top-level `middleware` or `models` package in **2.0+**.

Maintaining this repository instead of using the SDK? Head straight to [maintainers/README.md](maintainers/README.md) — releases, CI, and codegen internals live there, out of the way of the user-facing guides below.

## By audience

| Audience | Start here | Also useful |
|----------|------------|-------------|
| New users | [guide/USAGE.md](guide/USAGE.md) | [guide/REFERENCE.md](guide/REFERENCE.md), [guide/MEMBERS_QUERY.md](guide/MEMBERS_QUERY.md) |
| Integrators / packaging | [guide/PACKAGE_LAYOUT.md](guide/PACKAGE_LAYOUT.md) | [guide/VERSIONING.md](guide/VERSIONING.md), [guide/MIGRATION.md](guide/MIGRATION.md) |
| Optional features (cache, batch, export) | [guide/ADVANCED.md](guide/ADVANCED.md), [guide/REQUEST_STORE.md](guide/REQUEST_STORE.md), [guide/STORAGE.md](guide/STORAGE.md) | [README.md](../README.md) extras table |
| Network graphs | [guide/NETWORK_GRAPH.md](guide/NETWORK_GRAPH.md), [guide/GRAPH_CONSTRUCTION.md](guide/GRAPH_CONSTRUCTION.md) | [guide/ADVANCED.md](guide/ADVANCED.md) |
| Architecture overview | [guide/ARCHITECTURE.md](guide/ARCHITECTURE.md) | [guide/PACKAGE_LAYOUT.md](guide/PACKAGE_LAYOUT.md) |

## Quick links

- Runnable samples: [`examples/quickstart.py`](../examples/quickstart.py), [`examples/quickstart_async.py`](../examples/quickstart_async.py), [`examples/network_graph_exploration.ipynb`](../examples/network_graph_exploration.ipynb)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- Security: [SECURITY.md](../SECURITY.md)
- Project home: [README.md](../README.md)

## Document map

| File | Purpose |
|------|---------|
| [guide/USAGE.md](guide/USAGE.md) | Install, API key, sync/async examples, errors, congressional record types |
| [guide/REFERENCE.md](guide/REFERENCE.md) | Service table, client, models, extensions, exceptions |
| [guide/MEMBERS_QUERY.md](guide/MEMBERS_QUERY.md) | `Members` collection query/filter helpers |
| [guide/URL_FETCH.md](guide/URL_FETCH.md) | Fetch typed models from API `url` fields |
| [guide/REQUEST_STORE.md](guide/REQUEST_STORE.md) | HTTP-layer request deduplication and offline replay |
| [guide/STORAGE.md](guide/STORAGE.md) | Unified `.congressgov/` workspace and storage lanes |
| [guide/ADVANCED.md](guide/ADVANCED.md) | Caching, batch, export, rate limiting (optional extras) |
| [guide/NETWORK_GRAPH.md](guide/NETWORK_GRAPH.md) | Sponsor/cosponsor graph projections and Sigma JSON export |
| [guide/GRAPH_CONSTRUCTION.md](guide/GRAPH_CONSTRUCTION.md) | All graph construction methods, live scripts, and **CLI reference** |
| [guide/ARCHITECTURE.md](guide/ARCHITECTURE.md) | Layers, core vs extras, generated vs hand-maintained (summary) |
| [guide/PACKAGE_LAYOUT.md](guide/PACKAGE_LAYOUT.md) | Wheel/sdist layout, public namespaces, migration phases |
| [guide/MIGRATION.md](guide/MIGRATION.md) | Historical import path changes (1.x → 2.0) |
| [guide/VERSIONING.md](guide/VERSIONING.md) | SemVer and public API scope |
