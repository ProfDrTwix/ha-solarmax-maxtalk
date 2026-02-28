# flake8: noqa: E501
"""Constants for SolarMax integration."""

DOMAIN = "solarmax"
DEFAULT_PORT = 12345
DEFAULT_SCAN_INTERVAL = 10

# Field definitions mapping code -> properties
# scale is multiplied to the raw integer value
FIELD_DEFINITIONS = {
    "UDC": {"name": "DC Voltage", "device_class": "voltage", "unit": "V", "state_class": "measurement", "scale": 0.1},
    "IDC": {"name": "DC Current", "device_class": "current", "unit": "A", "state_class": "measurement", "scale": 0.01},
    "UL1": {"name": "AC Voltage", "device_class": "voltage", "unit": "V", "state_class": "measurement", "scale": 0.1},
    "IL1": {"name": "AC Current", "device_class": "current", "unit": "A", "state_class": "measurement", "scale": 0.01},
    "PAC": {"name": "AC Output", "device_class": "power", "unit": "W", "state_class": "measurement", "scale": 0.5},
    "PRL": {"name": "AC Output (relative)", "device_class": None, "unit": "%", "state_class": "measurement", "scale": 1},
    "TNF": {"name": "AC Frequency", "device_class": "frequency", "unit": "Hz", "state_class": "measurement", "scale": 0.01},
    "KDY": {"name": "Energy (today)", "device_class": "energy", "unit": "kWh", "state_class": "total_increasing", "scale": 0.1},
    "KLD": {"name": "Energy (yesterday)", "device_class": "energy", "unit": "kWh", "state_class": "total", "scale": 0.1},
    "KMT": {"name": "Energy (this month)", "device_class": "energy", "unit": "kWh", "state_class": "total_increasing", "scale": 1},
    "KLM": {"name": "Energy (last month)", "device_class": "energy", "unit": "kWh", "state_class": "total", "scale": 1},
    "KYR": {"name": "Energy (this year)", "device_class": "energy", "unit": "kWh", "state_class": "total_increasing", "scale": 1},
    "KLY": {"name": "Energy (last year)", "device_class": "energy", "unit": "kWh", "state_class": "total", "scale": 1},
    "KT0": {"name": "Energy (total)", "device_class": "energy", "unit": "kWh", "state_class": "total_increasing", "scale": 1},
    "TKK": {"name": "Temperature (inverter)", "device_class": "temperature", "unit": "°C", "state_class": "measurement", "scale": 0.5},
    "SYS": {"name": "Operating Mode", "device_class": None, "unit": None, "state_class": "measurement", "scale": 1},
    "KHR": {"name": "Operating Hours", "device_class": "duration", "unit": "h", "state_class": "total", "scale": 1},
    "CAC": {"name": "Start-ups", "device_class": None, "unit": None, "state_class": "total", "scale": 1},
    "TYP": {"name": "Type", "device_class": None, "unit": None, "state_class": "measurement", "scale": 1},
    "SWV": {"name": "Software Version", "device_class": None, "unit": None, "state_class": "measurement", "scale": 1},
    "BDN": {"name": "Build Number", "device_class": None, "unit": None, "state_class": "measurement", "scale": 1},
    "ADR": {"name": "Network Address", "device_class": None, "unit": None, "state_class": "measurement", "scale": 1},
    "PIN": {"name": "Capacity (installed)", "device_class": "power", "unit": "W", "state_class": "measurement", "scale": 0.5},
}
