"""Select platform for Amtron."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CHARGE_CONTROL_STATES, DEV_MODES, DOMAIN
from .entity import AmtronBaseEntity


class AmtronModeSelect(AmtronBaseEntity, SelectEntity):
    """Select the wallbox operating mode."""

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Charging Mode"
        self._attr_unique_id = f"{entry_id}-charging-mode"

    @property
    def options(self) -> list[str]:
        return list(DEV_MODES)

    @property
    def current_option(self) -> str | None:
        return (self.status_data.get("device_info", {}) or {}).get("DevMode")

    async def async_select_option(self, option: str) -> None:
        await self.client.set_device_info({"DevMode": option})
        await self.coordinator.async_request_refresh()


class AmtronChargeControlSelect(AmtronBaseEntity, SelectEntity):
    """Select the current charging action."""

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Charging Control"
        self._attr_unique_id = f"{entry_id}-charging-control"

    @property
    def options(self) -> list[str]:
        return list(CHARGE_CONTROL_STATES)

    @property
    def current_option(self) -> str | None:
        return (self.status_data.get("charge_data", {}) or {}).get("ChgState")

    async def async_select_option(self, option: str) -> None:
        payload: dict[str, Any] = {"Permanent": False, "RemoteCurr": None, "AutoChg": None, "ChgState": option, "Uid": "00000000"}
        await self.client.set_charge_data(payload)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Amtron select entities."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["status_coordinator"]
    use_modbus = data.get("use_modbus", False)

    entities: list[SelectEntity] = [AmtronChargeControlSelect(coordinator, entry.entry_id)]
    if not use_modbus:
        entities.insert(0, AmtronModeSelect(coordinator, entry.entry_id))

    async_add_entities(entities)
