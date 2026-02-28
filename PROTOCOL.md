# SolarMax MaxComm Protocol Reference

This document summarizes the protocol used by this integration based on the SolarMax MaxComm specification.

## Payload Frame Format

```
{FB;01;CC|DD:EEE|FFFF}
  FB   = Source address (always "FB")
  01   = Destination address (inverter address, typically "01")
  CC   = Length of data section in hex
  DD   = Port (64 hex = 100 decimal = user data read)
  EEE  = Semicolon-separated list of code names to query
  FFFF = Checksum (sum of ASCII values of FB;01;CC|DD:EEE|)
```

## Example

Query device 64 for DC voltage, current, and AC output:

```
{FB;01;10|64:UDC;IDC;PAC|1A45}
```

Where:
- Data section `|64:UDC;IDC;PAC|` is 16 characters
- Length `10` is hex (16 decimal)
- Checksum `1A45` is the sum of ASCII codes for `FB;01;10|64:UDC;IDC;PAC|`

## Available Codes

The integration supports the following codes (from `const.py`). See the SolarMax protocol documentation for meanings and conversion factors.

### Voltage & Current
- `UDC` – DC Voltage (V, scale 0.1)
- `IDC` – DC Current (A, scale 0.01)
- `UL1` – AC Voltage (V, scale 0.1)
- `IL1` – AC Current (A, scale 0.01)

### Power & Energy
- `PAC` – AC Output (W, scale 0.5)
- `PRL` – AC Output relative (%, no scale)
- `PIN` – Capacity installed (W, scale 0.5)
- `KDY` – Energy today (kWh, scale 0.1)
- `KLD` – Energy yesterday (kWh, scale 0.1)
- `KMT` – Energy this month (kWh, no scale)
- `KLM` – Energy last month (kWh, no scale)
- `KYR` – Energy this year (kWh, no scale)
- `KLY` – Energy last year (kWh, no scale)
- `KT0` – Energy total (kWh, no scale)

### System State
- `TNF` – AC Frequency (Hz, scale 0.01)
- `TKK` – Temperature (°C, no scale)
- `SYS` – Operating Mode (code, no scale)
- `KHR` – Operating Hours (h, no scale)
- `CAC` – Start-ups (count, no scale)

### Device Info
- `TYP` – Type (code, no scale)
- `SWV` – Software Version (no scale)
- `BDN` – Build Number (no scale)
- `ADR` – Network Address (no scale)

### Date/Time
- `DDY` – Date day (no scale)
- `DMT` – Date month (no scale)
- `DYR` – Date year (no scale)
- `TMI` – Time minute (no scale)
- `THR` – Time hour (no scale)

### Newer Inverters (if available)
- `DATE` – Date (combined, format TBD)
- `TIME` – Time (combined, format TBD)
- `TNP` – Grid period duration (µs, format TBD)

## Operating Modes (SYS Code)

- `20004` – Operating at MPP (maximum power point)
- `20008` – Grid operation

(Full list available in protocol documentation)

## Checksum Calculation

The checksum is computed as the sum of ASCII values of all characters in the frame before the CRC field:

```
crc_input = "FB;01;CC|DD:EEE|"
checksum = sum(ord(c) for c in crc_input)
checksum_hex = f"{checksum:04X}"
```

## Multi-Device Setup

To query two inverters on the same RS485 bus:

1. Configure device IDs (e.g. 64 and 65) in the integration settings.
2. The integration sends separate queries for each device sequentially.
3. Response codes are namespaced by device ID (e.g. `64_UDC`, `65_UDC`).
4. Combined sensors sum across all device IDs when multiple entries are configured.

## References

- MaxComm Protocol Specification (SolarMax)
- Payload format: {FB;01;82|...} where 82 is the length in hex
