# Hardware

A toaster oven converted to a reflow soldering oven, controlled by an Adafruit
PyPortal.

No design documentation exists. Everything here was established by
inspecting the running device, and confirmed by the owner where marked. Claims
are tagged so it is clear what rests on what:

- **[observed]** — read directly off the device or host
- **[confirmed]** — confirmed by the owner
- **[spec]** — published board specification, not verified on this unit
- **[inferred]** — deduced from the firmware, not electrically confirmed
- **[unverified]** — assumed, still unconfirmed
- **[recorded]** — measured previously and recovered from this repository's
  history; conditions not fully documented

## Controller

| | |
|---|---|
| Board | Adafruit PyPortal **[observed]** |
| MCU | ATSAMD51J20 **[observed]** |
| USB ID | `239a:8036` **[observed]** |
| Board UID | `FCC166805943385320202046141E04FF` **[observed]** |
| CircuitPython | **8.0.5** (2023-03-31) **[observed]** |
| Serial | USB CDC console; enumerates as `Adafruit Industries LLC PyPortal` **[observed]** |
| Mass storage | 8 MB FAT volume, label `CIRCUITPY` **[observed]** |

The board also enumerates as a USB HID keyboard and mouse **[observed]**. It
sends no input, but it is capable of typing into whatever host it is connected
to.

## Mains switching

| | |
|---|---|
| Device | Mechanical relay **[confirmed]** |
| Control pin | `board.D4`, `digitalio` output, `True` energises **[observed]** |
| Connector | `D4` is one of the PyPortal's two 3-pin JST-PH connectors **[spec]** |
| Load | 120 VAC to the oven elements **[confirmed]** |

Roughly 20 actuations in a typical session **[confirmed]**. The firmware holds
the relay on continuously while the temperature error is large and only
modulates near setpoint, so it does not toggle once per control window.

Whether the relay de-energises when `D4` stops being driven depends on a
pulldown at the relay input. **[unverified]**

## Temperature sensing

| | |
|---|---|
| Device | MCP9600 thermocouple amplifier **[observed + confirmed]** |
| Thermocouple | Type **K** **[observed]** |
| I²C address | `0x67` (103 decimal) **[observed]** |
| Bus | `board.SCL` / `board.SDA` at 100 kHz **[observed]** |
| Driver | `adafruit_mcp9600` **[observed]** |

Probe placement inside the oven cavity is **[unverified]**, which leaves thermal
lag between element and probe unquantified.

## Measured thermal behaviour

A calibration run from 2023, recovered from this repository's history, measured
the oven's response to the relay opening. At a **100 °C** setpoint **[recorded]**:

| | |
|---|---|
| Overshoot after the relay opens | **≈29.6 °C** |
| Time to peak after the relay opens | **≈37 s** |

The procedure: heat until the setpoint is reached, open the relay, keep sampling
until the temperature stops rising. The resulting figures were stored as
`calibrate_temp` and `calibrate_seconds` in a configuration file the current
firmware no longer reads.

One data point, at one temperature, with ambient and load unrecorded — treat the
numbers as indicative rather than exact. What they establish is not in doubt:
this oven keeps heating substantially after power is removed. Any control scheme
that decides when to stop by looking only at the present temperature will
overshoot its peak.

## Display and input

- 320×240 2.4" TFT with resistive touch **[spec]**. The firmware reads
  `board.DISPLAY.width` / `.height` rather than hardcoding **[observed]**.
- The panel is full colour. The firmware uses a five-entry palette — black,
  white, red, green, blue **[observed]**.
- Touch calibration in use: `((5200, 59000), (5800, 57000))` **[observed]**.

## Physical installation

The PyPortal, the relay, and the associated wiring are housed together in a
small 3D-printed plastic enclosure, hardwired into the oven and sitting beside
it **[confirmed]**.

Consequences worth recording:

- **No plug to pull.** The oven is hardwired, so isolating it means a breaker or
  an upstream switch, not unplugging. Any procedure that assumes a plug can be
  yanked needs rewriting.
- **The NeoPixel is not visible** from outside the enclosure **[confirmed]**,
  which leaves the screen as the only visual indicator, and audio as the only
  non-visual one.
- **The enclosure sits next to a heat source.** Internal ambient will rise during
  a run by an unmeasured amount. Two consequences: the enclosure material's
  softening point is a limit nobody has characterised, and the MCP9600's
  cold-junction compensation assumes its die and the thermocouple terminals are
  at the same temperature — a thermal gradient across the enclosure introduces
  measurement error. Neither is quantified. **[unverified]**

## Fitted, not used by the firmware

ESP32 WiFi co-processor **[spec]** — `adafruit_esp32spi` and `adafruit_io` are on
the volume, but no `secrets.py` or `settings.toml` exists, so networking is
inactive **[observed]**. Also unused: microSD slot, speaker, light sensor, and
NeoPixel **[spec]** — the NeoPixel is in any case enclosed, see above.

## Connecting to the device

Over USB the board presents two interfaces:

- **Serial console / REPL** — a USB CDC device, conventionally `/dev/ttyACM*` on
  Linux. The stable path is under `/dev/serial/by-id/`, keyed by the board UID
  above, which does not move between reboots or ports. On most Linux systems the
  node is group `dialout`, so the account using it needs that membership.
- **`CIRCUITPY` volume** — a small FAT filesystem. Where it does not auto-mount,
  mount it read-only unless you intend to deploy:

  ```
  sudo mount -o ro,uid=$(id -u),gid=$(id -g) /dev/disk/by-label/CIRCUITPY /mnt/circuitpy
  ```

Opening the serial console does not reset the board. Toggling DTR at 1200 baud
puts it into the UF2 bootloader, so avoid that unless reflashing is intended.

## Open questions

1. Does the relay fail safe when `D4` stops being driven?
2. Where is the thermocouple mounted in the cavity?
3. Relay contact rating, and whether it switches one leg or both.
4. Is there an independent thermal cutout, or is the PyPortal the only control
   over the elements?
