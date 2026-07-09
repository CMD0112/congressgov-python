from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_member_bioguide_id_format import GetMemberBioguideIdFormat
from ...models.member import Member
from ...types import UNSET, Response, Unset


def _get_kwargs(
    bioguide_id: str,
    *,
    format_: Union[Unset, GetMemberBioguideIdFormat] = GetMemberBioguideIdFormat.XML,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetMemberBioguideIdFormat.JSON
    elif isinstance(format_, str):
        format_ = GetMemberBioguideIdFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/member/{bioguide_id}".format(
            bioguide_id=bioguide_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Member]]:
    if response.status_code == 200:
        response_200 = Member.from_dict(response.json())

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
) -> Response[Union[Any, Member]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    bioguide_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberBioguideIdFormat] = GetMemberBioguideIdFormat.XML,
) -> Response[Union[Any, Member]]:
    """Returns detailed information for a specified congressional member.

     Returns detailed information for a specified congressional member.

    Args:
        bioguide_id (str):
        format_ (Union[Unset, GetMemberBioguideIdFormat]):  Default:
            GetMemberBioguideIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Member]]
    """

    kwargs = _get_kwargs(
        bioguide_id=bioguide_id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    bioguide_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberBioguideIdFormat] = GetMemberBioguideIdFormat.XML,
) -> Optional[Union[Any, Member]]:
    """Returns detailed information for a specified congressional member.

     Returns detailed information for a specified congressional member.

    Args:
        bioguide_id (str):
        format_ (Union[Unset, GetMemberBioguideIdFormat]):  Default:
            GetMemberBioguideIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Member]
    """

    return sync_detailed(
        bioguide_id=bioguide_id,
        client=client,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    bioguide_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberBioguideIdFormat] = GetMemberBioguideIdFormat.XML,
) -> Response[Union[Any, Member]]:
    """Returns detailed information for a specified congressional member.

     Returns detailed information for a specified congressional member.

    Args:
        bioguide_id (str):
        format_ (Union[Unset, GetMemberBioguideIdFormat]):  Default:
            GetMemberBioguideIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Member]]
    """

    kwargs = _get_kwargs(
        bioguide_id=bioguide_id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    bioguide_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberBioguideIdFormat] = GetMemberBioguideIdFormat.XML,
) -> Optional[Union[Any, Member]]:
    """Returns detailed information for a specified congressional member.

     Returns detailed information for a specified congressional member.

    Args:
        bioguide_id (str):
        format_ (Union[Unset, GetMemberBioguideIdFormat]):  Default:
            GetMemberBioguideIdFormat.XML.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Member]
    """

    return (
        await asyncio_detailed(
            bioguide_id=bioguide_id,
            client=client,
            format_=format_,
        )
    ).parsed
