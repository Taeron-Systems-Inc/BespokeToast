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

**The relay fails safe [measured].** Reading `D4` back as an input under each
internal pull returns `False` under both pull-up and pull-down, so an external
pulldown dominates and the relay is de-energised whenever the pin is not
driven. Reproduced identically on three separate runs.

This matters beyond the obvious: CircuitPython releases pins whenever the VM
exits, so high-Z on `D4` occurs on every reset, every `Ctrl-C` and every
auto-reload. All of those are safe.

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

Two step tests were run on 2026-08-25, empty oven, logged at 2 Hz. Raw data
is in `data/`.

| | **[measured]** |
|---|---|
| Heating, 26 → 200 °C | 143 s |
| Heating, 53 → 240 °C | 177 s |
| Peak heating rate | **1.85 °C/s at 80 °C** |
| Heating rate at 200 °C | **0.90 °C/s** |
| Passive cooling at 190 °C, door shut | **−0.70 °C/s** |
| Coast after relay opens, from 200 °C | **1.06 °C over 3 s** |
| Coast after relay opens, from 240 °C | **0.56 °C over 2 s** |
| Enclosure cold junction, peak | 41.8 °C |
| CPU die, peak | 36.2 °C |

Three things follow.

**The oven is not a first-order system.** Its heating rate *rises* to a peak
near 80 °C rather than decaying from the start, and its heating and cooling
time constants differ by roughly 2.5×. A fitted first-order-plus-dead-time
model gave a 20 s dead time, which predicts about 17 °C of coast — sixteen
times what was measured. The model is not used; the measured curves are.

**The oven's capability falls as it gets hotter, and reflow needs it hottest.**
1.85 °C/s at 80 °C but 0.90 °C/s at 200 °C. Both available profiles demand
their fastest rise in the spike zone, where the oven is weakest.

**Cooling cannot follow any reflow profile with the door shut**, at −0.70 °C/s
against the 1.3–2.0 °C/s profiles ask for.

### The 2023 figure was wrong

A calibration recovered from this repository's history recorded 29.6 °C of
overshoot over 37 s at a 100 °C setpoint. The measurement above is 1.06 °C
over 3 s — smaller by a factor of 28. Whatever that run measured, it does not
describe this oven. It is recorded here only so nobody re-derives anything
from it.

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
