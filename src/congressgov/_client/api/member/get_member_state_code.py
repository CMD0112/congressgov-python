from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_member_state_code_format import GetMemberStateCodeFormat
from ...models.members import Members
from ...types import UNSET, Response, Unset


def _get_kwargs(
    state_code: str,
    *,
    format_: Union[Unset, GetMemberStateCodeFormat] = GetMemberStateCodeFormat.XML,
    limit: Union[Unset, int] = UNSET,
    current_member: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_format_: Union[Unset, str] = UNSET
    if format_ is None:
        format_ = GetMemberStateCodeFormat.JSON
    elif isinstance(format_, str):
        format_ = GetMemberStateCodeFormat(format_.lower())
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params["limit"] = limit

    params["currentMember"] = current_member

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/member/{state_code}".format(
            state_code=state_code,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Members]]:
    if response.status_code == 200:
        response_200 = Members.from_dict(response.json())

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
) -> Response[Union[Any, Members]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    state_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberStateCodeFormat] = GetMemberStateCodeFormat.XML,
    limit: Union[Unset, int] = UNSET,
    current_member: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, Members]]:
    """Returns a list of members filtered by state.

     Returns a list of members filtered by state.

    Args:
        state_code (str):
        format_ (Union[Unset, GetMemberStateCodeFormat]):  Default: GetMemberStateCodeFormat.XML.
        limit (Union[Unset, int]):
        current_member (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Members]]
    """

    kwargs = _get_kwargs(
        state_code=state_code,
        format_=format_,
        limit=limit,
        current_member=current_member,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    state_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberStateCodeFormat] = GetMemberStateCodeFormat.XML,
    limit: Union[Unset, int] = UNSET,
    current_member: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, Members]]:
    """Returns a list of members filtered by state.

     Returns a list of members filtered by state.

    Args:
        state_code (str):
        format_ (Union[Unset, GetMemberStateCodeFormat]):  Default: GetMemberStateCodeFormat.XML.
        limit (Union[Unset, int]):
        current_member (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Members]
    """

    return sync_detailed(
        state_code=state_code,
        client=client,
        format_=format_,
        limit=limit,
        current_member=current_member,
    ).parsed


async def asyncio_detailed(
    state_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberStateCodeFormat] = GetMemberStateCodeFormat.XML,
    limit: Union[Unset, int] = UNSET,
    current_member: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, Members]]:
    """Returns a list of members filtered by state.

     Returns a list of members filtered by state.

    Args:
        state_code (str):
        format_ (Union[Unset, GetMemberStateCodeFormat]):  Default: GetMemberStateCodeFormat.XML.
        limit (Union[Unset, int]):
        current_member (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Members]]
    """

    kwargs = _get_kwargs(
        state_code=state_code,
        format_=format_,
        limit=limit,
        current_member=current_member,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    state_code: str,
    *,
    client: Union[AuthenticatedClient, Client],
    format_: Union[Unset, GetMemberStateCodeFormat] = GetMemberStateCodeFormat.XML,
    limit: Union[Unset, int] = UNSET,
    current_member: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, Members]]:
    """Returns a list of members filtered by state.

     Returns a list of members filtered by state.

    Args:
        state_code (str):
        format_ (Union[Unset, GetMemberStateCodeFormat]):  Default: GetMemberStateCodeFormat.XML.
        limit (Union[Unset, int]):
        current_member (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Members]
    """

    return (
        await asyncio_detailed(
            state_code=state_code,
            client=client,
            format_=format_,
            limit=limit,
            current_member=current_member,
        )
    ).parsed
