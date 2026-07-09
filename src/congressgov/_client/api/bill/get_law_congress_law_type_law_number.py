from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_law_congress_law_type_law_number_format import GetLawCongressLawTypeLawNumberFormat
from ...models.law_number import LawNumber
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    law_type: str,
    law_number: int,
    *,
    format_: Union[Unset, GetLawCongressLawTypeLawNumberFormat] = GetLawCongressLawTypeLawNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetLawCongressLawTypeLawNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetLawCongressLawTypeLawNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/law/{congress}/{law_type}/{law_number}".format(
            congress=congress,
            law_type=law_type,
            law_number=law_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, LawNumber]]:
    if response.status_code == 200:
        response_200 = LawNumber.from_dict(response.json())

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
) -> Response[Union[Any, LawNumber]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    law_type: str,
    law_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetLawCongressLawTypeLawNumberFormat] = GetLawCongressLawTypeLawNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, LawNumber]]:
    """Returns a law filtered by specified congress, law type (public or private), and law number.

     Returns a law filtered by specified congress, law type (public or private), and law number.

    Args:
        congress (int):
        law_type (str):
        law_number (int):
        format_ (Union[Unset, GetLawCongressLawTypeLawNumberFormat]):  Default:
            GetLawCongressLawTypeLawNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, LawNumber]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        law_type=law_type,
        law_number=law_number,
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
    law_type: str,
    law_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetLawCongressLawTypeLawNumberFormat] = GetLawCongressLawTypeLawNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, LawNumber]]:
    """Returns a law filtered by specified congress, law type (public or private), and law number.

     Returns a law filtered by specified congress, law type (public or private), and law number.

    Args:
        congress (int):
        law_type (str):
        law_number (int):
        format_ (Union[Unset, GetLawCongressLawTypeLawNumberFormat]):  Default:
            GetLawCongressLawTypeLawNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, LawNumber]
    """

    return sync_detailed(
        congress=congress,
        law_type=law_type,
        law_number=law_number,
        client=client,
        format_=format_,
        offset=offset,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    congress: int,
    law_type: str,
    law_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetLawCongressLawTypeLawNumberFormat] = GetLawCongressLawTypeLawNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Any, LawNumber]]:
    """Returns a law filtered by specified congress, law type (public or private), and law number.

     Returns a law filtered by specified congress, law type (public or private), and law number.

    Args:
        congress (int):
        law_type (str):
        law_number (int):
        format_ (Union[Unset, GetLawCongressLawTypeLawNumberFormat]):  Default:
            GetLawCongressLawTypeLawNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, LawNumber]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        law_type=law_type,
        law_number=law_number,
        format_=format_,
        offset=offset,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    law_type: str,
    law_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetLawCongressLawTypeLawNumberFormat] = GetLawCongressLawTypeLawNumberFormat.XML,
    offset: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, LawNumber]]:
    """Returns a law filtered by specified congress, law type (public or private), and law number.

     Returns a law filtered by specified congress, law type (public or private), and law number.

    Args:
        congress (int):
        law_type (str):
        law_number (int):
        format_ (Union[Unset, GetLawCongressLawTypeLawNumberFormat]):  Default:
            GetLawCongressLawTypeLawNumberFormat.XML.
        offset (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, LawNumber]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            law_type=law_type,
            law_number=law_number,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit,
        )
    ).parsed
