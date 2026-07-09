# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [2.1.1] - 2026-07-09

### Changed

- Codebase-wide prose and comment cleanup — rewrote module/class docstrings and stripped boilerplate `# NOTE:` comments, section banners, and templated "Best Practices"/"Features" headers across `services/extensions`, `services/core`, `services/batch`, `services/export`, `services/caching`, `services/rate_limiting`, and `models/entities`; added missing class docstrings (`Member`, `Amendment`, `Bills`, `Amendments`, and others) that double as the new API reference content.
- Reduced bold/em-dash/emoji density in `README.md`, `docs/GRAPH_CONSTRUCTION.md`, and `docs/STORAGE_AUDIT.md` (status legends now use plain `yes`/`partial`/`no` instead of `✅`/`⚠️`/`❌`).
- `README.md`: added PyPI/CI/docs badges, linked the Code of Conduct and GitHub Issues, added `URL_FETCH.md`/`STORAGE_AUDIT.md` to the doc table, and linked both example notebooks.
- `CONTRIBUTING.md`: added `pytest` and `mkdocs build --strict` to the quality-check list; linked the Code of Conduct and issue/PR templates.
- `docs/VERSIONING.md`: pointed the issue-reporting line at the concrete GitHub Issues URL.

### Added

- Hosted documentation site at https://cmd0112.github.io/congressgov-python/, built with MkDocs Material and deployed to GitHub Pages via `.github/workflows/docs.yml`. Includes an auto-generated API reference (`docs/api/*.md`, via `mkdocstrings`) alongside the existing hand-written guides.
- `examples/README.md` indexing every example script and notebook with its prerequisites.

## [2.1.0] - 2026-07-09

### Added

- **Unified storage workspace** — `.congressgov/` layout with storage lanes (blob, record, table, artifact); `Workspace`, `StoreRegistry`, and `congressgov.storage` facade; `CONGRESS_WORKSPACE` env var; extended `congressgov-store` CLI; legacy blob auto-migration; `export_graph_slice_to_workspace()` for artifact exports; see [STORAGE.md](docs/STORAGE.md) and [STORAGE_AUDIT.md](docs/STORAGE_AUDIT.md).
- **Request store** — persistent API deduplication enabled by default on `get_client_from_env()`; SQLite, file, and Redis backends; policy-based staleness; in-flight dedup; offline mode; CLI (`congressgov-store`); client factory routes through `StoreRegistry`; see [REQUEST_STORE.md](docs/REQUEST_STORE.md).
- **Client factories** — `create_stored_api_client()`, `create_offline_client()`; `CONGRESS_REQUEST_STORE` env var; `print_store_stats()` helper.
- **Policy system** — bundled JSON rules, closed-congress permanence, response `updateDate` timestamps, `estimate_staleness()`.
- **Storage-aware fetch** — `Bill.get_*()` and `Bill.expand()` skip already-loaded attributes; `CountRef.fetch()` respects parent hydration; graph `CongressGraphStore` provenance and early ingest dedup.
- **Network graph** — sponsor/cosponsor graph builder, `CongressGraphStore` persistent datasets, Sigma.js interactive HTML explorer, density-aware filtering; optional `[graph]` extra; see [NETWORK_GRAPH.md](docs/NETWORK_GRAPH.md). Examples: `examples/network_graph_live.py`, `examples/network_graph_exploration.ipynb` (includes workspace offline replay).
- **URL follow** — `fetch_from_url()` / `fetch_from_url_async()` resolve Congress.gov API URLs to typed models via a generated route table ([`url_resolver.py`](src/congressgov/services/core/url_resolver.py), [`URL_FETCH.md`](docs/URL_FETCH.md)).
- **`.fetch()` on refs** — `BillRef`, `MemberRef`, `AmendmentRef`, `CommitteeRef`, `TreatyRef`, `NominationRef`, `URL`, and `CountRef` fetch full entities from their API URLs or id fields.
- **Sponsorship item fetch** — `SponsoredLegislationItem.fetch()` and `CosponsoredLegislationItem.fetch()` (sync + async) resolve bill or amendment URLs or id fields to full models (same `.fetch()` pattern as refs).
- **Sponsor/cosponsor fetch** — `Sponsor.fetch_member()` and `Cosponsor.fetch_member()` (sync + async).
- **`Congress.get_members()`** — list members who served in a Congress (sync + async extensions).
- **`fetch_all` on member-by-Congress lists** — `Member.list_by_congress(..., fetch_all=True)` and `Congress.get_members(fetch_all=True)` paginate at 250 per request until the roster is complete.
- **`python-dotenv`** — promoted to a core runtime dependency so `get_client_from_env()` loads `.env` files without installing dev extras.

### Removed

- **`CachedBill`** / **`AsyncCachedBill`** — replaced by the HTTP-layer request store with standard `Bill` / `AsyncBill` services.

### Fixed

- **`onBehalfOfSponsor` validation** — `Bill` and `Amendment` accept a single `OnBehalfOfSponsor` object or a list from the API (Senate amendments and some resolutions previously raised `ValidationError` on `item.fetch()`).
- **Graph slice build** — `member_to_graph_node` no longer lazy-imports `GraphMemberNode`, avoiding class-identity failures after test/module reloads.
- **Test isolation** — `test_congressgov_public_api.py` / `test_package_layout.py` use `monkeypatch.delitem(sys.modules, ...)` instead of raw `sys.modules.pop(...)`, so popped module entries are restored after the test instead of leaking stale class objects (root cause of the `GraphMemberNode` identity failures above) into the rest of the pytest session.
- **Request store / storage / workspace** — staleness is computed from `fetched_at` instead of the API's `updateDate`, so cached responses aren't treated as immediately stale; in-flight dedup leader/follower gating is propagated on miss/failure instead of letting every follower become a new leader; `attach_request_store(client, None)` resolves the workspace SQLite path instead of silently falling back to `:memory:`; re-attaching a store to an already-wrapped client now replaces the old store; `default_workspace_root()` calls `.expanduser()` so `CONGRESS_WORKSPACE=~/...` resolves correctly; `url_resolver._query_to_kwargs` no longer silently drops unrecognized query params or crashes on malformed `offset`/`limit`; `store_registry` policy config paths resolve relative to `workspace_root` instead of CWD; `PolicyConfig.resolve()` uses `.match()` instead of `.search()` so unanchored rules can't match mid-path; `backends/file.py`'s `contains()` is now guarded by the same lock as the other methods.
- **Graph export** — ego graphs at `depth=2` now do a true 2-hop BFS instead of expanding entire neighbor stars; cosponsor chamber is inferred from the cosponsoring member instead of the bill's origin chamber, fixing cross-chamber mislabeling; bills with zero sponsorship events are no longer permanently marked ingested, so they can be revisited once cosponsor data becomes available; `get_edge_evidence` matches both edge orientations under `COLLABORATION` projection; `build_ego_graph` only aggregates directed edges for directed projections; `is_original_cosponsor=None` is now reported as "unknown" instead of "late"; `ingestion.py` separates the bill-search cap from the event-count cap and gives async ingestion the same `graph_store` dedup and hydration checks as sync; fixed a missing `MemberLabelResolver` type-only import (`F821`); `assign_communities` uses an id→node lookup instead of an O(n × communities) scan; `GraphVisualizer.draw_graph` restores `self.config` even if drawing raises.
- **Extensions / protocols** — `_field_matches` normalizes enum values (e.g. `Bill.type`) before comparing against plain-string filter expansions, fixing `filter(type="hr")` silently returning nothing; `order_by` no longer corrupts legitimate falsy sort keys (`0`, `False`); `Cosponsors.democrats()` / `.republicans()` filter on the API's `"D"`/`"R"` party codes instead of `"Democratic"`/`"Republican"`; async `CountRef.fetch_async` gets the sync version's parent-attribute shortcut and result binding; async `Bill` sub-resource getters cache/bind onto the parent the same way sync does; async member sponsorship methods support `limit="max"`; `protocols/member.py` imports the correct `extensions.members` module; stale `TYPE_CHECKING` import paths in `protocols/bill.py` corrected; `Congress` extension's `_resolve_congress_number` no longer mutates `instance.number` as a side effect.
- **Core services / codegen** — `codegen/scripts/generate_url_routes.py` resolves committee print/report `/text` routes to their specific models (`CommitteePrintTexts`/`CommitteeReportTexts`) instead of the generic `TextVersions`; `ApiService.expand()`'s `force_fetch` now applies per-attribute instead of only to the first attribute in the loop; `AsyncApiService._resolve_client` failures are caught as `ClientNotFoundError` (the exception it actually raises) instead of a dead `except ValueError`; `Member.get()` resolves its response format like other fetch paths; `get_current_roster()` (sync + async) paginates to completion instead of hard-capping at 750 members; `Bill.search_by_laws()` and `Congress.search()` (sync + async) attach `client` to returned collections and their items; async `CommitteePrint.get()` / `CommitteeReport.get()` validate `congress`/`chamber` like their sync counterparts; `expansion_helpers.extract_parameters_from_target` treats only `None` as a missing parameter, not falsy values like `0`/`False`; `url_resolver.fetch_from_url(_async)` coerces bare list payloads into the wrapper shape models expect (e.g. committee print/report `/text`); `rebuild.py` logs model-rebuild failures via `logging` instead of a bare `print()`.
- **Universal search** — `search()` / `search_async()` attach the resolved `client` to handler results (and nested list items), so extension methods work on search results the same way they do on direct fetches.
- **Graph store ingestion test** — `test_graph_store_add_bills_skips_before_cosponsor_fetch` now seeds the initial bill with a real sponsor/cosponsor pair so it is legitimately marked ingested before asserting the "already ingested" skip, matching the corrected zero-event-is-not-ingested behavior above (it previously relied on the bug it now guards against).

### Changed

- **`codegen/templates/extension.py.jinja2`** — regenerated `expand()` / `get_<attr>()` templates delegate to `ApiService.expand()` and `expansion_helpers.bind_related_attribute` instead of stale, undefined-`logger` / `deepcopy` / `response.parsed` logic, so future codegen runs match the hand-maintained implementation.
- **Dead code cleanup** — removed unused `DEFAULT_REQUEST_STORE_URL` export from `client_factory.py` / `services/__init__.py`; added missing `UnsupportedApiUrlError` to `services/__init__.py`'s `__all__`; removed unused imports and duplicated helpers flagged across `request_store`, `extensions`, and `export/graph`.
- **`CountRef.fetch()` on bills** — resolves sub-resources (e.g. cosponsors) to typed wrappers, assigns them on the parent `Bill` (e.g. `bill.cosponsors`), and uses normal `Model.__repr__` for envelope types (`Cosponsors`, `Actions`, …) instead of collection-style `<Name: N items>`.
- **`Bill.get_cosponsors()`** — stores the returned `Cosponsors` wrapper on `bill.cosponsors` (same as `bill.cosponsors.fetch()`).
- **Collection lists** — use `collection.query().to_list()` for a plain `list` of items; per-collection `to_list()` removed. `__iter__`, `__len__`, `__getitem__`, `__bool__`, and `__repr__` are registered once via `collections_registry`.
- **Sponsorship items** — `.fetch()` / `.fetch_async()` replace `fetch_legislation()` / `fetch_legislation_async()` (deprecated aliases retained for one release). Aligns with `BillRef.fetch()` and clarifies the split from `get_sponsored_legislation()`.
- **`Bill.get_amendments()`** / **`get_amendments_async()`** — populate `bill.amendments` with a list of full `Amendment` objects (not an `Amendments` wrapper).
- **`Bill.expand()`** — unwraps expanded `amendments` to `list[Amendment]` for consistent typing with detail refs and fetch helpers.
- **CommitteeReport** / **CommitteePrint** — `expand()` / `get_text()` for text sub-resources (sync + async).

### Deprecated

- **`CachedApiService`**, **`MultiLevelCache`**, **`UnifiedStorage` (TABLE lane)** — superseded by the request-store blob lane; see [STORAGE.md](docs/STORAGE.md#legacy-cache-layers-deprecated).

## [2.0.8] - 2026-05-22

### Added

- **`bind_related_attribute`** / **`bind_related_attribute_async`** in [`expansion_helpers`](src/congressgov/services/core/expansion_helpers.py) — fetch a related sub-resource, attach the resolved client, and store the result on the parent model attribute.
- **`propagate_client_to_items`** — member list/search/roster responses attach `client` (and parent collection link) to each `Member` in a `Members` collection.

### Changed

- **`Member.get_sponsored_legislation()`** / **`get_cosponsored_legislation()`** — populate `sponsoredLegislation` / `cosponsoredLegislation` on the member instance (return value is the same object as the attribute); reuse loaded payloads unless `refresh=True`; skip refetch when the attribute is already a full model (not a `CountRef` stub).
- **Client resolution** — `ApiService._resolve_client` and `AsyncApiService._resolve_client` fall back to the parent collection’s client when a member item has no `client` of its own.
- **`AsyncMember.get()`** — uses the resolved client for the details API call (was passing the raw `client` argument).
- **`get_current_roster`** (sync and async) — returned `Members` collections and their items receive the resolved client.
- **Publish workflow** — verifies checked-out `HEAD` matches the release tag, supports `workflow_dispatch` with a `tag` input, and asserts wheel `__version__` matches `pyproject.toml`.

## [2.0.7] - 2026-05-21

### Added

- **Member expansion** — `Member.expand()`, `expand_specific_attributes()`, and `get_available_attributes()` populate `sponsoredLegislation` and `cosponsoredLegislation` from the sponsorship list endpoints (sync via `MEMBER_MAPPINGS` / `expand_sync_instance`; async via `expand_async()` and `ASYNC_MEMBER_MAPPINGS`).
- **Async member extensions** — `expand_async`, `expand_specific_attributes_async`, `get_available_attributes_async`, and async `get_sponsored_legislation_async` / `get_cosponsored_legislation_async` on [`extensions/async/members.py`](src/congressgov/services/extensions/async/members.py).
- **Codegen** — Member `expansion_mappings` and `bioguide_id` parameter aliases in [`entity_mappings.yaml`](codegen/config/entity_mappings.yaml).

### Changed

- **Member protocols** — `MemberProtocol` and `AsyncMemberProtocol` declare expand helpers for type checkers.

## [2.0.6] - 2026-05-21

### Changed

- **Expansion architecture** — Sync `expand()` on Bill, Amendment, Committee, Treaty, and Nomination delegates to `ApiService.expand` through [`expansion_helpers`](src/congressgov/services/core/expansion_helpers.py) (shared parameter aliases, enum/string normalization, consistent logging). Async bill/amendment expansion uses the same normalization in `AsyncApiService.expand`.
- **Member sponsorship** — `Member.get_sponsored_legislation()` and `get_cosponsored_legislation()` return `SponsoredLegislation` / `CosponsoredLegislation` via `ModelRegistry` (async parity on member extensions).
- **Export** — `PandasIntegration.to_dataframe()` expands collection models such as `Bills` into one row per item.
- **HouseVotes extensions** — `house_votes` extension module is registered on import (query/filter helpers on `HouseVotes` collections).
- **Docs** — Documentation index at [`docs/README.md`](docs/README.md); path and terminology updates for 2.0.x layout (`congressgov.services`, no review sidecars). [`docs/CODEGEN.md`](docs/CODEGEN.md) is the canonical OpenAPI regen runbook.
- **Docs** — Members query guide at [`docs/MEMBERS_QUERY.md`](docs/MEMBERS_QUERY.md).
- **API coverage matrix** — Coverage label `middleware_service` renamed to `hand_service` in generated [`docs/API_COVERAGE.md`](docs/API_COVERAGE.md).
- **Docstrings** — Stale pre-2.0 `middleware` paths in service and model comments updated to `congressgov.services` terminology.
- **CongressionalRecord model** — Registry alias comment clarified (DailyCongressionalRecord APIs).
- **Dependencies** — `seaborn` minimum raised to 0.13 in the `viz` extra.

### Added

- `congressgov.services.core.expansion_helpers` — `normalize_param_value`, `extract_parameters_from_target`, `expand_sync_instance`.
- Tests: `test_expansion_helpers.py`, `test_member_sponsorship_extensions.py`, `test_pandas_integration.py`.
- Example notebook [`examples/visualization_export.ipynb`](examples/visualization_export.ipynb).

### Removed

- **`Model.expand_attributes`** — Unused; use model `expand()` extensions or `ApiService.expand`.
- **`ModelRegistry.get_expansion_mapping`** — Duplicate/stale mappings; use per-service `*_MAPPINGS` constants.
- Invalid WIP `models/base/mappings.py`.
- **`congressgov.services.async`** — Undocumented shim; use `congressgov.async_api` or `congressgov.services.async_api`.
- **Codegen review sidecars** — All committed `*.generated.py` files under `services/` removed; protected hand modules are canonical. Regeneration skips protected paths instead of writing sidecars.

### Fixed

- **Core dependencies** — `ipykernel` is no longer a required install dependency (dev optional group only).

## [2.0.4] - 2026-05-20

### Fixed

- **`Hearing.search`**, **`Summaries.search`** — Envelope list parsers in the generated client no longer iterate dict keys (fixes `ValueError: dictionary update sequence element #0 has length 1`). Patch script now handles single-line `from_dict` loops as well as multiline.
- **`Treaty.search`** — List endpoints skip eager `Treaty.from_dict` parsing; nullable `transmittedDate` (and similar) no longer crash `isoparse(None)`.
- **`HouseVote.search`** — `result` accepts arbitrary API strings (e.g. `"Elected Speaker Name"`) via `VoteResult | str`, not only the narrow enum.
- **Search format defaults** — `hearingsearch`, `treatysearch`, and `housevotesearch` (sync and async) resolve omitted `format_` to JSON like other resources.

### Added

- **`Summary` model** re-exported on the top-level `congressgov` package (`from congressgov import Summary`).
- Regression tests for hearing, summaries, treaty, and house vote search paths.
- Codegen: `patch_client_null_datetimes` after client regen; broader `patch_client_parse_response` (eager envelope list endpoints).

## [2.0.3] - 2026-05-20

### Changed

- **Dependencies** — Removed unused core packages (`beautifulsoup4`, `anytree`, `tenacity`). Dropped undocumented `jupyter` optional extra. Codegen formatting uses **ruff** instead of **black** (isort retained). Added **deptry** to dev extras for CI dependency audits.

### Fixed

- **`CommitteePrint.search`** — Generated client list parsers no longer iterate envelope dict keys (fixes `ValueError: dictionary update sequence element #0 has length 1` on `search(congress=119)`). `patch_client_parse_response` now patches all broken `get_*` list-iteration parsers (committee-print, committee-meeting, committee-report, etc.), not only congress endpoints.

## [2.0.2] - 2026-05-21

### Fixed

- **`CommitteeMeeting`** — `get()` resolves `format_` and chamber enums; `search()` resolves format/chamber on all list paths and raises `APIError` when the API returns an error string instead of meeting data (e.g. malformed requests that produced Django `NoReverseMatch` payloads). `get()` now raises **`APIError`** (not `ValidationError`) when Congress.gov returns not-found messages such as `"No Meeting matches the given query."` (HTTP 404 or error-shaped JSON).
- **`Bill.search`** — Stops passing unsupported `sort` to bill list endpoints (fixes `TypeError: sync_detailed() got an unexpected keyword argument 'sort'`); resolves `format_=None` to JSON on all bill list paths. Explicit `sort=` raises a clear `ValueError` (bill lists are fixed to latest-action order per the API).
- **Codegen** — `patch_client_format_none` handles multiline `format_` type unions; **47 detail/sub-resource** `get_*.py` modules are committed with `format_=None` coercion so CI `generate-client` drift check passes (list endpoints were already patched).

### Added

- **`resolve_chamber()`** in `congressgov.services.api_format` for chamber string → generated enum coercion.
- Tests: `test_committee_meeting_search_format.py`, `test_bill_search_format.py`.

## [2.0.1] - 2026-05-21

### Fixed

- **`format_=None`** — Services and universal search no longer pass `None` into the generated client (fixes `AttributeError: 'NoneType' object has no attribute 'value'` on `Committee.get`, `Committee.search`, `Amendment.search`, `Congress.get`, and similar calls). Generated client `_get_kwargs` coerces omitted format to JSON after `generate-client`.
- **`Congress`** — `get()` / `search()` resolve response format; congress list endpoints patched for API envelope JSON.
- **`Member`** — `search()` / `get_current_roster()` no longer depend on missing `core.search` module paths; direct member list API calls with resolved format.
- **`Amendment.search`** — Requires `congress` when filtering by `amendment_type`; format resolved on all amendment list paths.
- **Async parity** — `AsyncApiService.resolve_format` matches sync `ApiService.resolve_format`.

### Changed

- Search registry and docs updated for **2.0** import paths (`congressgov.services`, not `middleware`).

## [2.0.0] - 2026-05-20

### Changed

- **Breaking:** Package code now lives under **`src/congressgov/`** (standard src layout). Import paths are unchanged: `from congressgov import Bill`, `from congressgov.models import Bill`, etc.
- Maintainer codegen output paths use the `src/congressgov/` prefix (see `codegen/config/generator_config.yaml`).

### Removed

- **Breaking:** Top-level compatibility shims **`middleware`**, **`models`**, and **`congress_gov_api_client`** are no longer shipped on PyPI. Use `congressgov`, `congressgov.services`, `congressgov.models`, and `congressgov.client` instead. Pin `congressgov<2` if you still rely on legacy imports.

## [1.5.0] - 2026-05-20

### Changed

- API services now live at **`congressgov/services/`** (was top-level `middleware/`). Middleware, codegen, and tests use `congressgov.services`.
- **`congressgov`** and **`congressgov.services`** re-export the real service layer (no delegate to top-level `middleware`).

### Deprecated

- Top-level **`middleware`** — thin compatibility shim with `DeprecationWarning`; use `congressgov` or `congressgov.services`. Removed in 2.0.

## [1.4.0] - 2026-05-20

### Changed

- Domain Pydantic models now live at **`congressgov/models/`** (was top-level `models/`). Middleware, codegen, and registry paths use `congressgov.models`.
- **`congressgov.models`** is the real package (no longer a delegate to top-level `models`).

### Deprecated

- Top-level **`models`** — thin compatibility shim with `DeprecationWarning`; use `congressgov.models`. Removed in 2.0.

## [1.3.0] - 2026-05-20

### Changed

- Generated HTTP client now lives at **`congressgov._client/`** (was top-level `congress_gov_api_client/`). Middleware and codegen import `congressgov._client`.
- **`congressgov.client`** re-exports from `congressgov._client`.

### Deprecated

- Top-level **`congress_gov_api_client`** — thin compatibility shim with `DeprecationWarning`; use `congressgov.client` or `congressgov._client`. Removed in 2.0.

## [1.2.0] - 2026-05-20

### Added

- **`congressgov.services`**, **`congressgov.models`**, **`congressgov.client`** — nested namespaces aligned with the PyPI distribution name ([PACKAGE_LAYOUT.md](docs/PACKAGE_LAYOUT.md)).
- [`docs/PACKAGE_LAYOUT.md`](docs/PACKAGE_LAYOUT.md) — target `src/` layout and 2.0 migration plan.

### Changed

- `congressgov.client` is now a package (was `congressgov/client.py`).

## [1.1.1] - 2026-05-20

### Fixed

- **`get_client_from_env()`** now sends the API key as **`X-API-Key`** (Congress.gov requirement), not `Authorization: Bearer`.
- **Client compat exports** prefer `sync_detailed` so middleware can read `response.content` without monkeypatching.
- **`Bill.get()`** defaults `format` to **JSON** when omitted.
- Optional **`.env` loading** in `get_client_from_env()` when `python-dotenv` is installed.

### Fixed (docs)

- Document that **1.0.0** wheels lack the `congressgov` import facade; install **`>=1.1.0`** for documented quick-start imports.

## [1.1.0] - 2026-05-19

### Added

- **`congressgov` import facade** — canonical public API matching the PyPI distribution name (`from congressgov import Bill`, `congressgov.async_api`, `congressgov.client`).
- [`docs/MIGRATION.md`](docs/MIGRATION.md) — import path guide for 1.1 and planned 2.0.

### Changed

- User-facing docs and examples use `import congressgov` instead of `import middleware`.
- Maintainer codegen CLI: `poetry run python -m codegen …` (replaces `poetry run generate-*` console scripts).
- **PyPI wheels** exclude the `codegen` package (`format = "sdist"`); sdists and git clones still include it.

### Deprecated

- `import middleware` / `import middleware.async_api` — emits `DeprecationWarning` unless loaded via the `congressgov` facade first; removal planned in 2.0.

## [1.0.0] - 2026-05-16

**Note:** This release did not include a `congressgov/` Python package; `from congressgov import ...` fails. Use **1.1.0+** or `from middleware import ...` on 1.0.0 only.

### Added

- [`docs/USAGE.md`](docs/USAGE.md) — getting started, async, authentication, rate limits, errors, beta endpoints, congressional record guide.
- [`docs/VERSIONING.md`](docs/VERSIONING.md) — SemVer policy, deprecations, public API scope.
- [`examples/quickstart_async.py`](examples/quickstart_async.py) — async Bill sample.

### Changed

- **First PyPI release** at 1.0.0 (0.5.0 was not published to PyPI).
- README documentation table links to USAGE, VERSIONING, PUBLISHING, API_COVERAGE.
- GitHub repository name: `congressgov-python` (PyPI install name remains `congressgov`).

### Removed

- `DailyCongressionalRecord.list()` and `AsyncDailyCongressionalRecord.list()` — use `search()` (deprecated since 0.4.x).

## [0.5.0] - 2026-05-16

### Added

- Hand service sub-endpoints (sync + async): `Committee.get_by_congress`, `CommitteePrint.get_text`, `CommitteeReport.get_text`, `HouseVote.list_by_congress_session`, `Member.list_by_congress`, `Nomination.get_nominees`, `Treaty.get_actions`.
- `tests/test_sub_endpoint_services.py` for mocked sub-endpoint calls and coverage gap regression.

### Changed

- API coverage matrix: `HAND_METHOD_PATHS` classifier, `sync_detailed` import detection, early hand-method matching; CI fails when any `service_method` rows remain (`--check-service-methods`).
- [`docs/API_COVERAGE.md`](docs/API_COVERAGE.md): zero `service_method` backlog (108 operations).

## [0.4.0] - 2026-05-17

### Added

- `poetry run api-coverage-matrix` → [`docs/API_COVERAGE.md`](docs/API_COVERAGE.md) and `docs/api_coverage.json` (OpenAPI path coverage inventory).
- Async middleware codegen: `service_async.py.jinja2` + `middleware/async_api/*.generated.py` sidecars for all 21 entities (regenerate with `generate-middleware`).
- `tests/test_async_service_parity.py` (sync methods ⊆ async, signature parity, sidecar presence).
- `tests/test_actions_service.py` for Actions sidecar contract.
- Sub-endpoints: `HouseRequirement.matching_communications`, `BoundCongressionalRecord.get_by_year` / `get_by_year_month` / `get_by_date` (+ async mirrors).
- `DailyCongressionalRecord.search()` with deprecated `list()` alias.
- [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for PyPI trusted publishing.

### Changed

- CI: `audit-client-compat` and `api-coverage-matrix` in codegen job; async hand services protected in `generator_config.yaml`.
- `AsyncCRSReport.get()` aligned with sync service.

## [0.3.5] - 2026-05-17

### Added

- `HouseVote.members()` (sync + async) for the beta roll-call members endpoint; `HouseVoteMembers` registry alias.
- **DailyCongressionalRecord** middleware (`list`, `get_volume`, `get_issue`, `get_articles`) with async mirror, codegen list adoption, and adoption tests.
- `tests/test_async_service_parity.py` for tier-5/6 sync vs async public method alignment.
- GitHub Actions workflow `.github/workflows/publish.yml` (trusted publishing on GitHub Release).

### Changed

- **21 codegen entities** in merged spec (`validate-spec`); client get-only layout includes `daily_congressional_record`.
- `AsyncCongress.get()` now runs `validate_congress` like the sync service.

## [0.3.4] - 2026-05-17

### Added

- Tier-5 middleware codegen adoption for **Congress** (hand `current()`, validated `get`, direct-list `search`), **HouseRequirement**, **CongressionalRecord** (search-only), and **BoundCongressionalRecord** (search-only): OpenAPI annotations, `entity_mappings` / `service_codegen`, protected hand services and models, `*.generated.py` review sidecars.
- Runtime model registry wiring: `generate-registry` emits `middleware/core/model_registry_generated.py` (`MODEL_PATH_MAP`); hand `middleware/core/model_registry.py` merges codegen paths with `HAND_MODEL_OVERRIDES`.
- `tests/test_model_registry.py`, `tests/test_congress_service.py`, `tests/test_house_requirement_service.py`, `tests/test_congressional_record_service.py`, `tests/test_bound_congressional_record_service.py`.
- Service template: `parse_api_envelope` without `universal_search_entity` generates direct-list `search()` (Congress).

### Changed

- **20 codegen entities** in merged spec (`validate-spec`).
- Client get-only layout extended to `congress`, `house_requirement`, `congressional_record`, and `bound_congressional_record` API packages.
- Extended `tests/test_client_pilot_layout.py` for tier-5 packages.
- Removed duplicate `middleware/core/model_registry.generated.py` class artifact in favor of `model_registry_generated.py` map module.

## [0.3.3] - 2026-05-17

### Added

- Tier-4 middleware codegen adoption for **CommitteeMeeting**, **CommitteeReport**, and **CommitteePrint**: OpenAPI annotations, `entity_mappings` / `service_codegen`, protected hand services and models, `*.generated.py` review sidecars.
- `tests/test_committee_meeting_service.py`, `tests/test_committee_report_service.py`, `tests/test_committee_print_service.py`.

### Changed

- **16 codegen entities** in merged spec (`validate-spec`).
- Client get-only layout extended to `committee_meeting`, `committee_report`, and `committee_print` API packages.
- Extended `tests/test_client_pilot_layout.py` for tier-4 packages.

## [0.3.2] - 2026-05-17

### Added

- Tier-3b middleware codegen adoption for **Summaries** (search-only), **CRSReport** (list + `get`), **HouseCommunication**, and **SenateCommunication**: OpenAPI annotations, `entity_mappings` / `service_codegen`, protected hand services and models, `*.generated.py` review sidecars.
- Hand `CRSReport.get()` via `crsreport_details_sync` and `ApiEnvelope`.
- `tests/test_summaries_service.py`, `tests/test_crsreport_service.py`, `tests/test_house_communication_service.py`, `tests/test_senate_communication_service.py`.
- Tier-3 middleware codegen adoption for **HouseVote**: OpenAPI annotations, `entity_mappings` / `service_codegen`, protected hand service and model, `house_vote.generated.py` review sidecar.
- `tests/test_house_vote_service.py`.

### Changed

- **13 codegen entities** in merged spec (`validate-spec`); annotations cover pilot, tier-2, tier-3, tier-3b, and Actions.
- Model generator resolves output paths from `module_path` and skips protected targets (no stray `models/entities/housevote.py` after `generate-all`).
- Extension generator skips entities without `extension_path` (CRSReport has no extension module).
- Client `get_*` layout extended to all codegen-adopted API packages (`house_vote`, `summaries`, `crsreport`, `house_communication`, `senate_communication`); `emit-client-compat` skips vendor restore for those packages.
- Tier-2 API client packages (`hearing`, `nomination`, `treaty`): removed duplicate legacy endpoint modules; compat `__init__` exports use `get_*` only.
- Extended `tests/test_client_pilot_layout.py` for all get-only packages.
- Middleware generator: service output filename derived from `service_path` (fixes `HouseVote` → `house_vote.py` and prevents Actions from overwriting `bill.generated.py`).
- Actions OpenAPI overlay: `service-path` / `extension-path` for `middleware.actions`.

## [0.3.1] - 2026-05-17

### Changed

- Pilot API client packages (`bill`, `amendments`, `member`, `committee`): removed duplicate legacy endpoint modules; compat `__init__` exports use `get_*` only.
- `emit-client-compat` prefers `get_*` modules over legacy `source_module` files; skips vendor restore for pilot packages.

### Added

- Tier-2 middleware codegen adoption for **Hearing**, **Nomination**, and **Treaty**: OpenAPI annotations, `entity_mappings` / `service_codegen`, protected hand services and extensions, `*.generated.py` review sidecars.
- `tests/test_hearing_service.py`, `tests/test_nomination_service.py`, `tests/test_treaty_service.py`.
- Protected hand model modules for tier-2 entities (`models/documents/hearing.py`, `models/nominations/nomination.py`, `models/entities/treaty.py`).
- `tests/test_client_pilot_layout.py` for pilot client layout invariants.

## [0.3.0] - 2026-05-17

### Added

- OpenAPI merge sanitization for full `generate-client` success (boolean query params, schema name collisions, arrays without `items`, path param fixes).
- `tests/test_merge_openapi_sanitize.py`, `tests/test_member_service.py`, `tests/test_amendment_service.py`, `tests/test_bill_service.py`.

### Changed

- Regenerated `congress_gov_api_client/` from sanitized merged spec; `openapi_client_config` ruff post-hook uses `api/` relative to staging output.
- Member middleware adoption: `service_codegen` hooks in `entity_mappings.yaml`, `# CUSTOM:` markers in hand `middleware/member.py`, updated `member.generated.py` sidecar.
- Amendment middleware adoption: `service_codegen` hooks in `entity_mappings.yaml`, `# CUSTOM:` markers in hand `middleware/amendment.py`, regenerated `amendment.generated.py` sidecar; service template newline fix for `registry_models`.
- Bill middleware adoption: `service_codegen` hooks, `# CUSTOM:` markers in hand `middleware/bill.py`, regenerated `bill.generated.py` and `committee.generated.py` sidecars.
- Codegen: skip incremental merge for `*.generated.py` review sidecars (full replace on regen).
- CI: full `tests/` suite in `test` job; `codegen` job requires successful `generate-client` (no emit-only fallback).
- CI: blocking `generate-all` drift check (working tree must be clean after full regen).
- Regenerated extension sidecars and `model_registry.generated.py` aligned with `generate-all` baseline.
- Codegen: re-apply `entity_mappings` fallback after API client step in `generate-all` so `service_codegen` hooks are not lost before middleware regen.

## [0.2.0] - 2026-05-16

### Added

- Fail-safe `generate-client` staging (no partial delete of `congress_gov_api_client/` on regen failure).
- Committee middleware adoption: hand `middleware/committee.py` marked with `# CUSTOM:` validation and universal `search`; `entity_mappings` expansion mappings and `service_codegen` hooks for future regen.
- `tests/test_committee_service.py`, `tests/test_api_client_generator.py`.

### Changed

- CI client drift check tolerates `generate-client` failure when the full spec cannot regen (committed client preserved).
- `service.py.jinja2` supports `parse_api_envelope`, validation imports, and universal search via `service_codegen` in `entity_mappings.yaml`.
- List endpoint annotations for `/bill`, `/member`, `/amendment`; `generate-registry` and `generate-extensions` CLI commands.
- Review sidecars (`*.generated.py`) for pilot middleware; `model_registry.generated.py` no longer blocked by blanket `middleware/core/` protection.
- Compat audit uses param-preserving `path_signature` (no ambiguous `/member/{}` warnings).

### Notes

- Regenerated `congress_gov_api_client/` from merged OpenAPI spec (sanitized for known schema quirks).
- `generate-client` may still fail on a fresh clone until sanitization rules are applied; committed client is the source of truth until regen succeeds.

## [0.1.0] - 2026-05-15

### Added

- Initial public layout: `congress_gov_api_client/`, `models/`, `middleware/`, `codegen/`, Poetry package `congressgov`.
- OpenAPI-driven codegen CLI (`generate-client`, `generate-models`, `generate-middleware`, `generate-all`, `validate-spec`).
- Examples and documentation for Congress.gov API usage.
