from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    session: int,
    *,
    format_: Union[Unset, str] = UNSET,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["format"] = format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/house-vote/{congress}/{session}".format(
            congress=congress,
            session=session,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if response.status_code == 200:
        return None
    if response.status_code == 400:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    session: int,
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = UNSET,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Any]:
    r"""Returns House of Representatives roll call vote data from the API filtered by the specified Congress
    and session. This endpoint is currently in beta.

     GET /house-vote/:congress/:session

    **Example Request**

    https://api.congress.gov/v3/house-vote/119/1?api_key=[INSERT_KEY]

    **Example Response**

        {
            \"houseRollCallVotes\": [
                {
                   \"congress\": 119,
                   \"identifier\": 1191202517,
                   \"legislationNumber\": \"30\",
                   \"legislationType\": \"HR\",
                   \"legislationUrl\": \"https://congress.gov/bill/119/house-bill/30\",
                   \"result\": \"Passed\",
                   \"rollCallNumber\": 17,
                   \"sessionNumber\": 1,
                   \"sourceDataURL\": \"https://clerk.house.gov/evs/2025/roll017.xml\",
                   \"startDate\": \"2025-01-16T11:00:00-05:00\",
                   \"updateDate\": \"2025-04-18T08:44:47-04:00\",
                   \"url\": \"https://api.congress.gov/v3/house-vote/119/1/17\",
                   \"voteType\": \"Yea-and-Nay\"
                },
            ],
         }

    Args:
        congress (int):
        session (int):
        format_ (Union[Unset, str]):
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        congress=congress,
        session=session,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    congress: int,
    session: int,
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = UNSET,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Any]:
    r"""Returns House of Representatives roll call vote data from the API filtered by the specified Congress
    and session. This endpoint is currently in beta.

     GET /house-vote/:congress/:session

    **Example Request**

    https://api.congress.gov/v3/house-vote/119/1?api_key=[INSERT_KEY]

    **Example Response**

        {
            \"houseRollCallVotes\": [
                {
                   \"congress\": 119,
                   \"identifier\": 1191202517,
                   \"legislationNumber\": \"30\",
                   \"legislationType\": \"HR\",
                   \"legislationUrl\": \"https://congress.gov/bill/119/house-bill/30\",
                   \"result\": \"Passed\",
                   \"rollCallNumber\": 17,
                   \"sessionNumber\": 1,
                   \"sourceDataURL\": \"https://clerk.house.gov/evs/2025/roll017.xml\",
                   \"startDate\": \"2025-01-16T11:00:00-05:00\",
                   \"updateDate\": \"2025-04-18T08:44:47-04:00\",
                   \"url\": \"https://api.congress.gov/v3/house-vote/119/1/17\",
                   \"voteType\": \"Yea-and-Nay\"
                },
            ],
         }

    Args:
        congress (int):
        session (int):
        format_ (Union[Unset, str]):
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        congress=congress,
        session=session,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
