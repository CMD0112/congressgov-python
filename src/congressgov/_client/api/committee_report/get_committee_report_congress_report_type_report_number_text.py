from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committeereportsformats import Committeereportsformats
from ...models.get_committee_report_congress_report_type_report_number_text_format import (
    GetCommitteeReportCongressReportTypeReportNumberTextFormat,
)
from ...models.get_committee_report_congress_report_type_report_number_text_report_type import (
    GetCommitteeReportCongressReportTypeReportNumberTextReportType,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberTextReportType,
    report_number: int,
    *,
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeReportCongressReportTypeReportNumberTextFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeReportCongressReportTypeReportNumberTextFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee-report/{congress}/{report_type}/{report_number}/text".format(
            congress=congress,
            report_type=report_type,
            report_number=report_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["Committeereportsformats"]]]:
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
) -> Response[Union[Any, list["Committeereportsformats"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberTextReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, list["Committeereportsformats"]]]:
    """Returns the list of texts for a specified committee report.

     Returns the list of texts for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberTextReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat]):
            Default: GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Committeereportsformats']]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
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
    report_type: GetCommitteeReportCongressReportTypeReportNumberTextReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, list["Committeereportsformats"]]]:
    """Returns the list of texts for a specified committee report.

     Returns the list of texts for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberTextReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat]):
            Default: GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Committeereportsformats']]
    """

    return sync_detailed(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberTextReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, list["Committeereportsformats"]]]:
    """Returns the list of texts for a specified committee report.

     Returns the list of texts for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberTextReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat]):
            Default: GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Committeereportsformats']]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberTextReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, list["Committeereportsformats"]]]:
    """Returns the list of texts for a specified committee report.

     Returns the list of texts for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberTextReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberTextFormat]):
            Default: GetCommitteeReportCongressReportTypeReportNumberTextFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Committeereportsformats']]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            report_type=report_type,
            report_number=report_number,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
    ).parsed
