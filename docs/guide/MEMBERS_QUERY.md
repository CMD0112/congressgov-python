# Querying members

`Members.search(...)` gets you a page of members back from the API, but most real work involves narrowing that list down — by state, by party, by chamber — and often combining a few of those filters at once. Rather than writing the same `[m for m in members if ...]` loops over and over, `Members` collections carry a small query interface that does the filtering for you and hands back another `Members` object, so you can keep chaining, slicing, or iterating exactly like you would with the original result.

```python
from congressgov import Member, get_client_from_env

client = get_client_from_env()
members = Member(client=client).search(limit=250)

ca_dems = members.filter(state="CA", partyName="Democratic")
for member in ca_dems:
    print(member.firstName, member.lastName)
```

## State codes and full names are interchangeable

Filtering by `state` accepts either form — `"CA"` or `"California"` — case-insensitively, and both return identical results:

```python
members.filter(state="CA")
members.filter(state="california")
```

This works because the query builder checks a `StateCode` enum for both the code and the matching full name before comparing. It only applies to the `state` field; other enum-like fields (e.g. `partyName`) still expect the value as the API returns it (`"Democratic"`, not `"D"`).

## Filtering

`filter(**kwargs)` is eager by default — it runs immediately and returns a `Members` object you can keep filtering, iterate over, or measure with `len()`:

```python
ca_members = members.filter(state="CA")
ca_dems = ca_members.filter(partyName="Democratic")
current_ca_dems = ca_dems.filter(currentMember=True)

print(f"{len(current_ca_dems)} current CA Democrats")
```

A handful of convenience methods cover the filters you'll reach for most often — they're just `filter()` under the hood:

```python
members.by_state("CA")
members.by_chamber("House of Representatives")  # or "Senate"
members.democrats()
members.republicans()
members.current()
```

For anything the built-in filters don't cover, drop down to a predicate with `where()`:

```python
young_members = members.query().where(lambda m: m.birthYear and m.birthYear > 1980)
```

## Eager vs. lazy chaining

Every example above re-filters eagerly, which means each `.filter()` call builds a full intermediate `Members` object before the next one runs. That's fine for one or two filters, but it adds up if you're chaining several in a row. Pass `lazy=True` to defer execution, then call `.execute()` once at the end:

```python
results = (
    members
    .filter(state="CA", lazy=True)
    .filter(partyName="Democratic", lazy=True)
    .order_by("lastName", lazy=True)
    .limit(10)
    .execute()
)
```

Use eager filtering for a quick one-off lookup; switch to `lazy=True` once you're chaining three or more operations together.

## Grouping

`group_by(field)` returns a plain `dict` where each value is itself a `Members` object, so you can keep querying within each group:

```python
by_party = members.group_by("partyName")
for party, party_members in by_party.items():
    print(f"{party}: {len(party_members)} members")

ca_dems_only = by_party["Democratic"].filter(state="CA")
```

## Sorting, pagination, and indexing

```python
sorted_members = members.filter(state="CA").order_by("lastName")
newest_first = members.order_by("birthYear", reverse=True)

page_1 = members.filter(state="CA").limit(20)
page_2 = members.filter(state="CA").skip(20).limit(20)
```

`Members` objects also support the usual Python protocols — indexing, slicing, `len()`, and truthiness — so you don't need query-builder syntax for simple access:

```python
first = ca_members[0]          # Member
first_10 = ca_members[:10]     # Members, still chainable
if members.filter(state="WY"):
    print("Wyoming has members")
```

## Common gotchas

- **`filter()` vs `where()`** — `filter(**kwargs)` matches exact field values (with the state-code shortcut); `where(predicate)` runs your own function per member. Reach for `where()` once a filter needs logic beyond equality (date ranges, computed fields, etc.).
- **Lazy queries need `.execute()`** — a chain built with `lazy=True` doesn't run until you call `.execute()`. Forgetting it leaves you holding a query builder, not results.
- **`.query().to_list()` vs iterating directly** — both work; iterating the `Members` object directly (`for m in members`) is more idiomatic than calling `.query().to_list()` unless you specifically need a plain `list[Member]`.

## Reference

| Operation | Returns | Example |
|-----------|---------|---------|
| `filter(**kwargs)` | `Members` | `members.filter(state="CA")` |
| `where(predicate)` | `Members` | `members.query().where(lambda m: m.birthYear > 1980)` |
| `order_by(field, reverse=False)` | `Members` | `members.order_by("lastName")` |
| `limit(n)` / `skip(n)` | `Members` | `members.limit(10)`, `members.skip(20)` |
| `by_state(state)` / `by_chamber(chamber)` | `Members` | `members.by_state("CA")` |
| `democrats()` / `republicans()` / `current()` | `Members` | `members.democrats()` |
| `group_by(field)` | `dict[Any, Members]` | `members.group_by("state")` |
| `first()` | `Member \| None` | `members.first()` |
| `count()` | `int` | `members.query().count()` |
| `to_list()` | `list[Member]` | `members.query().to_list()` |
| `[index]` / `[slice]` | `Member` / `Members` | `members[0]`, `members[:10]` |
