# Documentation index

Guides for **congressgov** (Python SDK for the [Congress.gov API v3](https://api.congress.gov/)). The installable package lives under [`src/congressgov/`](../src/congressgov/) — there is no top-level `middleware` or `models` package in **2.0+**.

**Codegen policy:** Hand-maintained files under `congressgov/services/` and `congressgov/services/extensions/` are listed in [`generator_config.yaml`](../codegen/config/generator_config.yaml) `protected_paths`. With `emit_review_sidecars: false` (default), `generate-middleware` and `generate-extensions` **skip** those paths instead of writing `*.generated.py` sidecars.

## By audience

| Audience | Start here | Also useful |
|----------|------------|-------------|
| New users | [USAGE.md](USAGE.md) | [REFERENCE.md](REFERENCE.md), [MEMBERS_QUERY.md](MEMBERS_QUERY.md) |
| Integrators / packaging | [PACKAGE_LAYOUT.md](PACKAGE_LAYOUT.md) | [VERSIONING.md](VERSIONING.md), [MIGRATION.md](MIGRATION.md) |
| Optional features (cache, batch, export) | [ADVANCED.md](ADVANCED.md), [REQUEST_STORE.md](REQUEST_STORE.md), [STORAGE.md](STORAGE.md) | [README.md](../README.md) extras table |
| Network graphs | [NETWORK_GRAPH.md](NETWORK_GRAPH.md), [GRAPH_CONSTRUCTION.md](GRAPH_CONSTRUCTION.md) | [ADVANCED.md](ADVANCED.md) |
| Architecture overview | [ARCHITECTURE.md](ARCHITECTURE.md) | [PACKAGE_LAYOUT.md](PACKAGE_LAYOUT.md) |
| Maintainers (OpenAPI regen) | [CODEGEN.md](CODEGEN.md) | [API_COVERAGE.md](API_COVERAGE.md), [codegen/README.md](../codegen/README.md) |
| Release / PyPI / GitHub | [PUBLISHING.md](PUBLISHING.md) | [GITHUB_SETUP.md](GITHUB_SETUP.md), [CHANGELOG.md](../CHANGELOG.md) |

## Quick links

- Runnable samples: [`examples/quickstart.py`](../examples/quickstart.py), [`examples/quickstart_async.py`](../examples/quickstart_async.py), [`examples/network_graph_exploration.ipynb`](../examples/network_graph_exploration.ipynb)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- Security: [SECURITY.md](../SECURITY.md)
- Project home: [README.md](../README.md)

## Document map

| File | Purpose |
|------|---------|
| [USAGE.md](USAGE.md) | Install, API key, sync/async examples, errors, congressional record types |
| [REFERENCE.md](REFERENCE.md) | Service table, client, models, extensions, exceptions |
| [MEMBERS_QUERY.md](MEMBERS_QUERY.md) | `Members` collection query/filter helpers |
| [URL_FETCH.md](URL_FETCH.md) | Fetch typed models from API `url` fields |
| [REQUEST_STORE.md](REQUEST_STORE.md) | HTTP-layer request deduplication and offline replay |
| [STORAGE.md](STORAGE.md) | Unified `.congressgov/` workspace and storage lanes |
| [STORAGE_AUDIT.md](STORAGE_AUDIT.md) | Storage adoption audit matrix (maintainers) |
| [ADVANCED.md](ADVANCED.md) | Caching, batch, export, rate limiting (optional extras) |
| [NETWORK_GRAPH.md](NETWORK_GRAPH.md) | Sponsor/cosponsor graph projections and Sigma JSON export |
| [GRAPH_CONSTRUCTION.md](GRAPH_CONSTRUCTION.md) | All graph construction methods, live scripts, and **CLI reference** |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, core vs extras, generated vs hand-maintained (summary) |
| [PACKAGE_LAYOUT.md](PACKAGE_LAYOUT.md) | Wheel/sdist layout, public namespaces, migration phases |
| [MIGRATION.md](MIGRATION.md) | Historical import path changes (1.x → 2.0) |
| [VERSIONING.md](VERSIONING.md) | SemVer and public API scope |
| [CODEGEN.md](CODEGEN.md) | **Canonical** OpenAPI regeneration runbook |
| [API_COVERAGE.md](API_COVERAGE.md) | Generated path coverage matrix (maintainers) |
| [PUBLISHING.md](PUBLISHING.md) | PyPI trusted publishing |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | GitHub remote and CI setup |
