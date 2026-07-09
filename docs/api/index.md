# API reference overview

This section is generated from docstrings via [mkdocstrings](https://mkdocstrings.github.io/). For a
narrative walkthrough, start with [USAGE.md](../guide/USAGE.md) or the hand-written [REFERENCE.md](../guide/REFERENCE.md)
instead — these pages are best used to look up a specific class or function once you know its name.

- **[Facade](congressgov.md)** — the top-level `congressgov` import surface (`get_client_from_env`, exceptions, workspace helpers).
- **[Services](services.md)** — `Bill`, `Member`, `Committee`, and the rest of the 21 resource classes.
- **[Extensions](extensions.md)** — query/filter/chain helpers dynamically attached to models (`Members.filter(...)`, `Bill.get_actions()`, …).
- **[Models](models.md)** — the Pydantic entities these services return (`Bill`, `Member`, `Amendment`, …).
- **[Async API](async_api.md)** — the `Async*` mirror of every sync service, under `congressgov.async_api`.

Optional-extra symbols (caching, export, batch, graph, rate limiting) are documented alongside their
narrative guides in [ADVANCED.md](../guide/ADVANCED.md) and [GRAPH_CONSTRUCTION.md](../guide/GRAPH_CONSTRUCTION.md)
rather than here, since they're only importable once the matching extra is installed.
