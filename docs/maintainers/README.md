# Maintainer documentation

This section is for people maintaining the **congressgov** repository itself: releases, CI, and OpenAPI codegen. None of it is required to use the SDK — if that's what you're after, go back to the [user guide](../README.md).

## Document map

| File | Purpose |
|------|---------|
| [CODEGEN.md](CODEGEN.md) | **Canonical** OpenAPI regeneration runbook, including protected paths and the generated-vs-hand-maintained split |
| [API_COVERAGE.md](API_COVERAGE.md) | Generated OpenAPI path coverage matrix (regenerate with `poetry run api-coverage-matrix`) |
| [PUBLISHING.md](PUBLISHING.md) | PyPI trusted publishing setup and release checklist |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | Checklist for wiring a fresh GitHub remote and CI |

## Also useful

- [`codegen/README.md`](../../codegen/README.md) — codegen package entry point
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — dev setup, quality checks, PR workflow
- [CHANGELOG.md](../../CHANGELOG.md) — release history
