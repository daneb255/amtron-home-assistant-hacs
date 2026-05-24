"""Service handlers for Amtron."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_WHITELIST = "add_whitelist"
SERVICE_REMOVE_WHITELIST = "remove_whitelist"
SERVICE_GET_CHARGERECORDS = "get_chargerecords"

ATTR_UID = "uid"
ATTR_NAME = "name"
ATTR_DEVICE_ID = "device_id"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"


async def _async_open_session(client, session_type: str, pin: str | None = None, timeout: int = 30) -> dict[str, Any] | None:
    """Open a session and keep it alive during the operation."""
    try:
        await client.get_whitelist("Open", pin)
        entries = []
        remaining = float("inf")

        while remaining > 0 and timeout > 0:
            result = await client.get_whitelist("Read", pin)
            if result:
                entries.extend(result.get("RemEntries", []) or [])
                remaining = result.get("RemEntries", 0)
            timeout -= 1
            if remaining > 0 and timeout > 0:
                await asyncio.sleep(0.5)

        await client.get_whitelist("Close", pin)
        return entries
    except Exception as err:
        _LOGGER.error(f"Failed to open session: {err}")
        return None


async def handle_add_whitelist(hass: HomeAssistant, call: ServiceCall) -> None:
    """Add an RFID tag to the whitelist."""
    device_id = call.data[ATTR_DEVICE_ID]
    uid = call.data[ATTR_UID]
    name = call.data.get(ATTR_NAME, "")

    data = hass.data.get(DOMAIN, {})
    config_entry = None
    for entry_id, entry_data in data.items():
        config_entry = entry_data
        break

    if not config_entry:
        _LOGGER.error("No Amtron device found")
        return

    client = config_entry["client"]
    pin = config_entry["credentials"].pin2

    if not pin:
        _LOGGER.error("PIN2 is required to manage whitelist")
        return

    try:
        payload = {"Name": name, "Uid": uid, "Master": False}
        await client.set_whitelist(payload, pin)
        _LOGGER.info(f"Added RFID tag {uid} to whitelist")
    except Exception as err:
        _LOGGER.error(f"Failed to add whitelist entry: {err}")


async def handle_remove_whitelist(hass: HomeAssistant, call: ServiceCall) -> None:
    """Remove an RFID tag from the whitelist."""
    device_id = call.data[ATTR_DEVICE_ID]
    uid = call.data[ATTR_UID]

    data = hass.data.get(DOMAIN, {})
    config_entry = None
    for entry_id, entry_data in data.items():
        config_entry = entry_data
        break

    if not config_entry:
        _LOGGER.error("No Amtron device found")
        return

    client = config_entry["client"]
    pin = config_entry["credentials"].pin2

    if not pin:
        _LOGGER.error("PIN2 is required to manage whitelist")
        return

    try:
        await client.delete_whitelist(uid, pin)
        _LOGGER.info(f"Removed RFID tag {uid} from whitelist")
    except Exception as err:
        _LOGGER.error(f"Failed to remove whitelist entry: {err}")


async def handle_get_chargerecords(hass: HomeAssistant, call: ServiceCall) -> None:
    """Retrieve charge records (sessions)."""
    device_id = call.data[ATTR_DEVICE_ID]
    start_time = int(call.data.get(ATTR_START_TIME, 0))
    end_time = int(call.data.get(ATTR_END_TIME, 9999999999))

    data = hass.data.get(DOMAIN, {})
    config_entry = None
    for entry_id, entry_data in data.items():
        config_entry = entry_data
        break

    if not config_entry:
        _LOGGER.error("No Amtron device found")
        return

    client = config_entry["client"]

    try:
        await client.get_charge_records(start_time, end_time)
        _LOGGER.info(f"Retrieved charge records from {start_time} to {end_time}")
    except Exception as err:
        _LOGGER.error(f"Failed to retrieve charge records: {err}")


def register_services(hass: HomeAssistant) -> None:
    """Register Amtron services."""

    hass.services.async_register(DOMAIN, SERVICE_ADD_WHITELIST, handle_add_whitelist)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_WHITELIST, handle_remove_whitelist)
    hass.services.async_register(DOMAIN, SERVICE_GET_CHARGERECORDS, handle_get_chargerecords)
