# Extensions

These modules attach query, filter, and per-instance helper methods onto the plain Pydantic models
(so `Bill` stays a data model, and `Bill.get_actions()` / `Bills.filter(...)` are defined here
instead). They're registered when `congressgov.services.extensions` is imported, which happens
automatically as part of `import congressgov`. See [`_template.py`](https://github.com/CMD0112/congressgov-python/blob/main/src/congressgov/services/extensions/_template.py)
in the repo if you're adding a new one.

## Query builder

::: congressgov.services.extensions._query_builder
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Bill / Bills

::: congressgov.services.extensions.bill
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Members

::: congressgov.services.extensions.members
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Cosponsors

::: congressgov.services.extensions.cosponsors
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Actions

::: congressgov.services.extensions.actions
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Committees

::: congressgov.services.extensions.committees
    options:
      show_root_heading: false
      show_root_toc_entry: false

## URL follow

::: congressgov.services.extensions.url_follow
    options:
      show_root_heading: false
      show_root_toc_entry: false
