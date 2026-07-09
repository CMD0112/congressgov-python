from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_house_requirement_requirement_number_format import GetHouseRequirementRequirementNumberFormat
from ...models.house_requirement import HouseRequirement
from ...types import UNSET, Response, Unset


def _get_kwargs(
    requirement_number: int,
    *,
    format_: Union[Unset, GetHouseRequirementRequirementNumberFormat] = GetHouseRequirementRequirementNumberFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetHouseRequirementRequirementNumberFormat.JSON
    elif isinstance(format_, str):
        format_ = GetHouseRequirementRequirementNumberFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/house-requirement/{requirement_number}".format(
            requirement_number=requirement_number,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HouseRequirement]]:
    if response.status_code == 200:
        response_200 = HouseRequirement.from_dict(response.json())

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
) -> Response[Union[Any, HouseRequirement]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    requirement_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetHouseRequirementRequirementNumberFormat] = GetHouseRequirementRequirementNumberFormat.XML,
) -> Response[Union[Any, HouseRequirement]]:
    """Returns detailed information for a specified House requirement.

     Returns detailed information for a specified House requirement.

    Args:
        requirement_number (int):
        format_ (Union[Unset, GetHouseRequirementRequirementNumberFormat]):  Default:
            GetHouseRequirementRequirementNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HouseRequirement]]
    """

    kwargs = _get_kwargs(
        requirement_number=requirement_number,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    requirement_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetHouseRequirementRequirementNumberFormat] = GetHouseRequirementRequirementNumberFormat.XML,
) -> Optional[Union[Any, HouseRequirement]]:
    """Returns detailed information for a specified House requirement.

     Returns detailed information for a specified House requirement.

    Args:
        requirement_number (int):
        format_ (Union[Unset, GetHouseRequirementRequirementNumberFormat]):  Default:
            GetHouseRequirementRequirementNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HouseRequirement]
    """

    return sync_detailed(
        requirement_number=requirement_number,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    requirement_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetHouseRequirementRequirementNumberFormat] = GetHouseRequirementRequirementNumberFormat.XML,
) -> Response[Union[Any, HouseRequirement]]:
    """Returns detailed information for a specified House requirement.

     Returns detailed information for a specified House requirement.

    Args:
        requirement_number (int):
        format_ (Union[Unset, GetHouseRequirementRequirementNumberFormat]):  Default:
            GetHouseRequirementRequirementNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HouseRequirement]]
    """

    kwargs = _get_kwargs(
        requirement_number=requirement_number,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    requirement_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetHouseRequirementRequirementNumberFormat] = GetHouseRequirementRequirementNumberFormat.XML,
) -> Optional[Union[Any, HouseRequirement]]:
    """Returns detailed information for a specified House requirement.

     Returns detailed information for a specified House requirement.

    Args:
        requirement_number (int):
        format_ (Union[Unset, GetHouseRequirementRequirementNumberFormat]):  Default:
            GetHouseRequirementRequirementNumberFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HouseRequirement]
    """

    return (
        await asyncio_detailed(
            requirement_number=requirement_number,
            client=client,
            format_=format_,
        )
    ).parsed
