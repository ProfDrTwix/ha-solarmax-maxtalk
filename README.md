# SolarMax Integration

Custom integration for Home Assistant that reads data from SolarMax inverters over TCP.

## Installation

### HACS (preferred)

1. In Home Assistant, go to **HACS → Integrations → (three dots menu) → Custom repositories**.
2. Add this repository URL (`https://github.com/ProfDrTwix/ha-solarmax-maxtalk`) with category **Integration** and click **Add**.
3. Wait for HACS to refresh, then install **SolarMax** from the Integrations view.
4. Restart Home Assistant and configure via Settings → Devices & Services. When adding the
  integration you must supply both the inverter `host` and `port`; the payload string is
  created automatically and does **not** need to be entered manually.

### Manual

Copy the `solarmax` directory from `custom_components` into your HA configuration's
`custom_components` folder and restart Home Assistant.

## Configuration

The integration supports both the UI config flow and the legacy YAML platform.  The
following paragraphs are reproduced from `custom_components/solarmax/README.md` and
describe the fields that must be supplied.

- **UI** – when adding the integration through Settings → Devices & Services you need to
  supply a `name`, the inverter `host` and `port` (both required) and a `scan_interval` in
  seconds. The payload string is generated internally from the configured device IDs.
-- **YAML** – use the sensor platform directly if you prefer configuration files.  You
  must supply at least one `device_id`; a second ID may be given for a daisy‑chained
  RS485 inverter.  The payload string is generated automatically by the integration:
  ```yaml
  sensor:
    - platform: solarmax
      name: "SolarMax Inverters"
      host: 192.168.1.102
      port: 12345  # required
      # device_ids can be a list or comma-separated string
      device_ids:
        - 64
        - 65
      # optionally provide friendly names in the same order
      device_names:
        - "Inverter East"
        - "Inverter West"
      scan_interval: 10       # seconds, default 10
  ```

Once the entry is created (via UI or YAML) the integration will instantiate one
`SensorEntity` for every field listed in `const.py` (codes such as `UDC`, `IDC`,
`PAC`), exposing scaled values based on `FIELD_DEFINITIONS`.  If more than one inverter
is configured, additional "SolarMax Combined" sensors automatically appear; these sum
selected codes across all coordinators.

Once configured, the integration creates one `SensorEntity` per field defined in
`const.py` (e.g. `UDC`, `IDC`, `PAC`).  If multiple entries are added, additional
"SolarMax Combined" sensors appear that sum selected codes across all inverters.

## Development

The repository is structured for HACS; the integration code lives under
`custom_components/solarmax`.  The official source is
https://github.com/ProfDrTwix/ha-solarmax-maxtalk.

There are no automatic tests.  To validate code locally, you can run a linter:

```bash
pip install flake8
flake8 custom_components/solarmax
```

Basic unit tests exist under `tests/` and are executed by the CI workflow; they
exercise payload generation and checksum logic.  Install `pytest` and run

```bash
pip install pytest
pytest
```

CI is provided via GitHub Actions (see `.github/workflows/ci.yml`) which currently
executes flake8 on every push and pull request.

For debugging in Home Assistant, enable logging for `solarmax` and inspect
`hass.data['solarmax']` for coordinators and their `.data` attribute.

### Protocol Reference

The integration implements the **MaxComm protocol** for SolarMax inverters. Payloads are
automatically generated from device IDs and the list of codes in `const.py`. The frame
format follows:

```
{FB;01;CC|DD:EEE|FFFF}
  FB   = Source address
  01   = Destination address
  CC   = Length of data section (hex)
  DD   = Port 64 (user data)
  EEE  = Codes to query (e.g. UDC;IDC;PAC)
  FFFF = Checksum (ASCII sum of everything before it)
```

For the complete protocol specification, refer to the SolarMax documentation on
MaxComm communication and payload structure.

## Contributing

- Update `FIELD_DEFINITIONS` in `const.py` when adding new codes; ensure unique IDs
  remain unique (`{base_name}_{code}` format).
- Follow existing patterns for adding platforms or services: store state in
  `hass.data[DOMAIN]` keyed by `entry.entry_id` and call
  `hass.config_entries.async_setup_platforms` from `async_setup_entry`.

## License

This project is licensed under the MIT License.  See `LICENSE` for details.
