from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_senate_communication import CommitteeSenateCommunication
from ...models.get_committee_chamber_committee_code_senate_communication_format import (
    GetCommitteeChamberCommitteeCodeSenateCommunicationFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    chamber: str,
    committee_code: str,
    *,
    format_: Union[
        Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat
    ] = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee/{chamber}/{committee_code}/senate-communication".format(
            chamber=chamber,
            committee_code=committee_code,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CommitteeSenateCommunication]]:
    if response.status_code == 200:
        response_200 = CommitteeSenateCommunication.from_dict(response.json())

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
) -> Response[Union[Any, CommitteeSenateCommunication]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chamber: str,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat
    ] = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, CommitteeSenateCommunication]]:
    """Returns the list of Senate communications associated with a specified congressional committee.

     Returns the list of Senate communications associated with a specified congressional committee.

    Args:
        chamber (str):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat]):
            Default: GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeSenateCommunication]]
    """

    kwargs = _get_kwargs(
        chamber=chamber,
        committee_code=committee_code,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chamber: str,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat
    ] = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, CommitteeSenateCommunication]]:
    """Returns the list of Senate communications associated with a specified congressional committee.

     Returns the list of Senate communications associated with a specified congressional committee.

    Args:
        chamber (str):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat]):
            Default: GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeSenateCommunication]
    """

    return sync_detailed(
        chamber=chamber,
        committee_code=committee_code,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    chamber: str,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat
    ] = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, CommitteeSenateCommunication]]:
    """Returns the list of Senate communications associated with a specified congressional committee.

     Returns the list of Senate communications associated with a specified congressional committee.

    Args:
        chamber (str):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat]):
            Default: GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeSenateCommunication]]
    """

    kwargs = _get_kwargs(
        chamber=chamber,
        committee_code=committee_code,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chamber: str,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat
    ] = GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, CommitteeSenateCommunication]]:
    """Returns the list of Senate communications associated with a specified congressional committee.

     Returns the list of Senate communications associated with a specified congressional committee.

    Args:
        chamber (str):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeChamberCommitteeCodeSenateCommunicationFormat]):
            Default: GetCommitteeChamberCommitteeCodeSenateCommunicationFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeSenateCommunication]
    """

    return (
        await asyncio_detailed(
            chamber=chamber,
            committee_code=committee_code,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
    ).parsed
