"""Config flow for SolarMax integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
# callback not used
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# helper for list of strings (allows comma-separated or YAML list)
list_of_str = vol.All(cv.ensure_list, [cv.string])

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        # port is mandatory for every configuration
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        # arbitrary number of device IDs and optional matching names
        vol.Required("device_ids"): list_of_str,
        vol.Optional("device_names"): list_of_str,
    }
)


class SolarMaxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            data = dict(user_input)
            # normalize device_ids and device_names to lists of strings
            ids = [s.strip() for s in data.get("device_ids", [])]
            names = [s.strip() for s in data.get("device_names", [])] if data.get("device_names") else []
            # ensure names list length matches ids; fall back to the ID value
            while len(names) < len(ids):
                names.append(ids[len(names)])
            data["device_ids"] = ids
            data["device_names"] = names
            return self.async_create_entry(title=user_input[CONF_NAME], data=data)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
