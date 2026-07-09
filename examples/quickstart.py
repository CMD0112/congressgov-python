"""Minimal congressgov quickstart — requires CONGRESS_API_KEY in the environment."""

from congressgov import Bill, get_attached_store, get_client_from_env, print_store_stats


def main() -> None:
    client = get_client_from_env()
    bill_service = Bill(client=client)
    bill = bill_service.get(congress=118, bill_type="hr", bill_number=1)
    print(bill.title)
    actions = bill.get_actions()
    print(f"Actions: {len(actions) if actions else 0}")

    store = get_attached_store(client)
    if store is not None:
        print_store_stats(store)


if __name__ == "__main__":
    main()
