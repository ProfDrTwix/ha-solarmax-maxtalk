"""Sensor platform for SolarMax inverters."""
from __future__ import annotations

import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_PAYLOAD,
    CONF_SCAN_INTERVAL,
)
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, FIELD_DEFINITIONS, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL
from .coordinator import SolarMaxCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # legacy yaml setup
    # validate configuration values and apply defaults
    yaml_schema = vol.Schema(
        {
            vol.Required(CONF_NAME): cv.string,
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            vol.Required("device_id"): cv.string,
            vol.Optional("device_id_2"): cv.string,
            vol.Optional(CONF_PAYLOAD): cv.string,
        }
    )
    config = yaml_schema(config)
    name = config[CONF_NAME]
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    scan = config[CONF_SCAN_INTERVAL]
    payload = config.get(CONF_PAYLOAD)

    update_interval = scan if isinstance(scan, timedelta) else timedelta(seconds=int(scan))

    # compute device id list and optionally allow raw payload override
    device_ids = [config["device_id"]]
    if config.get("device_id_2"):
        device_ids.append(config["device_id_2"])
    payload = config.get(CONF_PAYLOAD)
    coordinator = SolarMaxCoordinator(
        hass,
        name,
        host,
        port,
        update_interval,
        device_ids=device_ids,
        payload=payload,
    )
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for dev in device_ids:
        for code, meta in FIELD_DEFINITIONS.items():
            entities.append(SolarMaxSensor(coordinator, name, dev, code, meta))

    async_add_entities(entities, update_before_add=False)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["solarmax"][entry.entry_id]
    name = entry.title
    # sensors for each device id; use provided device_names if available
    entities = []
    ids = getattr(coordinator, "device_ids", [None])
    names = getattr(coordinator, "device_names", [])
    for idx, dev in enumerate(ids):
        dev_name = names[idx] if idx < len(names) else dev
        for code, meta in FIELD_DEFINITIONS.items():
            entities.append(SolarMaxSensor(coordinator, name, dev, dev_name, code, meta))
    async_add_entities(entities, update_before_add=False)

    # if more than one entry, also create combined sensors for certain fields
    all_coordinators = hass.data.get("solarmax", {})
    if len(all_coordinators) > 1:
        # define which codes to aggregate and if we need special availability logic
        aggregate_codes = ["PAC", "KDY", "KLD", "KMT", "KLM", "KYR", "KLY", "KT0", "PIN"]
        combined_name = "SolarMax Combined"
        combined_entities = []
        for code in aggregate_codes:
            combined_entities.append(CombinedSolarMaxSensor(hass, combined_name, code))
        async_add_entities(combined_entities, update_before_add=False)


class SolarMaxSensor(SensorEntity):
    def __init__(
        self,
        coordinator: SolarMaxCoordinator,
        base_name: str,
        device_id: str | None,
        device_name: str | None,
        code: str,
        meta: dict,
    ):
        self.coordinator = coordinator
        self._device_id = device_id
        # friendly name for this inverter
        self._device_name = device_name
        self._code = code
        self._meta = meta
        # include device id in name/unique_id when present
        suffix = f" ({device_name or device_id})" if device_id else ""
        self._attr_name = f"{base_name}{suffix} {code} {meta['name']}"
        unique = (
            f"{base_name}_{device_name}_{code}" if device_name
            else f"{base_name}_{device_id}_{code}"
        ) if device_id else f"{base_name}_{code}"
        self._attr_unique_id = unique.replace(" ", "_")
        self._attr_native_unit_of_measurement = meta.get("unit")
        self._attr_device_class = meta.get("device_class")
        self._attr_state_class = meta.get("state_class")
        # associate with a device using host
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": base_name,
            "model": "SolarMax Inverter",
            "manufacturer": "SolarMax",
            "sw_version": None,
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        parsed = data.get("parsed", {})
        key = f"{self._device_id}_{self._code}" if self._device_id else self._code
        raw = parsed.get(key)
        if raw is None:
            return None
        scale = self._meta.get("scale", 1)
        try:
            return raw * scale
        except Exception:
            return raw

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()


class CombinedSolarMaxSensor(SensorEntity):
    """Sensor representing the sum of a particular code across all coordinators."""

    def __init__(self, hass, base_name: str, code: str):
        self.hass = hass
        self._code = code
        self._attr_name = f"{base_name} {code}"
        self._attr_unique_id = f"combined_{code}"
        # inherit attributes from FIELD_DEFINITIONS
        meta = FIELD_DEFINITIONS.get(code, {})
        self._attr_device_class = meta.get("device_class")
        self._attr_native_unit_of_measurement = meta.get("unit")
        self._attr_state_class = meta.get("state_class")

    @property
    def available(self) -> bool:
        # available if any coordinator has data
        for coord in self.hass.data.get("solarmax", {}).values():
            # if any parsed value exists for this code (with or without id)
            data = coord.data or {}
            parsed = data.get("parsed", {})
            for key in parsed:
                if key == self._code or key.endswith(f"_{self._code}"):
                    if coord.last_update_success:
                        return True
