"""Async congressgov quickstart — requires CONGRESS_API_KEY in the environment."""

import asyncio

from congressgov import get_attached_store, get_client_from_env, print_store_stats
from congressgov.async_api import AsyncBill


async def main() -> None:
    client = get_client_from_env()
    bill = await AsyncBill(client=client).get(
        congress=118, bill_type="hr", bill_number=1
    )
    print(bill.title)
    actions = await bill.get_actions_async()
    print(f"Actions: {len(actions) if actions else 0}")

    store = get_attached_store(client)
    if store is not None:
        print_store_stats(store)


if __name__ == "__main__":
    asyncio.run(main())
