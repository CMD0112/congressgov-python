from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_meeting_detail import CommitteeMeetingDetail
from ...models.get_committee_meeting_congress_chamber_event_id_chamber import (
    GetCommitteeMeetingCongressChamberEventIdChamber,
)
from ...models.get_committee_meeting_congress_chamber_event_id_format import (
    GetCommitteeMeetingCongressChamberEventIdFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    chamber: GetCommitteeMeetingCongressChamberEventIdChamber,
    event_id: str,
    *,
    format_: Union[
        Unset, GetCommitteeMeetingCongressChamberEventIdFormat
    ] = GetCommitteeMeetingCongressChamberEventIdFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeMeetingCongressChamberEventIdFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeMeetingCongressChamberEventIdFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee-meeting/{congress}/{chamber}/{event_id}".format(
            congress=congress,
            chamber=chamber,
            event_id=event_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CommitteeMeetingDetail]]:
    if response.status_code == 200:
        response_200 = CommitteeMeetingDetail.from_dict(response.json())

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
) -> Response[Union[Any, CommitteeMeetingDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    chamber: GetCommitteeMeetingCongressChamberEventIdChamber,
    event_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeMeetingCongressChamberEventIdFormat
    ] = GetCommitteeMeetingCongressChamberEventIdFormat.XML,
) -> Response[Union[Any, CommitteeMeetingDetail]]:
    """Returns detailed information for a specified committee meeting.

     Returns detailed information for a specified committee meeting.

    Args:
        congress (int):
        chamber (GetCommitteeMeetingCongressChamberEventIdChamber):
        event_id (str):
        format_ (Union[Unset, GetCommitteeMeetingCongressChamberEventIdFormat]):  Default:
            GetCommitteeMeetingCongressChamberEventIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeMeetingDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        event_id=event_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    chamber: GetCommitteeMeetingCongressChamberEventIdChamber,
    event_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeMeetingCongressChamberEventIdFormat
    ] = GetCommitteeMeetingCongressChamberEventIdFormat.XML,
) -> Optional[Union[Any, CommitteeMeetingDetail]]:
    """Returns detailed information for a specified committee meeting.

     Returns detailed information for a specified committee meeting.

    Args:
        congress (int):
        chamber (GetCommitteeMeetingCongressChamberEventIdChamber):
        event_id (str):
        format_ (Union[Unset, GetCommitteeMeetingCongressChamberEventIdFormat]):  Default:
            GetCommitteeMeetingCongressChamberEventIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeMeetingDetail]
    """

    return sync_detailed(
        congress=congress,
        chamber=chamber,
        event_id=event_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    chamber: GetCommitteeMeetingCongressChamberEventIdChamber,
    event_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeMeetingCongressChamberEventIdFormat
    ] = GetCommitteeMeetingCongressChamberEventIdFormat.XML,
) -> Response[Union[Any, CommitteeMeetingDetail]]:
    """Returns detailed information for a specified committee meeting.

     Returns detailed information for a specified committee meeting.

    Args:
        congress (int):
        chamber (GetCommitteeMeetingCongressChamberEventIdChamber):
        event_id (str):
        format_ (Union[Unset, GetCommitteeMeetingCongressChamberEventIdFormat]):  Default:
            GetCommitteeMeetingCongressChamberEventIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeMeetingDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        event_id=event_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    chamber: GetCommitteeMeetingCongressChamberEventIdChamber,
    event_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeMeetingCongressChamberEventIdFormat
    ] = GetCommitteeMeetingCongressChamberEventIdFormat.XML,
) -> Optional[Union[Any, CommitteeMeetingDetail]]:
    """Returns detailed information for a specified committee meeting.

     Returns detailed information for a specified committee meeting.

    Args:
        congress (int):
        chamber (GetCommitteeMeetingCongressChamberEventIdChamber):
        event_id (str):
        format_ (Union[Unset, GetCommitteeMeetingCongressChamberEventIdFormat]):  Default:
            GetCommitteeMeetingCongressChamberEventIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeMeetingDetail]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            chamber=chamber,
            event_id=event_id,
            client=client,
            format_=format_,
        )
    ).parsed
