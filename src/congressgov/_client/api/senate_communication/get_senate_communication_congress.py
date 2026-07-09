from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_senate_communication_congress_format import GetSenateCommunicationCongressFormat
from ...models.senate_communications import SenateCommunications
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    *,
    format_: Union[Unset, GetSenateCommunicationCongressFormat] = GetSenateCommunicationCongressFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetSenateCommunicationCongressFormat.JSON
    elif isinstance(format_, str):
        format_ = GetSenateCommunicationCongressFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/senate-communication/{congress}".format(
            congress=congress,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SenateCommunications]]:
    if response.status_code == 200:
        response_200 = SenateCommunications.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SenateCommunications]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetSenateCommunicationCongressFormat] = GetSenateCommunicationCongressFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, SenateCommunications]]:
    """Returns a list of Senate communications filtered by the specified congress.

     Returns a list of Senate communications filtered by the specified congress.

    Args:
        congress (int):
        format_ (Union[Unset, GetSenateCommunicationCongressFormat]):  Default:
            GetSenateCommunicationCongressFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SenateCommunications]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetSenateCommunicationCongressFormat] = GetSenateCommunicationCongressFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, SenateCommunications]]:
    """Returns a list of Senate communications filtered by the specified congress.

     Returns a list of Senate communications filtered by the specified congress.

    Args:
        congress (int):
        format_ (Union[Unset, GetSenateCommunicationCongressFormat]):  Default:
            GetSenateCommunicationCongressFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SenateCommunications]
    """

    return sync_detailed(
        congress=congress,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    congress: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetSenateCommunicationCongressFormat] = GetSenateCommunicationCongressFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, SenateCommunications]]:
    """Returns a list of Senate communications filtered by the specified congress.

     Returns a list of Senate communications filtered by the specified congress.

    Args:
        congress (int):
        format_ (Union[Unset, GetSenateCommunicationCongressFormat]):  Default:
            GetSenateCommunicationCongressFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SenateCommunications]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetSenateCommunicationCongressFormat] = GetSenateCommunicationCongressFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, SenateCommunications]]:
    """Returns a list of Senate communications filtered by the specified congress.

     Returns a list of Senate communications filtered by the specified congress.

    Args:
        congress (int):
        format_ (Union[Unset, GetSenateCommunicationCongressFormat]):  Default:
            GetSenateCommunicationCongressFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SenateCommunications]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
    ).parsed
