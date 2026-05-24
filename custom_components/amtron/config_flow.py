"""Config flow for Amtron."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmtronApiClient, AmtronApiError, AmtronCredentials
from .const import CONF_BASE_PATH, CONF_DEVKEY, CONF_HOST, CONF_NAME, CONF_PIN2, CONF_PORT, DEFAULT_BASE_PATH, DEFAULT_PORT, DOMAIN


class AmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Amtron config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            devkey = user_input[CONF_DEVKEY].strip()
            port = user_input[CONF_PORT]
            base_path = user_input[CONF_BASE_PATH].strip() or DEFAULT_BASE_PATH
            pin2 = user_input.get(CONF_PIN2, "").strip() or None
            name = user_input.get(CONF_NAME, "Amtron Wallbox").strip() or "Amtron Wallbox"

            await self.async_set_unique_id(f"amtron-{host}-{port}")
            self._abort_if_unique_id_configured()

            credentials = AmtronCredentials(host=host, devkey=devkey, pin2=pin2, port=port, base_path=base_path)
            client = AmtronApiClient(async_get_clientsession(self.hass), credentials)

            try:
                await client.get_device_info()
            except AmtronApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_DEVKEY: devkey,
                        CONF_PIN2: pin2,
                        CONF_PORT: port,
                        CONF_BASE_PATH: base_path,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.100"): str,
                vol.Required(CONF_DEVKEY): str,
                vol.Optional(CONF_PIN2, default=""): str,
                vol.Optional(CONF_NAME, default="Amtron Wallbox"): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
                vol.Optional(CONF_BASE_PATH, default=DEFAULT_BASE_PATH): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
