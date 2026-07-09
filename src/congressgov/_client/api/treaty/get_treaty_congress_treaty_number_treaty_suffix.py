from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_treaty_congress_treaty_number_treaty_suffix_format import (
    GetTreatyCongressTreatyNumberTreatySuffixFormat,
)
from ...models.treaty_detail import TreatyDetail
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    treaty_number: int,
    treaty_suffix: str,
    *,
    format_: Union[
        Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat
    ] = GetTreatyCongressTreatyNumberTreatySuffixFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetTreatyCongressTreatyNumberTreatySuffixFormat.JSON
    elif isinstance(format_, str):
        format_ = GetTreatyCongressTreatyNumberTreatySuffixFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/treaty/{congress}/{treaty_number}/{treaty_suffix}".format(
            congress=congress,
            treaty_number=treaty_number,
            treaty_suffix=treaty_suffix,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, TreatyDetail]]:
    if response.status_code == 200:
        response_200 = TreatyDetail.from_dict(response.json())

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
) -> Response[Union[Any, TreatyDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    treaty_number: int,
    treaty_suffix: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat
    ] = GetTreatyCongressTreatyNumberTreatySuffixFormat.XML,
) -> Response[Union[Any, TreatyDetail]]:
    """Returns detailed information for a specified partitioned treaty.

     Returns detailed information for a specified partitioned treaty.

    Args:
        congress (int):
        treaty_number (int):
        treaty_suffix (str):
        format_ (Union[Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat]):  Default:
            GetTreatyCongressTreatyNumberTreatySuffixFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TreatyDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        treaty_number=treaty_number,
        treaty_suffix=treaty_suffix,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    treaty_number: int,
    treaty_suffix: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat
    ] = GetTreatyCongressTreatyNumberTreatySuffixFormat.XML,
) -> Optional[Union[Any, TreatyDetail]]:
    """Returns detailed information for a specified partitioned treaty.

     Returns detailed information for a specified partitioned treaty.

    Args:
        congress (int):
        treaty_number (int):
        treaty_suffix (str):
        format_ (Union[Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat]):  Default:
            GetTreatyCongressTreatyNumberTreatySuffixFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TreatyDetail]
    """

    return sync_detailed(
        congress=congress,
        treaty_number=treaty_number,
        treaty_suffix=treaty_suffix,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    treaty_number: int,
    treaty_suffix: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat
    ] = GetTreatyCongressTreatyNumberTreatySuffixFormat.XML,
) -> Response[Union[Any, TreatyDetail]]:
    """Returns detailed information for a specified partitioned treaty.

     Returns detailed information for a specified partitioned treaty.

    Args:
        congress (int):
        treaty_number (int):
        treaty_suffix (str):
        format_ (Union[Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat]):  Default:
            GetTreatyCongressTreatyNumberTreatySuffixFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TreatyDetail]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        treaty_number=treaty_number,
        treaty_suffix=treaty_suffix,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    treaty_number: int,
    treaty_suffix: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat
    ] = GetTreatyCongressTreatyNumberTreatySuffixFormat.XML,
) -> Optional[Union[Any, TreatyDetail]]:
    """Returns detailed information for a specified partitioned treaty.

     Returns detailed information for a specified partitioned treaty.

    Args:
        congress (int):
        treaty_number (int):
        treaty_suffix (str):
        format_ (Union[Unset, GetTreatyCongressTreatyNumberTreatySuffixFormat]):  Default:
            GetTreatyCongressTreatyNumberTreatySuffixFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TreatyDetail]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            treaty_number=treaty_number,
            treaty_suffix=treaty_suffix,
            client=client,
            format_=format_,
        )
    ).parsed
