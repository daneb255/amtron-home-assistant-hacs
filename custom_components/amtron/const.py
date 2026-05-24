"""Constants for the Amtron integration."""

from __future__ import annotations

DEFAULT_BASE_PATH = "/MHCP/1.0"
DEFAULT_PORT = 25000
DEFAULT_SCAN_INTERVAL_SECONDS = 30
DEFAULT_STATS_SCAN_INTERVAL_SECONDS = 3600

DOMAIN = "amtron"
MANUFACTURER = "Mennekes"
PLATFORMS = ["sensor", "select", "switch", "number"]

CONF_BASE_PATH = "base_path"
CONF_DEVKEY = "devkey"
CONF_HOST = "host"
CONF_NAME = "name"
CONF_PIN2 = "pin2"
CONF_PORT = "port"

STATISTICS_PERIODS = ["Day", "Week", "Month", "Hyear", "Year", "Annual"]
CHARGE_CONTROL_STATES = ["Continue", "Pause", "Start", "Terminate"]
DEV_MODES = ["Remote", "HomeManager", "Time"]
