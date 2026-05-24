"""Amtron integration setup."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmtronApiClient, AmtronCredentials
from .const import CONF_BASE_PATH, CONF_DEVKEY, CONF_HOST, CONF_PIN2, CONF_PORT, CONF_USE_MODBUS, DOMAIN, PLATFORMS
from .coordinator import AmtronStatisticsCoordinator, AmtronStatusCoordinator
from .modbus_api import AmtronModbusClient
from .services import register_services


def _entry_value(entry: ConfigEntry, key: str, default=None):
    """Return option override value or fallback to entry data."""
    if key in entry.options:
        return entry.options[key]
    return entry.data.get(key, default)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amtron from a config entry."""

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    use_modbus = _entry_value(entry, CONF_USE_MODBUS, False)

    credentials = AmtronCredentials(
        host=_entry_value(entry, CONF_HOST),
        devkey=_entry_value(entry, CONF_DEVKEY, ""),
        pin2=_entry_value(entry, CONF_PIN2),
        port=_entry_value(entry, CONF_PORT),
        base_path=_entry_value(entry, CONF_BASE_PATH),
    )

    if use_modbus:
        client = AmtronModbusClient(host=credentials.host, port=credentials.port)
    else:
        session = async_get_clientsession(hass)
        client = AmtronApiClient(session, credentials)

    status_coordinator = AmtronStatusCoordinator(hass, client, credentials.host)
    statistics_coordinator = AmtronStatisticsCoordinator(hass, client, credentials.host)

    await status_coordinator.async_config_entry_first_refresh()
    await statistics_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "credentials": credentials,
        "use_modbus": use_modbus,
        "status_coordinator": status_coordinator,
        "statistics_coordinator": statistics_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Amtron."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
