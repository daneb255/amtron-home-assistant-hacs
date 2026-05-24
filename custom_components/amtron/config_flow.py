"""Config flow for Amtron."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmtronApiClient, AmtronApiError, AmtronCredentials
from .const import CONF_BASE_PATH, CONF_DEVKEY, CONF_HOST, CONF_NAME, CONF_PIN2, CONF_PORT, CONF_USE_MODBUS, DEFAULT_BASE_PATH, DEFAULT_MODBUS_PORT, DEFAULT_PORT, DOMAIN
from .modbus_api import AmtronModbusClient


class AmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Amtron config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return AmtronOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            devkey = user_input.get(CONF_DEVKEY, "").strip()
            use_modbus = user_input.get(CONF_USE_MODBUS, False)
            port = user_input[CONF_PORT]
            if use_modbus and port == DEFAULT_PORT:
                port = DEFAULT_MODBUS_PORT
            base_path = user_input[CONF_BASE_PATH].strip() or DEFAULT_BASE_PATH
            pin2 = user_input.get(CONF_PIN2, "").strip() or None
            name = user_input.get(CONF_NAME, "Amtron Wallbox").strip() or "Amtron Wallbox"

            if not use_modbus and not devkey:
                errors["base"] = "devkey_required_http"

            if not errors:
                await self.async_set_unique_id(f"amtron-{host}-{port}")
                self._abort_if_unique_id_configured()

                credentials = AmtronCredentials(host=host, devkey=devkey, pin2=pin2, port=port, base_path=base_path)
                if use_modbus:
                    client = AmtronModbusClient(host=host, port=port)
                else:
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
                            CONF_USE_MODBUS: use_modbus,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.100"): str,
                vol.Optional(CONF_DEVKEY, default=""): str,
                vol.Optional(CONF_PIN2, default=""): str,
                vol.Optional(CONF_NAME, default="Amtron Wallbox"): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
                vol.Optional(CONF_BASE_PATH, default=DEFAULT_BASE_PATH): str,
                vol.Optional(CONF_USE_MODBUS, default=False): bool,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class AmtronOptionsFlow(config_entries.OptionsFlow):
    """Handle Amtron options."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors: dict[str, str] = {}

        host = self._config_entry.data[CONF_HOST]
        current_use_modbus = self._config_entry.options.get(
            CONF_USE_MODBUS,
            self._config_entry.data.get(CONF_USE_MODBUS, False),
        )
        current_devkey = self._config_entry.options.get(
            CONF_DEVKEY,
            self._config_entry.data.get(CONF_DEVKEY, ""),
        )
        current_pin2 = self._config_entry.options.get(
            CONF_PIN2,
            self._config_entry.data.get(CONF_PIN2, ""),
        )
        current_port = self._config_entry.options.get(
            CONF_PORT,
            self._config_entry.data.get(CONF_PORT, DEFAULT_PORT),
        )
        current_base_path = self._config_entry.options.get(
            CONF_BASE_PATH,
            self._config_entry.data.get(CONF_BASE_PATH, DEFAULT_BASE_PATH),
        )

        if user_input is not None:
            use_modbus = user_input.get(CONF_USE_MODBUS, current_use_modbus)
            devkey = user_input.get(CONF_DEVKEY, "").strip()
            pin2 = user_input.get(CONF_PIN2, "").strip() or None
            port = user_input.get(CONF_PORT, current_port)
            base_path = user_input.get(CONF_BASE_PATH, DEFAULT_BASE_PATH).strip() or DEFAULT_BASE_PATH

            if use_modbus and port == DEFAULT_PORT:
                port = DEFAULT_MODBUS_PORT

            if not use_modbus and not devkey:
                errors["base"] = "devkey_required_http"

            if not errors:
                credentials = AmtronCredentials(
                    host=host,
                    devkey=devkey,
                    pin2=pin2,
                    port=port,
                    base_path=base_path,
                )
                if use_modbus:
                    client = AmtronModbusClient(host=host, port=port)
                else:
                    client = AmtronApiClient(async_get_clientsession(self.hass), credentials)

                try:
                    await client.get_device_info()
                except AmtronApiError:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_USE_MODBUS: use_modbus,
                            CONF_DEVKEY: devkey,
                            CONF_PIN2: pin2,
                            CONF_PORT: port,
                            CONF_BASE_PATH: base_path,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Optional(CONF_USE_MODBUS, default=current_use_modbus): bool,
                vol.Optional(CONF_DEVKEY, default=current_devkey): str,
                vol.Optional(CONF_PIN2, default=current_pin2): str,
                vol.Optional(CONF_PORT, default=current_port): vol.All(int, vol.Range(min=1, max=65535)),
                vol.Optional(CONF_BASE_PATH, default=current_base_path): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
