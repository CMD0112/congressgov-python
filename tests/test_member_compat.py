"""Member client compat import smoke tests."""


def test_member_sync_and_async_exports() -> None:
    from congressgov._client.api import member as member_api

    assert callable(member_api.member_details_sync)
    assert callable(member_api.member_sponsorship_list_async)
    assert callable(member_api.member_cosponsorship_list_async)
