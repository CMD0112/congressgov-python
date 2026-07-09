from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.congressional_record import CongressionalRecord
from ...models.get_congressional_record_format import GetCongressionalRecordFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    format_: Union[Unset, GetCongressionalRecordFormat] = GetCongressionalRecordFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    y: Union[Unset, int] = UNSET,
    m: Union[Unset, int] = UNSET,
    d: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCongressionalRecordFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCongressionalRecordFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params["y"] = y

    params["m"] = m

    params["d"] = d

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/congressional-record",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CongressionalRecord]]:
    if response.status_code == 200:
        response_200 = CongressionalRecord.from_dict(response.json())

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
) -> Response[Union[Any, CongressionalRecord]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCongressionalRecordFormat] = GetCongressionalRecordFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    y: Union[Unset, int] = UNSET,
    m: Union[Unset, int] = UNSET,
    d: Union[Unset, int] = UNSET,
) -> Response[Union[Any, CongressionalRecord]]:
    """Returns a list of congressional record issues sorted by most recent.

     Returns a list of congressional record issues sorted by most recent.

    Args:
        format_ (Union[Unset, GetCongressionalRecordFormat]):  Default:
            GetCongressionalRecordFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        y (Union[Unset, int]):
        m (Union[Unset, int]):
        d (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CongressionalRecord]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        offset=offset,
        limit=limit,
        y=y,
        m=m,
        d=d,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCongressionalRecordFormat] = GetCongressionalRecordFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    y: Union[Unset, int] = UNSET,
    m: Union[Unset, int] = UNSET,
    d: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, CongressionalRecord]]:
    """Returns a list of congressional record issues sorted by most recent.

     Returns a list of congressional record issues sorted by most recent.

    Args:
        format_ (Union[Unset, GetCongressionalRecordFormat]):  Default:
            GetCongressionalRecordFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        y (Union[Unset, int]):
        m (Union[Unset, int]):
        d (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CongressionalRecord]
    """

    return sync_detailed(
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
        y=y,
        m=m,
        d=d,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCongressionalRecordFormat] = GetCongressionalRecordFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    y: Union[Unset, int] = UNSET,
    m: Union[Unset, int] = UNSET,
    d: Union[Unset, int] = UNSET,
) -> Response[Union[Any, CongressionalRecord]]:
    """Returns a list of congressional record issues sorted by most recent.

     Returns a list of congressional record issues sorted by most recent.

    Args:
        format_ (Union[Unset, GetCongressionalRecordFormat]):  Default:
            GetCongressionalRecordFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        y (Union[Unset, int]):
        m (Union[Unset, int]):
        d (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CongressionalRecord]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        offset=offset,
        limit=limit,
        y=y,
        m=m,
        d=d,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCongressionalRecordFormat] = GetCongressionalRecordFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    y: Union[Unset, int] = UNSET,
    m: Union[Unset, int] = UNSET,
    d: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, CongressionalRecord]]:
    """Returns a list of congressional record issues sorted by most recent.

     Returns a list of congressional record issues sorted by most recent.

    Args:
        format_ (Union[Unset, GetCongressionalRecordFormat]):  Default:
            GetCongressionalRecordFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        y (Union[Unset, int]):
        m (Union[Unset, int]):
        d (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CongressionalRecord]
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
            y=y,
            m=m,
            d=d,
        )
    ).parsed
