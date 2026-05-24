"""Switch platform for Amtron."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AmtronBaseEntity


class AmtronAutoChargeSwitch(AmtronBaseEntity, SwitchEntity):
    """Toggle automatic charging."""

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Auto Charge"
        self._attr_unique_id = f"{entry_id}-auto-charge"

    @property
    def is_on(self) -> bool | None:
        return self._device_info.get("AutoChg")

    async def async_turn_on(self, **kwargs) -> None:
        await self.client.set_charge_data({"Permanent": True, "RemoteCurr": None, "AutoChg": True, "ChgState": None, "Uid": None})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.client.set_charge_data({"Permanent": True, "RemoteCurr": None, "AutoChg": False, "ChgState": None, "Uid": None})
        await self.coordinator.async_request_refresh()


class AmtronExcessEnergySwitch(AmtronBaseEntity, SwitchEntity):
    """Toggle charging from excess energy only."""

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Excess Energy Only"
        self._attr_unique_id = f"{entry_id}-excess-energy-only"

    @property
    def is_on(self) -> bool | None:
        return (self.status_data.get("charge_data", {}) or {}).get("ExcessNrg")

    async def async_turn_on(self, **kwargs) -> None:
        await self.client.set_home_manager({"Permanent": True, "NrgDemand": None, "ExcessNrg": True, "SolarPrice": None, "RemTime": None})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.client.set_home_manager({"Permanent": True, "NrgDemand": None, "ExcessNrg": False, "SolarPrice": None, "RemTime": None})
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Amtron switches."""

    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AmtronAutoChargeSwitch(data["status_coordinator"], entry.entry_id), AmtronExcessEnergySwitch(data["status_coordinator"], entry.entry_id)])
