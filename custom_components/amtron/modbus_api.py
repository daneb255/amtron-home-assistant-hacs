"""Amtron Modbus-TCP client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pymodbus.client import AsyncModbusTcpClient

from .api import AmtronApiError


_CHARGE_STATE_TO_REGISTER = {
    "Pause": 1,
    "Continue": 2,
    "Terminate": 3,
    "Start": 4,
}

_REGISTER_STATE_TO_CHARGE_STATE = {
    0: "Idle",
    1: "Authorize",
    2: "Connect",
    3: "Charging",
    4: "Pause",
    5: "Terminate",
    6: "Error",
}

_REGISTER_MODE_TO_DEV_MODE = {
    1: "Remote",
    2: "Time",
    3: "Time",
}


class AmtronModbusClient:
    """Minimal async client for the Amtron Modbus API."""

    def __init__(self, host: str, port: int, unit_id: int = 0xFF) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._client = AsyncModbusTcpClient(host=host, port=port)

    async def _connect(self) -> None:
        connected = await self._client.connect()
        if not connected:
            raise AmtronApiError(f"Unable to contact Amtron wallbox via Modbus at {self._host}:{self._port}")

    async def _read_input_registers(self, address: int, count: int) -> list[int]:
        await self._connect()
        response = await self._client.read_input_registers(address=address, count=count, device_id=self._unit_id)
        if response.isError():
            raise AmtronApiError(f"Modbus read_input_registers failed for 0x{address:04X}")
        return list(response.registers)

    async def _read_holding_registers(self, address: int, count: int) -> list[int]:
        await self._connect()
        response = await self._client.read_holding_registers(address=address, count=count, device_id=self._unit_id)
        if response.isError():
            raise AmtronApiError(f"Modbus read_holding_registers failed for 0x{address:04X}")
        return list(response.registers)

    async def _read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        await self._connect()
        response = await self._client.read_discrete_inputs(address=address, count=count, device_id=self._unit_id)
        if response.isError():
            raise AmtronApiError(f"Modbus read_discrete_inputs failed for 0x{address:04X}")
        return list(response.bits[:count])

    async def _write_holding_register(self, address: int, value: int) -> None:
        await self._connect()
        response = await self._client.write_register(address=address, value=value, device_id=self._unit_id)
        if response.isError():
            raise AmtronApiError(f"Modbus write_register failed for 0x{address:04X}")

    @staticmethod
    def _decode_uint32(low: int, high: int) -> int:
        return low | (high << 16)

    @staticmethod
    def _decode_ascii(registers: list[int]) -> str:
        raw = bytearray()
        for reg in registers:
            raw.append((reg >> 8) & 0xFF)
            raw.append(reg & 0xFF)
        return raw.split(b"\x00", maxsplit=1)[0].decode("ascii", errors="ignore").strip()

    async def get_device_info(self) -> dict[str, Any]:
        serial_low, serial_high = await self._read_input_registers(0x030B, 2)
        name_registers = await self._read_input_registers(0x0311, 12)
        mode_reg = (await self._read_input_registers(0x0306, 1))[0]
        phase_reg = (await self._read_input_registers(0x0308, 1))[0]
        error_reg = (await self._read_input_registers(0x0304, 1))[0]
        discrete = await self._read_discrete_inputs(0x0208, 4)

        return {
            "Sn": self._decode_uint32(serial_low, serial_high),
            "DevName": self._decode_ascii(name_registers) or f"Amtron {self._host}",
            "DevMode": _REGISTER_MODE_TO_DEV_MODE.get(mode_reg, "Remote"),
            "Phases": phase_reg,
            "Err": error_reg,
            "EmEnabled": bool(discrete[0]),
            "Auth": bool(discrete[3]),
            "AutoChg": bool((await self._read_discrete_inputs(0x020D, 1))[0]),
            "WifiOn": bool((await self._read_discrete_inputs(0x0211, 1))[0]),
            "ItemNo": "Modbus",
        }

    async def get_charge_data(self) -> dict[str, Any]:
        state_reg = (await self._read_input_registers(0x0305, 1))[0]
        session_low, session_high = await self._read_input_registers(0x030D, 2)
        power_low, power_high = await self._read_input_registers(0x030F, 2)
        remote_curr = (await self._read_holding_registers(0x0400, 1))[0]

        return {
            "ChgState": _REGISTER_STATE_TO_CHARGE_STATE.get(state_reg, "Unknown"),
            "ChgNrg": self._decode_uint32(session_low, session_high),
            "ActPwr": self._decode_uint32(power_low, power_high),
            "RemoteCurr": remote_curr,
            "ActCurr": remote_curr,
            "AutoChg": bool((await self._read_discrete_inputs(0x020D, 1))[0]),
        }

    async def get_statistics(self, period: str) -> dict[str, Any]:
        return {}

    async def set_charge_data(self, payload: Mapping[str, Any]) -> None:
        if (remote_curr := payload.get("RemoteCurr")) is not None:
            await self._write_holding_register(0x0400, int(remote_curr))

        if (chg_state := payload.get("ChgState")) is not None:
            code = _CHARGE_STATE_TO_REGISTER.get(str(chg_state))
            if code is None:
                raise AmtronApiError(f"Unsupported charge state for Modbus: {chg_state}")
            await self._write_holding_register(0x0401, code)

        if payload.get("RemoteCurr") is None and payload.get("ChgState") is None:
            raise AmtronApiError("This action is not supported via Modbus")

    async def set_device_info(self, payload: Mapping[str, Any]) -> None:
        raise AmtronApiError("Changing device info is not supported via Modbus")

    async def set_home_manager(self, payload: Mapping[str, Any]) -> None:
        raise AmtronApiError("Home Manager controls are not supported via Modbus")

    async def get_whitelist(self, state: str, pin: str | None = None) -> dict[str, Any]:
        raise AmtronApiError("Whitelist is not supported via Modbus")

    async def set_whitelist(self, payload: Mapping[str, Any], pin: str | None = None) -> None:
        raise AmtronApiError("Whitelist is not supported via Modbus")

    async def delete_whitelist(self, uid: str, pin: str | None = None) -> None:
        raise AmtronApiError("Whitelist is not supported via Modbus")

    async def get_charge_records(self, start_time: int, end_time: int) -> dict[str, Any]:
        raise AmtronApiError("Charge records are not supported via Modbus")
