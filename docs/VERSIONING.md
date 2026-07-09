# Versioning and API stability

**congressgov** follows [Semantic Versioning](https://semver.org/) from **1.0.0** onward.

## Version numbers

| Bump | When |
|------|------|
| **MAJOR** | Breaking changes to the public Python API |
| **MINOR** | New features, new service methods, new models (backward compatible) |
| **PATCH** | Bug fixes, docs, internal refactors with no public API change |

## Public API (2.0+ scope)

Considered stable for semver purposes:

- **`congressgov`** — service classes, `get_client_from_env()`, exceptions, lazy optional symbols ([REFERENCE.md](REFERENCE.md))
- **`congressgov.services`** — same symbols as `congressgov` (explicit services namespace)
- **`congressgov.models`** — Pydantic models used by services
- **`congressgov.async_api`** — async service classes (parity with sync)
- **`congressgov.client`** — `Client`, `AuthenticatedClient`
- Optional extras (`cache`, `batch`, `export`, `all`) entry points described in README / ADVANCED

**Removed in 2.0** (were deprecated in 1.x): top-level **`middleware`**, **`models`**, **`congress_gov_api_client`** — see [MIGRATION.md](MIGRATION.md).

**Not** guaranteed as stable public API:

- `congressgov._client` module layout beyond documented `*_sync` / `*_async` compat exports (stable via `congressgov.client` for `Client` types)
- Codegen CLI outputs (maintainer-only)
- Undocumented internal modules (`congressgov.services.core`, `codegen`)

## Deprecations

1. Deprecate in a **minor** release (`DeprecationWarning` where practical).
2. Remove in the **next major** release.

Example (0.5.x → 1.0.0): `DailyCongressionalRecord.list()` was deprecated in 0.4.x and **removed** in 1.0.0; use `search()` instead.

## API coverage

As of 1.0.0, all paths in the merged OpenAPI spec are classified as covered by middleware services (see [API_COVERAGE.md](API_COVERAGE.md)). New Congress.gov paths may appear in future spec updates; we treat uncovered matrix rows as release blockers for minors that adopt new spec versions.

## Client compatibility shims

Through **1.0.x**, the generated HTTP client keeps legacy `*_sync` / `*_async` names on package `__init__` modules for backward compatibility. Migrating imports to raw `get_*` modules is optional until a future major (see roadmap in [ARCHITECTURE.md](ARCHITECTURE.md)).

## Support

- **Python:** 3.13+ (see `pyproject.toml`)
- **Congress.gov API:** v3 (`https://api.congress.gov/v3`)

Report bugs and feature requests via [GitHub Issues](https://github.com/CMD0112/congressgov-python/issues); security issues per [SECURITY.md](../SECURITY.md).
