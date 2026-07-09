from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_detail import CommitteeDetail
from ...models.get_committee_congress_chamber_committee_code_chamber import (
    GetCommitteeCongressChamberCommitteeCodeChamber,
)
from ...models.get_committee_congress_chamber_committee_code_format import (
    GetCommitteeCongressChamberCommitteeCodeFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    chamber: GetCommitteeCongressChamberCommitteeCodeChamber,
    committee_code: str,
    *,
    format_: Union[
        Unset, GetCommitteeCongressChamberCommitteeCodeFormat
    ] = GetCommitteeCongressChamberCommitteeCodeFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeCongressChamberCommitteeCodeFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeCongressChamberCommitteeCodeFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee/{congress}/{chamber}/{committee_code}".format(
            congress=congress,
            chamber=chamber,
            committee_code=committee_code,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CommitteeDetail]]:
    if response.status_code == 200:
        response_200 = CommitteeDetail.from_dict(response.json())

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
) -> Response[Union[Any, CommitteeDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    chamber: GetCommitteeCongressChamberCommitteeCodeChamber,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeCongressChamberCommitteeCodeFormat
    ] = GetCommitteeCongressChamberCommitteeCodeFormat.XML,
) -> Response[Union[Any, CommitteeDetail]]:
    """Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

     Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

    Args:
        congress (int):
        chamber (GetCommitteeCongressChamberCommitteeCodeChamber):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeCongressChamberCommitteeCodeFormat]):  Default:
            GetCommitteeCongressChamberCommitteeCodeFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        committee_code=committee_code,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    chamber: GetCommitteeCongressChamberCommitteeCodeChamber,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeCongressChamberCommitteeCodeFormat
    ] = GetCommitteeCongressChamberCommitteeCodeFormat.XML,
) -> Optional[Union[Any, CommitteeDetail]]:
    """Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

     Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

    Args:
        congress (int):
        chamber (GetCommitteeCongressChamberCommitteeCodeChamber):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeCongressChamberCommitteeCodeFormat]):  Default:
            GetCommitteeCongressChamberCommitteeCodeFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeDetail]
    """

    return sync_detailed(
        congress=congress,
        chamber=chamber,
        committee_code=committee_code,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    chamber: GetCommitteeCongressChamberCommitteeCodeChamber,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeCongressChamberCommitteeCodeFormat
    ] = GetCommitteeCongressChamberCommitteeCodeFormat.XML,
) -> Response[Union[Any, CommitteeDetail]]:
    """Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

     Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

    Args:
        congress (int):
        chamber (GetCommitteeCongressChamberCommitteeCodeChamber):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeCongressChamberCommitteeCodeFormat]):  Default:
            GetCommitteeCongressChamberCommitteeCodeFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteeDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        committee_code=committee_code,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    chamber: GetCommitteeCongressChamberCommitteeCodeChamber,
    committee_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeCongressChamberCommitteeCodeFormat
    ] = GetCommitteeCongressChamberCommitteeCodeFormat.XML,
) -> Optional[Union[Any, CommitteeDetail]]:
    """Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

     Returns detailed information for a specified congressional committee filtered by the specified
    Congress.

    Args:
        congress (int):
        chamber (GetCommitteeCongressChamberCommitteeCodeChamber):
        committee_code (str):
        format_ (Union[Unset, GetCommitteeCongressChamberCommitteeCodeFormat]):  Default:
            GetCommitteeCongressChamberCommitteeCodeFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteeDetail]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            chamber=chamber,
            committee_code=committee_code,
            client=client,
            format_=format_,
        )
    ).parsed
