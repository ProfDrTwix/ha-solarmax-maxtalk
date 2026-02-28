"""Coordinator to fetch data from SolarMax inverter over TCP."""
import asyncio
import logging
import re
from typing import Dict, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import FIELD_DEFINITIONS


_FIELD_RE = re.compile(r"([A-Z0-9]{2,4})=([0-9A-F]+)")


class SolarMaxCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: int,
        update_interval,
        device_ids: list[str] | None = None,
        device_names: list[str] | None = None,
        payload: str | None = None,
    ):
        # use logger from module
        super().__init__(hass, logging.getLogger(__name__), name=name, update_interval=update_interval)
        self.host = host
        self.port = port
        self.name = name
        # list of one or two device ids on the RS485 chain
        self.device_ids = device_ids or []
        # names corresponding to each device id; default to id if not given
        self.device_names = device_names or []
        # allow a raw payload string to be supplied for backwards compatibility
        self._raw_payload = payload
        self._raw = ""

    async def _async_update_data(self) -> Dict[str, Any]:
        # The SolarMax protocol expects a specific payload string; if the caller
        # passed a raw payload we just send that once.  Otherwise build one or
        # two query messages based on ``self.device_ids`` and merge the results.
        parsed: Dict[str, int] = {}
        raw_accum = []

        async def _send_query(payload_str: str) -> str:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=5)
            writer.write(payload_str.encode())
            await writer.drain()
            try:
                data = await asyncio.wait_for(reader.read(4096), timeout=5)
            except asyncio.TimeoutError:
                data = b""
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return data.decode(errors="ignore") if data else ""

        try:
            if self._raw_payload:
                # legacy behaviour
                text = await _send_query(self._raw_payload)
                raw_accum.append(text)
                target_ids = [None]
            else:
                target_ids = self.device_ids or []
                # generate a query string for each ID and send sequentially
                for dev in target_ids:
                    payload_str, _ = self._build_frame(dev)
                    text = await _send_query(payload_str)
                    raw_accum.append(text)
            self._raw = "\n".join(raw_accum)

            # parse all responses; if multiple device ids we prefix the codes
            # with the id to keep them distinct.
            for text in raw_accum:
                for m in _FIELD_RE.finditer(text):
                    code = m.group(1)
                    value = m.group(2)
                    key = code
                    # if we have multiple ids, attempt to detect which id the
                    # response came from by looking for the ID prefix in the
                    # text; fallback to code alone if unknown.
                    for dev in target_ids:
                        if dev and f"{dev}" in text:
                            key = f"{dev}_{code}"
                            break
                    try:
                        parsed[key] = int(value, 16)
                    except ValueError:
                        parsed[key] = None

            return {"raw": self._raw, "parsed": parsed}

        except Exception as err:
            raise UpdateFailed(err)

    def _build_frame(self, device_id: str) -> tuple:
        """Build the complete payload frame for a given device id.

        Returns (payload_string, crc_hex).
        See protocol documentation section 05 (Payload creation) for frame structure:
        {FB;01;CC|DD:EEE|FFFF}
          FB = Source address
          01 = Destination address
          CC = Length of data section in hex
          DD = Port (64 = user data)
          EEE = Codes to query
          FFFF = Checksum (sum of ASCII values before CRC)
        """
        codes = ";".join(FIELD_DEFINITIONS.keys())
        # Data portion: |ID:codes|
        data_section = f"|{device_id}:{codes}|"
        # Length of data section in hex (2 digits)
        length_hex = f"{len(data_section):02X}"
        # Header: FB;01;CC where CC is the length in hex
        header = f"FB;01;{length_hex}"
        # Everything that gets checksummed (no outer braces, no CRC yet)
        crc_input = header + data_section
        # Checksum is sum of ASCII values (protocol section 05.05)
        crc_val = sum(ord(c) for c in crc_input)
        crc_hex = f"{crc_val:04X}"
        # Complete frame with braces
        payload = f"{{{crc_input}{crc_hex}}}"
        return payload, crc_hex
