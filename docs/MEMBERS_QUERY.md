# Members Query System Usage Guide

## Overview

The `Members` class provides a powerful query interface that returns `Members` objects, allowing for chainable operations and consistent API.

**Enum shortcuts**: Query with state codes (e.g., `"CA"`) that automatically match full names (e.g., `"California"`).

## Key Features

- **Returns `Members` objects**: All query operations return `Members` objects, not plain lists
- **Eager by default**: Most operations execute immediately
- **Lazy when needed**: Use `lazy=True` for complex chaining
- **Chainable**: Query results can be further filtered
- **Enum shortcuts**: Use state codes ("CA") or full names ("California") interchangeably
- **Python protocols**: Supports iteration, indexing, slicing, `len()`, and truthiness

---

## Enum Shortcut Feature

The query system automatically expands state codes using the `StateCode` enum:

```python
# Query with state code
ca_members = members.filter(state="CA")  # Matches state="California"

# Query with full state name
ca_members = members.filter(state="California")  # Also works

# Both queries return identical results!

# Case insensitive too
ca_members = members.filter(state="ca")
ca_members = members.filter(state="california")
```

**How it works**: The `StateCode` enum defines `CA = "California"`. The query builder automatically tries both the code and the full name when matching.

---

## Basic Usage

### Simple Filtering (Eager)

```python
# Get members from California (returns Members object)
ca_members = members.filter(state="CA")

# Access the underlying list if needed
ca_list = ca_members.query().to_list()

# Or iterate directly
for member in ca_members:
    print(member.firstName, member.lastName)

# Check count
print(f"Found {len(ca_members)} members")
```

### Multiple Filters

```python
# Filter by multiple criteria
ca_dems = members.filter(state="CA", partyName="Democratic")

# Further filter the results (chaining on Members objects)
current_ca_dems = ca_dems.filter(currentMember=True)
```

### Convenience Methods

```python
# All return Members objects
ca_members = members.by_state("CA")
democrats = members.democrats()
republicans = members.republicans()
current = members.current()
house = members.by_chamber("House of Representatives")
senate = members.by_chamber("Senate")
```

---

## Advanced Usage

### Lazy Chaining (for complex queries)

```python
# Build complex query chain
results = (members
    .filter(state="CA", lazy=True)
    .order_by("lastName", lazy=True)
    .limit(10)
    .execute())  # Returns Members object

# Continue querying the results
top_5 = results.limit(5)  # Returns Members object with 5 members
```

### Custom Predicates

```python
# Filter with custom function
young_members = members.query().where(
    lambda m: m.birthYear and m.birthYear > 1980
)  # Returns Members object

# Lazy version
young_query = members.query().where(
    lambda m: m.birthYear and m.birthYear > 1980,
    lazy=True
)
sorted_young = young_query.order_by("birthYear").execute()
```

### Grouping

```python
# Group by state (returns dict of Members objects)
by_state = members.group_by("state")

# Each value is a Members object
ca_members = by_state["California"]
ny_members = by_state["New York"]

# Further operations on grouped results
ca_democrats = ca_members.democrats()
print(f"CA has {len(ca_democrats)} Democrats")

# Group and analyze
by_party = members.group_by("partyName")
for party, party_members in by_party.items():
    print(f"{party}: {len(party_members)} members")
```

---

## Working with Results

### Iteration

```python
# Direct iteration
for member in members.filter(state="NY"):
    print(f"{member.firstName} {member.lastName}")
```

### Indexing and Slicing

```python
# Get first member
first = ca_members[0]  # Returns Member

# Slice (returns Members object)
first_10 = ca_members[:10]  # Returns Members with 10 members
next_10 = ca_members[10:20]  # Returns Members with next 10

# Continue querying sliced results
first_10_dems = first_10.democrats()
```

### Length and Truthiness

```python
# Get count
count = len(members.filter(state="CA"))

# Check if results exist
if members.filter(state="WY"):
    print("Wyoming has members")
```

### Accessing Data

```python
# Get Members object
ca_members = members.by_state("CA")

# Access underlying list
member_list = ca_members.query().to_list()  # list[Member]

# Or access the Pydantic field
member_list = ca_members.members  # list[Member] | None

# Iterate directly (most Pythonic)
for member in ca_members:
    print(member.firstName)
```

---

## Query Builder Pattern

### Starting a Query

```python
# Get query builder
query = members.query()

# Build and execute
results = (query
    .filter(state="CA", lazy=True)
    .order_by("lastName", lazy=True)
    .execute())  # Returns Members object
```

### Reusable Queries

```python
# Create base query
current_dems = members.filter(partyName="Democratic", currentMember=True, lazy=True)

# Reuse with different states
ca_current_dems = current_dems.filter(state="CA", lazy=True).execute()
ny_current_dems = current_dems.filter(state="NY", lazy=True).execute()
```

---

## Sorting and Pagination

### Sorting

```python
# Sort (returns Members object)
sorted_members = members.filter(state="CA").order_by("lastName")

# Sort descending
newest = members.order_by("birthYear", reverse=True)
```

### Pagination

```python
# Limit results
top_20 = members.filter(state="CA").limit(20)

# Skip and limit (pagination)
page_2 = members.filter(state="CA").skip(20).limit(20)

# Or use slicing
page_1 = ca_members[:20]
page_2 = ca_members[20:40]
```

---

## Complex Queries

### Multi-Stage Filtering

```python
# Filter in stages
all_members = members
current = all_members.current()
current_house = current.by_chamber("House of Representatives")
swing_state = current_house.filter(state="PA")
freshmen = swing_state.query().where(
    lambda m: m.terms and m.terms.item and
              max(m.terms.item, key=lambda t: t.startYear or 0).startYear >= 2023
)

# All intermediate results are Members objects
print(f"Found {len(freshmen)} freshmen from PA")
```

### Statistical Analysis

```python
# Get all current members
current = members.current()

# Group by party
by_party = current.group_by("partyName")

# Analyze each party
for party, party_members in by_party.items():
    by_state = party_members.group_by("state")
    print(f"{party}:")
    for state, state_members in by_state.items():
        print(f"  {state}: {len(state_members)}")
```

---

## Performance Tips

### Eager vs Lazy

```python
# Eager (executes immediately) - Use for simple queries
results = members.filter(state="CA")

# Lazy (delays execution) - Use for complex chains
results = (members
    .filter(state="CA", lazy=True)
    .filter(partyName="Democratic", lazy=True)
    .order_by("lastName", lazy=True)
    .limit(10)
    .execute())
```

### Efficient Filtering

```python
# Good: Filter once with multiple criteria
ca_current_dems = members.filter(
    state="CA",
    partyName="Democratic",
    currentMember=True
)

# Less efficient: Multiple separate filters (creates intermediate Members objects)
result = members.filter(state="CA")
result = result.filter(partyName="Democratic")
result = result.filter(currentMember=True)

# Better: Use lazy chaining for multiple filters
result = (members
    .filter(state="CA", lazy=True)
    .filter(partyName="Democratic", lazy=True)
    .filter(currentMember=True)
    .execute())
```

---

## Type Annotations

```python
from congressgov.models import Members, Member

def get_california_democrats(all_members: Members) -> Members:
    """Filter to CA Democrats."""
    return all_members.filter(state="CA", partyName="Democratic")

def get_first_member(members: Members) -> Member | None:
    """Get first member."""
    return members.first()

def count_by_state(members: Members) -> dict[str, int]:
    """Count members by state."""
    by_state = members.group_by("state")
    return {state: len(state_members) for state, state_members in by_state.items()}
```

---

## Summary

| Operation | Returns | Example |
|-----------|---------|---------|
| `filter(**kwargs)` | `Members` | `members.filter(state="CA")` |
| `where(predicate)` | `Members` | `members.query().where(lambda m: m.birthYear > 1980)` |
| `order_by(field)` | `Members` | `members.order_by("lastName")` |
| `limit(n)` | `Members` | `members.limit(10)` |
| `skip(n)` | `Members` | `members.skip(20)` |
| `by_state(state)` | `Members` | `members.by_state("CA")` |
| `by_party(party)` | `Members` | `members.by_party("Democratic")` |
| `democrats()` | `Members` | `members.democrats()` |
| `republicans()` | `Members` | `members.republicans()` |
| `current()` | `Members` | `members.current()` |
| `group_by(field)` | `dict[Any, Members]` | `members.group_by("state")` |
| `first()` | `Member \| None` | `members.first()` |
| `count()` | `int` | `members.query().count()` |
| `to_list()` | `list[Member]` | `members.query().to_list()` |
| `[index]` | `Member` | `members[0]` |
| `[slice]` | `Members` | `members[:10]` |
