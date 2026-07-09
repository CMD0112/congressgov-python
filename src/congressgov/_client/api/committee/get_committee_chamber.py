from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committees import Committees
from ...models.get_committee_chamber_chamber import GetCommitteeChamberChamber
from ...models.get_committee_chamber_format import GetCommitteeChamberFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    chamber: GetCommitteeChamberChamber,
    *,
    format_: Union[Unset, GetCommitteeChamberFormat] = GetCommitteeChamberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeChamberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeChamberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params["fromDateTime"] = from_date_time

    params["toDateTime"] = to_date_time

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee/{chamber}".format(
            chamber=chamber,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Committees]]:
    if response.status_code == 200:
        response_200 = Committees.from_dict(response.json())

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
) -> Response[Union[Any, Committees]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chamber: GetCommitteeChamberChamber,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeChamberFormat] = GetCommitteeChamberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Response[Union[Any, Committees]]:
    """Returns a list of congressional committees filtered by the specified chamber.

     Returns a list of congressional committees filtered by the specified chamber.

    Args:
        chamber (GetCommitteeChamberChamber):
        format_ (Union[Unset, GetCommitteeChamberFormat]):  Default:
            GetCommitteeChamberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Committees]]
    """

    kwargs = _get_kwargs(
        chamber=chamber,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chamber: GetCommitteeChamberChamber,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeChamberFormat] = GetCommitteeChamberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, Committees]]:
    """Returns a list of congressional committees filtered by the specified chamber.

     Returns a list of congressional committees filtered by the specified chamber.

    Args:
        chamber (GetCommitteeChamberChamber):
        format_ (Union[Unset, GetCommitteeChamberFormat]):  Default:
            GetCommitteeChamberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Committees]
    """

    return sync_detailed(
        chamber=chamber,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    ).parsed


async def asyncio_detailed(
    chamber: GetCommitteeChamberChamber,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeChamberFormat] = GetCommitteeChamberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Response[Union[Any, Committees]]:
    """Returns a list of congressional committees filtered by the specified chamber.

     Returns a list of congressional committees filtered by the specified chamber.

    Args:
        chamber (GetCommitteeChamberChamber):
        format_ (Union[Unset, GetCommitteeChamberFormat]):  Default:
            GetCommitteeChamberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Committees]]
    """

    kwargs = _get_kwargs(
        chamber=chamber,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chamber: GetCommitteeChamberChamber,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeChamberFormat] = GetCommitteeChamberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, Committees]]:
    """Returns a list of congressional committees filtered by the specified chamber.

     Returns a list of congressional committees filtered by the specified chamber.

    Args:
        chamber (GetCommitteeChamberChamber):
        format_ (Union[Unset, GetCommitteeChamberFormat]):  Default:
            GetCommitteeChamberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Committees]
    """

    return (
        await asyncio_detailed(
            chamber=chamber,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
        )
    ).parsed
