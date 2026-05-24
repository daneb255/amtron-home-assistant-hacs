"""Common entity helpers for Amtron."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER


class AmtronBaseEntity(CoordinatorEntity):
    """Base entity with access to the client and device metadata."""

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entry_id = entry_id

    @property
    def hass_data(self) -> Mapping[str, Any]:
        return self.hass.data[DOMAIN][self.entry_id]

    @property
    def client(self):
        return self.hass_data["client"]

    @property
    def use_modbus(self) -> bool:
        return bool(self.hass_data.get("use_modbus", False))

    @property
    def status_data(self) -> dict[str, Any]:
        return self.hass_data["status_coordinator"].data or {}

    @property
    def statistics_data(self) -> dict[str, Any]:
        return self.hass_data["statistics_coordinator"].data or {}

    @property
    def device_info(self) -> DeviceInfo:
        device = self.status_data.get("device_info", {})
        identifier = str(device.get("Sn") or self.hass_data["credentials"].host)
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            manufacturer=MANUFACTURER,
            model=str(device.get("ItemNo") or "Amtron Wallbox"),
            name=str(device.get("DevName") or f"Amtron {identifier}"),
            sw_version=str(device.get("Hmi") or device.get("Wifi") or ""),
        )
