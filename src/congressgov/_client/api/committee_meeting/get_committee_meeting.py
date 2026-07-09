from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_meetings import CommitteeMeetings
from ...models.get_committee_meeting_format import GetCommitteeMeetingFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    format_: Union[Unset, GetCommitteeMeetingFormat] = GetCommitteeMeetingFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeMeetingFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeMeetingFormat(format_.lower())
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
        "url": "/committee-meeting",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["CommitteeMeetings"]]]:
    if response.status_code == 200:
        # Congress.gov returns an envelope dict; congressgov.services parses
        # response.content via ApiEnvelope. Generated list iteration fails.
        return None
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, list["CommitteeMeetings"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeMeetingFormat] = GetCommitteeMeetingFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["CommitteeMeetings"]]]:
    """Returns a list of committee meetings.

     Returns a list of committee meetings.

    Args:
        format_ (Union[Unset, GetCommitteeMeetingFormat]):  Default:
            GetCommitteeMeetingFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['CommitteeMeetings']]]
    """

    kwargs = _get_kwargs(
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
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeMeetingFormat] = GetCommitteeMeetingFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["CommitteeMeetings"]]]:
    """Returns a list of committee meetings.

     Returns a list of committee meetings.

    Args:
        format_ (Union[Unset, GetCommitteeMeetingFormat]):  Default:
            GetCommitteeMeetingFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['CommitteeMeetings']]
    """

    return sync_detailed(
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeMeetingFormat] = GetCommitteeMeetingFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["CommitteeMeetings"]]]:
    """Returns a list of committee meetings.

     Returns a list of committee meetings.

    Args:
        format_ (Union[Unset, GetCommitteeMeetingFormat]):  Default:
            GetCommitteeMeetingFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['CommitteeMeetings']]]
    """

    kwargs = _get_kwargs(
        format_=format_,
        offset=offset,
        limit=limit,
        from_date_time=from_date_time,
        to_date_time=to_date_time,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCommitteeMeetingFormat] = GetCommitteeMeetingFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    from_date_time: Union[Unset, str] = UNSET,
    to_date_time: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["CommitteeMeetings"]]]:
    """Returns a list of committee meetings.

     Returns a list of committee meetings.

    Args:
        format_ (Union[Unset, GetCommitteeMeetingFormat]):  Default:
            GetCommitteeMeetingFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):
        from_date_time (Union[Unset, str]):
        to_date_time (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['CommitteeMeetings']]
    """

    return (
        await asyncio_detailed(
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
            from_date_time=from_date_time,
            to_date_time=to_date_time,
        )
    ).parsed
