"""Sensor platform for Amtron."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AmtronBaseEntity


STATUS_SENSORS: list[dict[str, Any]] = [
    {"key": "dev_name", "source": "device_info", "field": "DevName", "name": "Device Name"},
    {"key": "mode", "source": "device_info", "field": "DevMode", "name": "Charging Mode"},
    {"key": "charging_state", "source": "charge_data", "field": "ChgState", "name": "Charging State"},
    {"key": "location_time", "source": "device_info", "field": "LocTime", "name": "Wallbox Time"},
    {"key": "current_power", "source": "charge_data", "field": "ActPwr", "name": "Current Power", "unit": "W"},
    {"key": "current_current", "source": "charge_data", "field": "ActCurr", "name": "Current Limit", "unit": "A"},
    {"key": "charged_energy", "source": "charge_data", "field": "ChgNrg", "name": "Charged Energy", "unit": "Wh"},
    {"key": "energy_demand", "source": "charge_data", "field": "NrgDemand", "name": "Energy Demand", "unit": "Wh"},
    {"key": "charge_duration", "source": "charge_data", "field": "ChgDuration", "name": "Charging Duration", "unit": "min"},
    {"key": "remaining_time", "source": "charge_data", "field": "RemTime", "name": "Remaining Time", "unit": "min"},
    {"key": "solar_share", "source": "charge_data", "field": "Solar", "name": "Solar Share", "unit": "%"},
    {"key": "tariff", "source": "charge_data", "field": "Tariff", "name": "Tariff"},
    {"key": "price", "source": "charge_data", "field": "Price", "name": "Price", "unit": "0.1 ct/kWh"},
    {"key": "battery_capacity", "source": "device_info", "field": "Battery", "name": "Battery Capacity", "unit": "Wh"},
    {"key": "phase_count", "source": "device_info", "field": "Phases", "name": "Phase Count"},
    {"key": "error_code", "source": "device_info", "field": "Err", "name": "Error Code"},
    {"key": "wifi_on", "source": "device_info", "field": "WifiOn", "name": "WiFi Enabled"},
    {"key": "auto_chg", "source": "device_info", "field": "AutoChg", "name": "Auto Charge"},
    {"key": "energy_manager", "source": "device_info", "field": "EmEnabled", "name": "Energy Manager"},
    {"key": "rfid_auth", "source": "device_info", "field": "Auth", "name": "RFID Auth"},
]


STATISTICS_SENSORS: list[dict[str, Any]] = [
    {"period": "Day", "key": "day", "name": "Statistics Today"},
    {"period": "Week", "key": "week", "name": "Statistics This Week"},
    {"period": "Month", "key": "month", "name": "Statistics This Month"},
    {"period": "Hyear", "key": "half_year", "name": "Statistics Half Year"},
    {"period": "Year", "key": "year", "name": "Statistics This Year"},
    {"period": "Annual", "key": "annual", "name": "Statistics Annual"},
]


class AmtronSensor(AmtronBaseEntity, SensorEntity):
    """Generic Amtron sensor."""

    NUMERIC_UNITS = {"W", "A", "Wh", "min", "%", "0.1 ct/kWh"}

    def __init__(self, coordinator, entry_id: str, description: dict[str, Any]) -> None:
        super().__init__(coordinator, entry_id)
        self.description = description
        self._attr_name = description["name"]
        self._attr_unique_id = f"{entry_id}-{description['key']}"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self.description["source"], {}).get(self.description["field"])

    @property
    def native_unit_of_measurement(self):
        return self.description.get("unit")

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT if self.description.get("unit") in self.NUMERIC_UNITS else None


class AmtronStatisticsSensor(AmtronBaseEntity, SensorEntity):
    """Statistics sensor."""

    def __init__(self, coordinator, entry_id: str, description: dict[str, Any]) -> None:
        super().__init__(coordinator, entry_id)
        self.description = description
        self._attr_name = description["name"]
        self._attr_unique_id = f"{entry_id}-statistics-{description['key']}"

    @property
    def native_value(self):
        period = self.description["period"]
        period_data = (self.coordinator.data or {}).get(period, {})
        if period == "Annual":
            years = period_data.get("Years", [])
            return len(years)
        return period_data.get("ChrNr")

    @property
    def native_unit_of_measurement(self):
        return "years" if self.description["period"] == "Annual" else "Wh"

    @property
    def extra_state_attributes(self):
        period = self.description["period"]
        period_data = (self.coordinator.data or {}).get(period, {})
        if period == "Annual":
            return {"years": period_data.get("Years", [])}
        return {
            "hybrid_energy": period_data.get("HybridNrg"),
            "solar_percent": period_data.get("Solar"),
            "tariff1_percent": period_data.get("Tariff1"),
            "tariff2_percent": period_data.get("Tariff2"),
            "charge_costs": period_data.get("ChgCosts"),
            "hybrid_costs": period_data.get("HybridCosts"),
            "avg_costs": period_data.get("AvgCosts"),
            "fix_costs": period_data.get("FixCosts"),
            "old_costs": period_data.get("OldCosts"),
            "km_diff": period_data.get("KmDiff"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Amtron sensors."""

    data = hass.data[DOMAIN][entry.entry_id]
    status_coordinator = data["status_coordinator"]
    statistics_coordinator = data["statistics_coordinator"]

    entities = [AmtronSensor(status_coordinator, entry.entry_id, description) for description in STATUS_SENSORS]
    entities.extend(
        AmtronStatisticsSensor(statistics_coordinator, entry.entry_id, description)
        for description in STATISTICS_SENSORS
    )

    async_add_entities(entities)
