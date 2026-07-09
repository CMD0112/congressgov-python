# Storage adoption audit

Track end-to-end adoption of the unified storage paradigm across the SDK.
Criteria (see [CMD-543](linear://cmd0112/issue/CMD-543)):

| ID | Criterion | Question |
| -- | -- | -- |
| **A** | Storage leverage | Does the process persist or read from the appropriate lane? |
| **B** | Duplicate-work prevention | Does the process skip redundant network/API work? |
| **C** | Cache-aware downstream logic | Does downstream logic work when data is already cached? |

Legend: yes = adopted, partial = partial, no = gap (pre-remediation)

## Client & blob lane

| Process | A | B | C | Notes |
| -- | -- | -- | -- | -- |
| `get_client_from_env()` | yes | yes | yes | Registry-backed blob store |
| `create_api_client(request_store=True)` | yes | yes | yes | Routes via `Workspace.blob_store()` |
| `create_api_client()` default bare | partial | partial | — | Intentional opt-in; use `create_stored_api_client()` |
| `RequestStore.open()` | yes | yes | yes | Workspace-relative paths |
| Legacy `.congressgov/request_store.db` | yes | yes | yes | Auto-migrate to `api/` on workspace open |
| `config.yaml` blob overrides | yes | yes | yes | Via `StoreRegistry` |

## Extension fetch & expand

| Process | A | B | C | Notes |
| -- | -- | -- | -- | -- |
| `Member.get_sponsored_legislation()` | yes | yes | yes | Reference `bind_related_attribute` pattern |
| `Bill.get_*()` sub-resources | yes | yes | yes | `bind_bill_subresource` + `refresh=` |
| `Bill.expand()` / `ApiService.expand()` | yes | yes | yes | Skip loaded attributes unless `force_fetch` |
| `CountRef.fetch()` / url_follow | yes | yes | yes | Skip when parent field already hydrated |
| `fetch_from_url(force_fetch=)` | yes | yes | yes | Respects request-store policy |

## Graph pipeline

| Process | A | B | C | Notes |
| -- | -- | -- | -- | -- |
| `CongressGraphStore` record lane | yes | yes | yes | `.congressgov/datasets/graphs/{congress}.json` |
| `CongressGraphStore.save()` provenance | yes | — | — | `built_at`, counts, path |
| `add_bills()` early dedup | yes | yes | — | Skips cosponsor fetch when bill ingested |
| `ingest_bill_events(graph_store=)` | yes | yes | — | Optional skip via store bill IDs |
| `Workspace.open_graph()` | yes | — | — | Default graph entry path |

## Artifact & exports lane

| Process | A | B | C | Notes |
| -- | -- | -- | -- | -- |
| Default `exports` registry entry | yes | — | — | `file:///exports` |
| `Workspace.write_export()` | yes | — | — | Writes via `FileArtifactLane` |
| Graph HTML/JSON export helpers | yes | — | — | `export_graph_slice_to_workspace()` + direct paths |

## Deferred / legacy

| Process | A | B | C | Notes |
| -- | -- | -- | -- | -- |
| `UnifiedStorage` / TABLE lane | partial | — | — | Deprecated; registry-only |
| `MultiLevelCache` / CACHE lane | partial | — | — | Deprecated; not wired |
| `CachedApiService` | partial | — | — | Deprecated; use request store |

## Related Linear issues

- [CMD-543](linear://cmd0112/issue/CMD-543): Epic: adoption audit & remediation
- [CMD-544](linear://cmd0112/issue/CMD-544): This audit matrix
- [CMD-545](linear://cmd0112/issue/CMD-545): Legacy blob migration
- [CMD-546](linear://cmd0112/issue/CMD-546): Client factory to registry
- [CMD-547](linear://cmd0112/issue/CMD-547): Extension skip-if-loaded
- [CMD-548](linear://cmd0112/issue/CMD-548): Graph ingest pipeline
- [CMD-549](linear://cmd0112/issue/CMD-549): Artifact lane exports
- [CMD-550](linear://cmd0112/issue/CMD-550): Orphaned cache consolidation (deferred)
- [CMD-551](linear://cmd0112/issue/CMD-551): Storage-aware examples

See also: [STORAGE.md](./STORAGE.md), [REQUEST_STORE.md](./REQUEST_STORE.md).
