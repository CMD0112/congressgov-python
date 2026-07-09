from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_house_communication_congress_communication_type_communication_number_communication_type import (
    GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
)
from ...models.get_house_communication_congress_communication_type_communication_number_format import (
    GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat,
)
from ...models.house_communication_type_number import HouseCommunicationTypeNumber
from ...types import UNSET, Response, Unset


def _get_kwargs(
    congress: int,
    communication_type: GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
    communication_number: int,
    *,
    format_: Union[
        Unset, GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat
    ] = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/house-communication/{congress}/{communication_type}/{communication_number}".format(
            congress=congress,
            communication_type=communication_type,
            communication_number=communication_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HouseCommunicationTypeNumber]]:
    if response.status_code == 200:
        response_200 = HouseCommunicationTypeNumber.from_dict(response.json())

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
) -> Response[Union[Any, HouseCommunicationTypeNumber]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    congress: int,
    communication_type: GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
    communication_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat
    ] = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML,
) -> Response[Union[Any, HouseCommunicationTypeNumber]]:
    """Returns a list of House communications filtered by the specified congress and communication type..

     Returns a list of House communications filtered by the specified congress and communication type.

    Args:
        congress (int):
        communication_type
            (GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType):
        communication_number (int):
        format_ (Union[Unset,
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat]):  Default:
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HouseCommunicationTypeNumber]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        communication_type=communication_type,
        communication_number=communication_number,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    congress: int,
    communication_type: GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
    communication_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat
    ] = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML,
) -> Optional[Union[Any, HouseCommunicationTypeNumber]]:
    """Returns a list of House communications filtered by the specified congress and communication type..

     Returns a list of House communications filtered by the specified congress and communication type.

    Args:
        congress (int):
        communication_type
            (GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType):
        communication_number (int):
        format_ (Union[Unset,
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat]):  Default:
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HouseCommunicationTypeNumber]
    """

    return sync_detailed(
        congress=congress,
        communication_type=communication_type,
        communication_number=communication_number,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    congress: int,
    communication_type: GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
    communication_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat
    ] = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML,
) -> Response[Union[Any, HouseCommunicationTypeNumber]]:
    """Returns a list of House communications filtered by the specified congress and communication type..

     Returns a list of House communications filtered by the specified congress and communication type.

    Args:
        congress (int):
        communication_type
            (GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType):
        communication_number (int):
        format_ (Union[Unset,
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat]):  Default:
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HouseCommunicationTypeNumber]]
    """

    kwargs = _get_kwargs(
        congress=congress,
        communication_type=communication_type,
        communication_number=communication_number,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    congress: int,
    communication_type: GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType,
    communication_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[
        Unset, GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat
    ] = GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML,
) -> Optional[Union[Any, HouseCommunicationTypeNumber]]:
    """Returns a list of House communications filtered by the specified congress and communication type..

     Returns a list of House communications filtered by the specified congress and communication type.

    Args:
        congress (int):
        communication_type
            (GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType):
        communication_number (int):
        format_ (Union[Unset,
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat]):  Default:
            GetHouseCommunicationCongressCommunicationTypeCommunicationNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HouseCommunicationTypeNumber]
    """

    return (
        await asyncio_detailed(
            congress=congress,
            communication_type=communication_type,
            communication_number=communication_number,
            client=client,
            format_=format_,
        )
    ).parsed
