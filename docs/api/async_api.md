# Async API

Every sync service has an `Async*` counterpart with the same method surface, importable from
`congressgov.async_api`:

```python
from congressgov.async_api import AsyncBill

bill = await AsyncBill(client=async_client).get(congress=118, bill_type="hr", bill_number=1)
```

::: congressgov.async_api
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_submodules: false
