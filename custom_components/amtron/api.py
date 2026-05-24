"""Amtron API client."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aiohttp
from homeassistant.exceptions import HomeAssistantError
from yarl import URL

from .const import DEFAULT_BASE_PATH, DEFAULT_PORT


class AmtronApiError(HomeAssistantError):
    """Raised when an API call fails."""


@dataclass(slots=True)
class AmtronCredentials:
    """Connection details for one wallbox."""

    host: str
    devkey: str
    pin2: str | None = None
    port: int = DEFAULT_PORT
    base_path: str = DEFAULT_BASE_PATH


class AmtronApiClient:
    """Minimal async client for the Amtron HTTP API."""

    def __init__(self, session: aiohttp.ClientSession, credentials: AmtronCredentials) -> None:
        self._session = session
        self._credentials = credentials

    @property
    def base_url(self) -> URL:
        return URL.build(
            scheme="http",
            host=self._credentials.host,
            port=self._credentials.port,
        ).with_path(self._credentials.base_path.rstrip("/"))

    def _url(self, path: str) -> URL:
        return self.base_url / path.lstrip("/")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Mapping[str, Any] | None = None,
        allow_empty: bool = False,
    ) -> Any:
        headers = {"Accept": "application/json"}
        if json_data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"

        try:
            async with self._session.request(
                method,
                self._url(path),
                params=params,
                json=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                if response.status >= 400:
                    raise AmtronApiError(
                        f"Amtron API request {method} {path} failed with {response.status}: {await response.text()}"
                    )
                if allow_empty or response.content_length == 0:
                    return None
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise AmtronApiError(f"Unable to contact Amtron wallbox: {err}") from err

    async def get_device_info(self) -> dict[str, Any]:
        return await self._request("GET", "/DevInfo", params={"DevKey": self._credentials.devkey})

    async def get_charge_data(self) -> dict[str, Any]:
        return await self._request("GET", "/ChargeData", params={"DevKey": self._credentials.devkey})

    async def get_statistics(self, period: str) -> dict[str, Any]:
        return await self._request("GET", f"/Statistics/{period}", params={"DevKey": self._credentials.devkey})

    async def set_device_info(self, payload: Mapping[str, Any]) -> None:
        await self._request("POST", "/DevInfo", params={"DevKey": self._credentials.devkey}, json_data=payload, allow_empty=True)

    async def set_charge_data(self, payload: Mapping[str, Any]) -> None:
        await self._request("POST", "/ChargeData", params={"DevKey": self._credentials.devkey}, json_data=payload, allow_empty=True)

    async def set_home_manager(self, payload: Mapping[str, Any]) -> None:
        await self._request("POST", "/HomeManager", params={"DevKey": self._credentials.devkey}, json_data=payload, allow_empty=True)

    async def get_whitelist(self, state: str, pin: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"DevKey": self._credentials.devkey, "State": state}
        pin_value = pin or self._credentials.pin2
        if pin_value is not None:
            params["Pin"] = pin_value
        return await self._request("GET", "/Whitelist", params=params)

    async def set_whitelist(self, payload: Mapping[str, Any], pin: str | None = None) -> None:
        params: dict[str, Any] = {"DevKey": self._credentials.devkey}
        pin_value = pin or self._credentials.pin2
        if pin_value is not None:
            params["Pin"] = pin_value
        await self._request("POST", "/Whitelist", params=params, json_data=payload, allow_empty=True)

    async def delete_whitelist(self, uid: str, pin: str | None = None) -> None:
        params: dict[str, Any] = {"DevKey": self._credentials.devkey, "Uid": uid}
        pin_value = pin or self._credentials.pin2
        if pin_value is not None:
            params["Pin"] = pin_value
        await self._request("DELETE", "/Whitelist", params=params, allow_empty=True)
