import pytest

import sys
import os
import types

# ensure the project root (workspace) is on sys.path so we can import
# `custom_components` as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# homeassistant is not a dependency of the test runner; stub minimal submodules so
# importing the integration doesn't fail.  We only need the classes used for typing.
ha = types.ModuleType("homeassistant")
core = types.ModuleType("homeassistant.core")
update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")

# additional stubs for components imported by sensor.py
components = types.ModuleType("homeassistant.components")
sensor_mod = types.ModuleType("homeassistant.components.sensor")
const_mod = types.ModuleType("homeassistant.const")

# helper stub for DataUpdateCoordinator so that inheriting from it doesn't try to
# call object.__init__ directly (which would raise a TypeError).
class _DummyCoordinator:
    def __init__(self, hass, logger, name=None, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
config_entries = types.ModuleType("homeassistant.config_entries")
setattr(core, "HomeAssistant", object)
setattr(update_coordinator, "DataUpdateCoordinator", _DummyCoordinator)
setattr(update_coordinator, "UpdateFailed", Exception)
setattr(config_entries, "ConfigEntry", object)
setattr(sensor_mod, "SensorEntity", object)
setattr(const_mod, "CONF_NAME", "name")
setattr(const_mod, "CONF_HOST", "host")
setattr(const_mod, "CONF_PORT", "port")
setattr(const_mod, "CONF_PAYLOAD", "payload")
setattr(const_mod, "CONF_SCAN_INTERVAL", "scan_interval")
sys.modules["homeassistant"] = ha
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.sensor"] = sensor_mod
sys.modules["homeassistant.const"] = const_mod
# stub helpers.config_validation
helpers = types.ModuleType("homeassistant.helpers")
config_validation = types.ModuleType("homeassistant.helpers.config_validation")
config_validation.string = lambda v: v
config_validation.port = lambda v: v
config_validation.positive_int = lambda v: v
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.config_validation"] = config_validation

from custom_components.solarmax.coordinator import SolarMaxCoordinator
from custom_components.solarmax.const import FIELD_DEFINITIONS


def test_payload_generation():
    # create coordinator with dummy values; hass not used for this helper
    coord = SolarMaxCoordinator(None, "name", "host", 12345, 1, device_ids=["64"], device_names=["Primary"])
    payload, crc_hex = coord._build_frame("64")
    # payload should be {FB;01;CC|64:codes|FFFF}
    assert payload.startswith("{FB;01;")
    assert "|64:" in payload
    assert payload.endswith(f"|{crc_hex}}}")
    # verify CRC is 4 hex digits
    assert len(crc_hex) == 4
    # verify CRC is just sum of ASCII values (not including length offset)
    crc_input = payload[1:-5]  # strip { and |FFFF}
    expected_crc = sum(ord(c) for c in crc_input)
    assert int(crc_hex, 16) == expected_crc


def test_sensor_naming():
    # verify that sensors include device names when provided
    class DummyCoord:
        host = "1.2.3.4"
        last_update_success = True
        data = {"parsed": {"64_UDC": 100}}

    coord = DummyCoord()
    meta = FIELD_DEFINITIONS["UDC"]
    sensor = __import__("custom_components.solarmax.sensor", fromlist=["SolarMaxSensor"]).SolarMaxSensor(
        coord, "Base", "64", "East", "UDC", meta
    )
    # stub SensorEntity doesn't implement properties, inspect raw attributes
    assert "East" in sensor._attr_name
    assert "Base_East_UDC" in sensor._attr_unique_id
    assert sensor.native_value == pytest.approx(100 * meta["scale"])
