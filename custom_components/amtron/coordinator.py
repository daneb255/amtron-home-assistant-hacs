"""Data coordinators for Amtron."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AmtronApiClient, AmtronApiError
from .const import DEFAULT_SCAN_INTERVAL_SECONDS, DEFAULT_STATS_SCAN_INTERVAL_SECONDS, STATISTICS_PERIODS


_LOGGER = logging.getLogger(__name__)


class AmtronStatusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that keeps the wallbox status up to date."""

    def __init__(self, hass, client: AmtronApiClient, host: str) -> None:
        self.client = client
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"amtron_{host}_status",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            device_info, charge_data = await asyncio.gather(self.client.get_device_info(), self.client.get_charge_data())
        except AmtronApiError as err:
            raise UpdateFailed(str(err)) from err

        return {"device_info": device_info, "charge_data": charge_data}


class AmtronStatisticsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that keeps statistics up to date."""

    def __init__(self, hass, client: AmtronApiClient, host: str) -> None:
        self.client = client
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"amtron_{host}_statistics",
            update_interval=timedelta(seconds=DEFAULT_STATS_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            results = await asyncio.gather(*(self.client.get_statistics(period) for period in STATISTICS_PERIODS))
        except AmtronApiError as err:
            raise UpdateFailed(str(err)) from err

        return dict(zip(STATISTICS_PERIODS, results, strict=True))
