# Code generation

**congressgov** can regenerate the HTTP client, Pydantic models, `congressgov.services` wrappers, and extension stubs from an OpenAPI specification. Generated code is committed to the repo; consumers typically use the pre-built packages without running codegen.

See [ARCHITECTURE.md](ARCHITECTURE.md) for how generation fits the hybrid layout. End users: [USAGE.md](USAGE.md). SemVer: [VERSIONING.md](VERSIONING.md). Doc index: [README.md](README.md).

## Prerequisites

- Python 3.13+
- Clone the repository and install the **codegen** extra:

```bash
poetry install --with codegen
# Or: pip install -e ".[codegen]"
```

## Quick workflow

```bash
# 0. Refresh merged spec (after updating base or annotation overlay)
poetry run python -m codegen.scripts.merge_openapi_annotations

# 1. Validate the spec
poetry run python -m codegen validate-spec

# 2. Regenerate everything
poetry run python -m codegen generate-all

# Or stepwise:
poetry run python -m codegen generate-client
poetry run python -m codegen generate-models
poetry run python -m codegen generate-middleware
poetry run python -m codegen generate-extensions
poetry run python -m codegen generate-registry
```

Standalone scripts (not Click subcommands):

```bash
poetry run python -m codegen.scripts.emit_client_compat
poetry run python -m codegen.scripts.audit_client_compat
poetry run python -m codegen.scripts.api_coverage_matrix --check
```

## Configuration

| File | Purpose |
|------|---------|
| [`codegen/config/congressgov_openapi_base.yaml`](../codegen/config/congressgov_openapi_base.yaml) | Vendored official Congress.gov OpenAPI (do not edit by hand) |
| [`codegen/config/openapi_spec_annotations.yaml`](../codegen/config/openapi_spec_annotations.yaml) | `x-*` codegen annotations (21 entities) |
| [`codegen/config/openapi_spec.yaml`](../codegen/config/openapi_spec.yaml) | **Merged** spec — input for validate/generate |
| [`codegen/config/generator_config.yaml`](../codegen/config/generator_config.yaml) | Output paths, incremental markers, `protected_paths`, `emit_review_sidecars` |
| [`codegen/config/entity_mappings.yaml`](../codegen/config/entity_mappings.yaml) | Entity and field mapping overrides |
| [`codegen/config/openapi_client_config.yaml`](../codegen/config/openapi_client_config.yaml) | `openapi-python-client` options (`post_hooks`, package name) |

Default output directories (from `generator_config.yaml`):

| Output | Path on disk |
|--------|----------------|
| HTTP client | `src/congressgov/_client/` |
| Models | `src/congressgov/models/` |
| Sync services (when not protected) | `src/congressgov/services/` |
| Extensions (when not protected) | `src/congressgov/services/extensions/` |
| Model registry map | `src/congressgov/services/core/model_registry_generated.py` |

CLI command `generate-middleware` still uses the historical name; it targets `congressgov.services`, not a separate package.

## Incremental generation

When `incremental: true` and `preserve_custom: true`:

- Blocks marked `# CUSTOM:` are kept across regenerations.
- Generated sections may be marked `# GENERATED:`.
- Backups use the configured `backup_suffix` before overwrite (gitignored locally).

Review diffs carefully after `generate-all`; do not commit unintended overwrites.

## Protected paths

The file manager **skips writes** to paths in `protected_paths` in [`generator_config.yaml`](../codegen/config/generator_config.yaml). Hand-maintained core files are listed explicitly (not the whole `congressgov/services/core/` tree), so **`model_registry_generated.py` is regenerated** while `model_registry.py` stays hand-maintained and imports `MODEL_PATH_MAP` from the generated module.

Examples of protected service and extension modules:

- `src/congressgov/services/bill.py`, `member.py`, `amendment.py`, `committee.py`, and other adopted entity services
- Matching files under `src/congressgov/services/extensions/`
- `src/congressgov/models/entities/bill.py`, `member.py`, `amendment.py`, `src/congressgov/models/committees/committee.py`

Optional feature packages (`services/batch/`, `export/`, `caching/`, `rate_limiting/`, etc.) remain protected.

Full list: see `protected_paths` in `generator_config.yaml`.

## Protected services and extensions (default)

With `middleware.emit_review_sidecars: false` (default), `generate-middleware` and `generate-extensions` **log and skip** paths listed in `protected_paths`. No `*.generated.py` files are written.

Hand-maintained modules under `congressgov/services/` and `congressgov/services/extensions/` are canonical. After OpenAPI changes, update hand files directly (use `# CUSTOM:` markers where incremental model generation applies).

**Legacy sidecar workflow:** Set `emit_review_sidecars: true`, run `generate-middleware` / `generate-extensions`, diff `*.generated.py` against hand files, port changes, then set the flag back to `false`. Sidecars are not committed in the current baseline.

## Get-only client layout (`get_*` only)

For codegen-adopted API packages, only `get_*.py` endpoint modules and `__init__.py` compat re-exports are committed. Legacy-named shim files (e.g. `bill_details.py`) are removed when a matching `get_*` module exists.

After `generate-client`, run `emit-client-compat`. For get-only packages (`bill`, `amendments`, `member`, `committee`, `hearing`, `nomination`, `treaty`, `house_vote`, `summaries`, `crsreport`, `house_communication`, `senate_communication`, `committee_meeting`, `committee_report`, `committee_print`), compat prefers `get_*` imports and does **not** restore modules from `codegen/data/legacy_api_modules/`. Services may keep importing `bill_details_sync` etc. from package `__init__` — no import path changes required for this layout.

## Hand-maintained async services

Do **not** blindly regenerate or overwrite protected paths.

Hand `congressgov/services/async_api/<entity>.py` files are protected; `generate-middleware` skips them when `emit_review_sidecars` is false. `tests/test_async_service_parity.py` verifies sync public methods exist on async with matching signatures.

Always protect (manual edits only):

- `congressgov/services/async_api/bill.py`

Use `# CUSTOM:` markers in incrementally generated model files to preserve hand edits.

## CLI reference

| Command | Description |
|---------|-------------|
| `generate-all` | Client + models + services + extensions + registry |
| `generate-client` | `congressgov/_client` only (runs `emit-client-compat` after success) |
| `generate-models` | `congressgov/models/` only |
| `generate-middleware` | Service modules; **skips** protected paths by default |
| `generate-extensions` | Extension modules; **skips** protected paths by default |
| `generate-registry` | `services/core/model_registry_generated.py` (`MODEL_PATH_MAP`) |
| `generate-url-routes` | `services/core/url_routes_generated.py` (`URL_ROUTES` for `fetch_from_url`) |
| `validate-spec` | Parse and validate OpenAPI + entity config |
| `merge-openapi-spec` | Merge base + annotation overlay into `openapi_spec.yaml` |
| `emit-client-compat` | Rebuild `api/*/__init__.py` legacy `*_sync` / `*_async` exports |
| `emit-client-compat --vendor-legacy` | Snapshot legacy modules into `codegen/data/legacy_api_modules/` |
| `audit-client-compat` | Audit aliases vs `__init__` exports (CI) |
| `api-coverage-matrix` | Regenerate [API_COVERAGE.md](API_COVERAGE.md) + `api_coverage.json` |
| `api-coverage-matrix --check-service-methods` | Fail if any `service_method` rows remain (CI) |

Verbose logging: `poetry run python -m codegen.cli -v generate-all`.

## Updating the OpenAPI spec

1. Refresh `codegen/config/congressgov_openapi_base.yaml` from [LibraryOfCongress/api.congress.gov](https://github.com/LibraryOfCongress/api.congress.gov/blob/main/Documentation/swagger.yaml) when Congress.gov publishes updates.
2. Edit `codegen/config/openapi_spec_annotations.yaml` for new `x-*` annotations.
3. Run `poetry run python -m codegen.scripts.merge_openapi_annotations`.
4. Run `poetry run python -m codegen validate-spec`.
5. Run `poetry run python -m codegen generate-all` (or stepwise commands).
6. Run `poetry run ruff check .` and fix any issues in custom code.
7. Run `poetry run python -m codegen.scripts.api_coverage_matrix` and commit updated coverage docs if paths changed.
8. Update [CHANGELOG.md](../CHANGELOG.md) if public APIs changed.

## API client regeneration (fail-safe)

`generate-client` runs `openapi-python-client` into a **staging directory** first. The committed `congressgov/_client/` tree is replaced only when generation succeeds. If the full vendored spec cannot be regenerated, the existing client is left intact and `emit-client-compat` still runs when invoked manually.

After `merge-openapi-spec`, the merged spec is sanitized automatically (see table below). Run `generate-client` then `emit-client-compat` for legacy `*_sync` exports.

## Merge-time spec sanitization

`merge-openapi-spec` applies fixes in [`codegen/scripts/merge_openapi_annotations.py`](../codegen/scripts/merge_openapi_annotations.py) (do not hand-edit the vendored base spec):

| Quirk | Fix |
|-------|-----|
| `type: string` + `enum: [true, false]` (YAML booleans) | `type: boolean` |
| `items: [{ $ref: ... }]` | Collapse to `items: { $ref: ... }` |
| `type: array` without `items` | `items: { type: object }` |
| camelCase + PascalCase schema names | Rename camelCase to `{Pascal}Item` and rewrite `$ref`s |
| Path parameters not `required` | Set `required: true` |
| `default` on path parameter schemas | Remove (avoids invalid Python param order in generated client) |

After `generate-client`, [`normalize_client_tree`](../codegen/scripts/normalize_client_tree.py) runs **isort** and **ruff** (see `codegen/config/ruff_generated_client.toml`). [`patch_client_parse_response`](../codegen/scripts/patch_client_parse_response.py) fixes envelope list parsers that do not match API JSON shape. [`patch_client_format_none`](../codegen/scripts/patch_client_format_none.py) coerces `format_=None` to JSON so service callers can omit `format_` without `AttributeError`.

Hand-maintained services should prefer [`resolve_response_format`](../src/congressgov/services/api_format.py) (or `ApiService.resolve_format`) when calling the client; the client patch is a safety net for universal search and legacy call sites.

## Troubleshooting

| Issue | Action |
|-------|--------|
| `openapi-python-client` errors | `poetry install --with codegen`; run `merge-openapi-spec`; check YAML syntax. Failed regen does not delete the committed client. |
| New client breaks `*_sync` imports | Run `emit-client-compat` after `generate-client` |
| `merge-openapi-spec` warnings | Overlay path/method not in base spec — align with official swagger |
| Lost custom code | Restore from `.backup` files; add `# CUSTOM:` guards |
| Import errors after regen | `poetry install --with dev` |
| Async out of sync with sync | Edit `congressgov/services/async_api/` manually for affected services |
| No files from `generate-middleware` | Expected when paths are protected and `emit_review_sidecars` is false — update hand services directly |

Implementation: [`codegen/`](../codegen/) package and Jinja templates under `codegen/templates/`.
