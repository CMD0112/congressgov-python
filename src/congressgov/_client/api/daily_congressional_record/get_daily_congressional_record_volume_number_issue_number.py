from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.daily_congressional_record_issue import DailyCongressionalRecordIssue
from ...models.get_daily_congressional_record_volume_number_issue_number_format import (
    GetDailyCongressionalRecordVolumeNumberIssueNumberFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    volume_number: int,
    issue_number: int,
    *,
    format_: Union[
        Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat
    ] = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/daily-congressional-record/{volume_number}/{issue_number}".format(
            volume_number=volume_number,
            issue_number=issue_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DailyCongressionalRecordIssue]]:
    if response.status_code == 200:
        response_200 = DailyCongressionalRecordIssue.from_dict(response.json())

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
) -> Response[Union[Any, DailyCongressionalRecordIssue]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    volume_number: int,
    issue_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat
    ] = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, DailyCongressionalRecordIssue]]:
    """Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

     Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

    Args:
        volume_number (int):
        issue_number (int):
        format_ (Union[Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat]):
            Default: GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DailyCongressionalRecordIssue]]
    """

    kwargs = _get_kwargs(
        volume_number=volume_number,
        issue_number=issue_number,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    volume_number: int,
    issue_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat
    ] = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, DailyCongressionalRecordIssue]]:
    """Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

     Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

    Args:
        volume_number (int):
        issue_number (int):
        format_ (Union[Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat]):
            Default: GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DailyCongressionalRecordIssue]
    """

    return sync_detailed(
        volume_number=volume_number,
        issue_number=issue_number,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    volume_number: int,
    issue_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat
    ] = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, DailyCongressionalRecordIssue]]:
    """Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

     Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

    Args:
        volume_number (int):
        issue_number (int):
        format_ (Union[Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat]):
            Default: GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DailyCongressionalRecordIssue]]
    """

    kwargs = _get_kwargs(
        volume_number=volume_number,
        issue_number=issue_number,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume_number: int,
    issue_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat
    ] = GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, DailyCongressionalRecordIssue]]:
    """Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

     Returns a list of daily Congressional Records filtered by the specified volume number and specified
    issue number.

    Args:
        volume_number (int):
        issue_number (int):
        format_ (Union[Unset, GetDailyCongressionalRecordVolumeNumberIssueNumberFormat]):
            Default: GetDailyCongressionalRecordVolumeNumberIssueNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DailyCongressionalRecordIssue]
    """

    return (
        await asyncio_detailed(
            volume_number=volume_number,
            issue_number=issue_number,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
    ).parsed
