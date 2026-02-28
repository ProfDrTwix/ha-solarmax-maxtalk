"""SolarMax integration initializer."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SolarMaxCoordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # create coordinator and store in hass.data
    conf = entry.data
    name = conf["name"]
    host = conf["host"]
    port = conf.get("port")
    scan = conf.get("scan_interval")
    # device ids stored as list, fallback to legacy payload
    device_ids = conf.get("device_ids", [])
    device_names = conf.get("device_names", [])
    payload = conf.get("payload")

    from datetime import timedelta

    update_interval = timedelta(seconds=scan) if isinstance(scan, (int, float)) else scan

    coordinator = SolarMaxCoordinator(
        hass,
        name,
        host,
        port,
        update_interval,
        device_ids=device_ids,
        device_names=device_names,
        payload=payload,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
