from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.crs_report_detail import CrsReportDetail
from ...models.get_crsreport_report_number_format import GetCrsreportReportNumberFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    report_number: str,
    *,
    format_: Union[Unset, GetCrsreportReportNumberFormat] = GetCrsreportReportNumberFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetCrsreportReportNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetCrsreportReportNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/crsreport/{report_number}".format(
            report_number=report_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CrsReportDetail]]:
    if response.status_code == 200:
        response_200 = CrsReportDetail.from_dict(response.json())

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
) -> Response[Union[Any, CrsReportDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    report_number: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCrsreportReportNumberFormat] = GetCrsreportReportNumberFormat.XML,
) -> Response[Union[Any, CrsReportDetail]]:
    """Returns Congressional Research Service (CRS) report data from the API

     Returns Congressional Research Service (CRS) report data from the API

    Args:
        report_number (str):
        format_ (Union[Unset, GetCrsreportReportNumberFormat]):  Default:
            GetCrsreportReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CrsReportDetail]]
    """

    kwargs = _get_kwargs(
        report_number=report_number,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_number: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCrsreportReportNumberFormat] = GetCrsreportReportNumberFormat.XML,
) -> Optional[Union[Any, CrsReportDetail]]:
    """Returns Congressional Research Service (CRS) report data from the API

     Returns Congressional Research Service (CRS) report data from the API

    Args:
        report_number (str):
        format_ (Union[Unset, GetCrsreportReportNumberFormat]):  Default:
            GetCrsreportReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CrsReportDetail]
    """

    return sync_detailed(
        report_number=report_number,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    report_number: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCrsreportReportNumberFormat] = GetCrsreportReportNumberFormat.XML,
) -> Response[Union[Any, CrsReportDetail]]:
    """Returns Congressional Research Service (CRS) report data from the API

     Returns Congressional Research Service (CRS) report data from the API

    Args:
        report_number (str):
        format_ (Union[Unset, GetCrsreportReportNumberFormat]):  Default:
            GetCrsreportReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CrsReportDetail]]
    """

    kwargs = _get_kwargs(
        report_number=report_number,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_number: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetCrsreportReportNumberFormat] = GetCrsreportReportNumberFormat.XML,
) -> Optional[Union[Any, CrsReportDetail]]:
    """Returns Congressional Research Service (CRS) report data from the API

     Returns Congressional Research Service (CRS) report data from the API

    Args:
        report_number (str):
        format_ (Union[Unset, GetCrsreportReportNumberFormat]):  Default:
            GetCrsreportReportNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CrsReportDetail]
    """

    return (
        await asyncio_detailed(
            report_number=report_number,
            client=client,
            format_=format_,
        )
    ).parsed
