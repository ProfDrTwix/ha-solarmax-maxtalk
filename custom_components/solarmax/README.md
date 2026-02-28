SolarMax Home Assistant custom integration

### Installation (manual)

1. Copy the `solarmax` folder into `custom_components` in your Home Assistant config directory (see https://github.com/ProfDrTwix/ha-solarmax-maxtalk for the canonical source).
2. Restart Home Assistant.

Configuration may be done either via YAML (legacy) or the UI config flow.  For general
information, see the [repository README](../../README.md) which also covers HACS usage.

**UI Setup**

Go to Settings → Devices & Services → Add Integration and search for "SolarMax". Provide a
name, host, port and scan interval (seconds); the port field is mandatory.  Specify one or
more device IDs (for daisy‑chained inverters you may add additional IDs).  Friendly names
for each device can be entered in the same order; missing names default to the numeric ID.
The integration generates the payload string automatically, so you don't need to enter it.

**YAML Example** (legacy)

```yaml
sensor:
  - platform: solarmax
    name: "SolarMax Inverters"
    host: 192.168.1.102
    port: 12345          # required
    # specify arbitrary number of IDs; optionally names too
    device_ids:
      - 64
      - 65
    device_names:
      - "Inverter East"
      - "Inverter West"
    scan_interval: 10    # seconds; defaults to 10
```

This integration exposes individual sensor entities for each SolarMax field (e.g. UDC, IDC, PAC). When you add multiple SolarMax devices, additional "SolarMax Combined" sensors will appear that sum data across all inverters for power and energy codes.
