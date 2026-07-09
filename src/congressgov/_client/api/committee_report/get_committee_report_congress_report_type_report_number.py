from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.committee_reports_number_item import CommitteeReportsNumberItem
from ...models.get_committee_report_congress_report_type_report_number_format import (
    GetCommitteeReportCongressReportTypeReportNumberFormat,
)
from ...models.get_committee_report_congress_report_type_report_number_report_type import (
    GetCommitteeReportCongressReportTypeReportNumberReportType,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberReportType,
    report_number: int,
    *,
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCommitteeReportCongressReportTypeReportNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCommitteeReportCongressReportTypeReportNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/committee-report/{congress}/{report_type}/{report_number}".format(
            congress=congress,
            report_type=report_type,
            report_number=report_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["CommitteeReportsNumberItem"]]]:
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
) -> Response[Union[Any, list["CommitteeReportsNumberItem"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberFormat.XML,
) -> Response[Union[Any, list["CommitteeReportsNumberItem"]]]:
    """Returns detailed information for a specified committee report.

     Returns detailed information for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberFormat]):  Default:
            GetCommitteeReportCongressReportTypeReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['CommitteeReportsNumberItem']]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberFormat.XML,
) -> Optional[Union[Any, list["CommitteeReportsNumberItem"]]]:
    """Returns detailed information for a specified committee report.

     Returns detailed information for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberFormat]):  Default:
            GetCommitteeReportCongressReportTypeReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['CommitteeReportsNumberItem']]
    """

    return sync_detailed(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberFormat.XML,
) -> Response[Union[Any, list["CommitteeReportsNumberItem"]]]:
    """Returns detailed information for a specified committee report.

     Returns detailed information for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberFormat]):  Default:
            GetCommitteeReportCongressReportTypeReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['CommitteeReportsNumberItem']]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        report_type=report_type,
        report_number=report_number,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    report_type: GetCommitteeReportCongressReportTypeReportNumberReportType,
    report_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetCommitteeReportCongressReportTypeReportNumberFormat
    ] = GetCommitteeReportCongressReportTypeReportNumberFormat.XML,
) -> Optional[Union[Any, list["CommitteeReportsNumberItem"]]]:
    """Returns detailed information for a specified committee report.

     Returns detailed information for a specified committee report.

    Args:
        congress (int):
        report_type (GetCommitteeReportCongressReportTypeReportNumberReportType):
        report_number (int):
        format_ (Union[Unset, GetCommitteeReportCongressReportTypeReportNumberFormat]):  Default:
            GetCommitteeReportCongressReportTypeReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['CommitteeReportsNumberItem']]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            report_type=report_type,
            report_number=report_number,
            client=client,
            format_=format_,
        )
    ).parsed
