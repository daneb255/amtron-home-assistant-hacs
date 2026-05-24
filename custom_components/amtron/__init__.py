"""Amtron integration setup."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmtronApiClient, AmtronCredentials
from .const import CONF_BASE_PATH, CONF_DEVKEY, CONF_HOST, CONF_PIN2, CONF_PORT, DOMAIN, PLATFORMS
from .coordinator import AmtronStatisticsCoordinator, AmtronStatusCoordinator
from .services import register_services


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amtron from a config entry."""

    session = async_get_clientsession(hass)
    credentials = AmtronCredentials(
        host=entry.data[CONF_HOST],
        devkey=entry.data[CONF_DEVKEY],
        pin2=entry.data.get(CONF_PIN2),
        port=entry.data[CONF_PORT],
        base_path=entry.data[CONF_BASE_PATH],
    )
    client = AmtronApiClient(session, credentials)
    status_coordinator = AmtronStatusCoordinator(hass, client, credentials.host)
    statistics_coordinator = AmtronStatisticsCoordinator(hass, client, credentials.host)

    await status_coordinator.async_config_entry_first_refresh()
    await statistics_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "credentials": credentials,
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
