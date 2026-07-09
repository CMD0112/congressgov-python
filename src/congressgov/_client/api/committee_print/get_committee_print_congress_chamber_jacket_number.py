from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_print_detail import CommitteePrintDetail
from ...models.get_committee_print_congress_chamber_jacket_number_chamber import (
    GetCommitteePrintCongressChamberJacketNumberChamber,
)
from ...models.get_committee_print_congress_chamber_jacket_number_format import (
    GetCommitteePrintCongressChamberJacketNumberFormat,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    chamber: GetCommitteePrintCongressChamberJacketNumberChamber,
    jacket_number: int,
    *,
    format_: Union[
        Unset, GetCommitteePrintCongressChamberJacketNumberFormat
    ] = GetCommitteePrintCongressChamberJacketNumberFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteePrintCongressChamberJacketNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteePrintCongressChamberJacketNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee-print/{congress}/{chamber}/{jacket_number}".format(
            congress=congress,
            chamber=chamber,
            jacket_number=jacket_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CommitteePrintDetail]]:
    if response.status_code == 200:
        response_200 = CommitteePrintDetail.from_dict(response.json())

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
) -> Response[Union[Any, CommitteePrintDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    chamber: GetCommitteePrintCongressChamberJacketNumberChamber,
    jacket_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteePrintCongressChamberJacketNumberFormat
    ] = GetCommitteePrintCongressChamberJacketNumberFormat.XML,
) -> Response[Union[Any, CommitteePrintDetail]]:
    """Returns detailed information for a specified committee print.

     Returns detailed information for a specified committee print.

    Args:
        congress (int):
        chamber (GetCommitteePrintCongressChamberJacketNumberChamber):
        jacket_number (int):
        format_ (Union[Unset, GetCommitteePrintCongressChamberJacketNumberFormat]):  Default:
            GetCommitteePrintCongressChamberJacketNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteePrintDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        jacket_number=jacket_number,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    chamber: GetCommitteePrintCongressChamberJacketNumberChamber,
    jacket_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteePrintCongressChamberJacketNumberFormat
    ] = GetCommitteePrintCongressChamberJacketNumberFormat.XML,
) -> Optional[Union[Any, CommitteePrintDetail]]:
    """Returns detailed information for a specified committee print.

     Returns detailed information for a specified committee print.

    Args:
        congress (int):
        chamber (GetCommitteePrintCongressChamberJacketNumberChamber):
        jacket_number (int):
        format_ (Union[Unset, GetCommitteePrintCongressChamberJacketNumberFormat]):  Default:
            GetCommitteePrintCongressChamberJacketNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteePrintDetail]
    """

    return sync_detailed(
        congress=congress,
        chamber=chamber,
        jacket_number=jacket_number,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    chamber: GetCommitteePrintCongressChamberJacketNumberChamber,
    jacket_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteePrintCongressChamberJacketNumberFormat
    ] = GetCommitteePrintCongressChamberJacketNumberFormat.XML,
) -> Response[Union[Any, CommitteePrintDetail]]:
    """Returns detailed information for a specified committee print.

     Returns detailed information for a specified committee print.

    Args:
        congress (int):
        chamber (GetCommitteePrintCongressChamberJacketNumberChamber):
        jacket_number (int):
        format_ (Union[Unset, GetCommitteePrintCongressChamberJacketNumberFormat]):  Default:
            GetCommitteePrintCongressChamberJacketNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CommitteePrintDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        chamber=chamber,
        jacket_number=jacket_number,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    chamber: GetCommitteePrintCongressChamberJacketNumberChamber,
    jacket_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteePrintCongressChamberJacketNumberFormat
    ] = GetCommitteePrintCongressChamberJacketNumberFormat.XML,
) -> Optional[Union[Any, CommitteePrintDetail]]:
    """Returns detailed information for a specified committee print.

     Returns detailed information for a specified committee print.

    Args:
        congress (int):
        chamber (GetCommitteePrintCongressChamberJacketNumberChamber):
        jacket_number (int):
        format_ (Union[Unset, GetCommitteePrintCongressChamberJacketNumberFormat]):  Default:
            GetCommitteePrintCongressChamberJacketNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CommitteePrintDetail]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            chamber=chamber,
            jacket_number=jacket_number,
            client=client,
            format_=format_,
        )
    ).parsed
