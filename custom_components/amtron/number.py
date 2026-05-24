"""Number platform for Amtron."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AmtronBaseEntity


class AmtronNumberEntity(AmtronBaseEntity, NumberEntity):
    """Generic number entity."""

    def __init__(self, coordinator, entry_id: str, *, key: str, name: str, unit: str | None, minimum: float, maximum: float, step: float, getter, setter) -> None:
        super().__init__(coordinator, entry_id)
        self._key = key
        self._getter = getter
        self._setter = setter
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}-{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        return self._getter(self.status_data)

    async def async_set_native_value(self, value: float) -> None:
        await self._setter(self.client, value)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Amtron numbers."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["status_coordinator"]

    def _getter(source: str, field: str):
        def inner(data: dict[str, Any]):
            return (data.get(source, {}) or {}).get(field)

        return inner

    async def _set_remote_curr(client, value):
        await client.set_charge_data({"Permanent": True, "RemoteCurr": value, "AutoChg": None, "ChgState": None, "Uid": None})

    async def _set_battery(client, value):
        await client.set_device_info({"Battery": value})

    async def _set_energy_demand(client, value):
        await client.set_home_manager({"Permanent": True, "NrgDemand": value, "ExcessNrg": None, "SolarPrice": None, "RemTime": None})

    async def _set_rem_time(client, value):
        await client.set_home_manager({"Permanent": True, "NrgDemand": None, "ExcessNrg": None, "SolarPrice": None, "RemTime": str(int(value))})

    async def _set_solar_price(client, value):
        await client.set_home_manager({"Permanent": True, "NrgDemand": None, "ExcessNrg": None, "SolarPrice": value, "RemTime": None})

    async_add_entities(
        [
            AmtronNumberEntity(coordinator, entry.entry_id, key="remote-current", name="Remote Current", unit="A", minimum=0, maximum=32, step=1, getter=_getter("charge_data", "RemoteCurr"), setter=_set_remote_curr),
            AmtronNumberEntity(coordinator, entry.entry_id, key="battery-capacity", name="Battery Capacity", unit="Wh", minimum=0, maximum=200000, step=100, getter=_getter("device_info", "Battery"), setter=_set_battery),
            AmtronNumberEntity(coordinator, entry.entry_id, key="energy-demand", name="Energy Demand", unit="Wh", minimum=0, maximum=200000, step=100, getter=_getter("charge_data", "NrgDemand"), setter=_set_energy_demand),
            AmtronNumberEntity(coordinator, entry.entry_id, key="remaining-time", name="Remaining Time", unit="min", minimum=0, maximum=10080, step=1, getter=_getter("charge_data", "RemTime"), setter=_set_rem_time),
            AmtronNumberEntity(coordinator, entry.entry_id, key="solar-price", name="Solar Price", unit="0.1 ct/kWh", minimum=0, maximum=1000, step=1, getter=_getter("charge_data", "SolarPrice"), setter=_set_solar_price),
        ]
    )
