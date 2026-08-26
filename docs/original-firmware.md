# The original firmware

How the controller worked before the rewrite. It no longer exists in this
tree; line references point at `firmware/code.py` as it stood at tag `v1`,
and `git show v1:firmware/code.py` still produces it.

How the controller in `firmware/` works. Line references point at
`firmware/code.py`.

## Structure

A single file built around one `Oven` class:

| method | role |
|---|---|
| `__init__` | relay pin, display, palette, fonts, graph bounds, MCP9600, touchscreen |
| `load_profile` | parses a profile from `reflow_profiles/` |
| `draw_line` / `draw_profile` | rasterises the target curve and grid into a `displayio.Bitmap` |
| `run_profile` | the control loop |
| `mainloop` | idle screen; waits for START |

The oven idles showing the target curve. Touching START runs the profile,
drawing the measured temperature over the target as it goes; touching the button
again stops the run.

## Control loop

Every one-second window the loop locates the active profile segment, linearly
interpolates the target temperature for the elapsed time, and forms the error
`tempDiff` (lines 312–327). Relay on-time for the window follows from the
squared error (lines 329–342):

```
if tempDiff > 0:  onTime = tempDiff**2 / 100   # clamped to 1.0 s
else:             onTime = 0
```

This is proportional control on squared error — no integral or derivative term,
and no feed-forward for the oven's thermal lag. When `onTime` saturates at a full
second the `skipOffTime` flag holds the relay on across consecutive windows
rather than dropping it out (lines 360–364), which is why a session shows on the
order of 20 actuations rather than one per second.

`tempOffset` (line 76) is a manual calibration offset applied to the error,
currently 0.

## Profiles

`firmware/reflow_profiles/<name>.txt`, one `time_s temperature_C` pair per line,
whitespace separated (lines 131–138).

| file | profile |
|---|---|
| `SAC305.txt` | lead-free: ramp to a 118–138 °C soak, peak **235 °C at 300 s**, 128 °C at 360 s |
| `SAC305_bu.txt` | the earlier profile, peak 225 °C |

`SAC305_bu.txt` is byte-identical to the profile in this repository's 2023
history, and `SAC305.txt` is that same profile with its three peak points raised
by 10 °C. The peak was lifted from 225 °C to 235 °C on the device and the
original kept alongside it. SAC305's liquidus is around 217–220 °C, so the
earlier profile cleared it by only a few degrees — which makes the change look
like a deliberate fix rather than an experiment.

Run length comes from `self.totalTime = 360` (line 59), which is set
independently of the profile file. A profile extending past that time is cut
short.

## Logging

None. `save_temp_log` is commented out (lines 226–233) and `reflow_logs/log.txt`
on the device is empty. No run data is recorded anywhere.

## Libraries on the device

Bundled Adafruit libraries, CircuitPython 8.x builds, at the volume root rather
than in `lib/`:

```
adafruit_bitmap_font    adafruit_portalbase     adafruit_mcp9600.mpy
adafruit_bus_device     adafruit_pyportal       adafruit_requests.mpy
adafruit_button         adafruit_register       adafruit_touchscreen.mpy
adafruit_display_shapes adafruit_esp32spi       neopixel.mpy
adafruit_display_text   adafruit_io
```

Plus `fonts/Px437_IBM_VGA_8x16-10-r.bdf`, used for all on-screen text.

These are not committed here — they are redistributable Adafruit builds. They
are compiled for CircuitPython 8.x and will not load on 9.x. `neopixel.mpy` is
present but never imported.

## CircuitPython version coupling

`display.show(group)` (line 40) was removed in CircuitPython 9. Moving the board
to 9.x or later requires changing that call to `display.root_group = group` and
replacing every `.mpy` above with a build matching the new version.

## Recovering earlier work

Two artifacts from this repository's history are worth knowing about. Neither is
carried in the tree — the tree records the oven as it is now — but both are one
command away:

| What | Where | Why it matters |
|---|---|---|
| `config.json` | `git show b23f1a4^:code/config.json` | Holds the measured coast figures, `calibrate_temp` and `calibrate_seconds`. See `hardware.md`. |
| `codecalibrate/code.py` | `git show b23f1a4^:code/codecalibrate/code.py` | The program that measured them: heat to setpoint, open the relay, log until the temperature stops rising. |

The earlier controller, before it was reduced to its current form, is at
`git show 3ad005f:code/code.py` — 897 lines, carrying a state machine, audio, and
a profile-selection screen that the current firmware does not have.

A JSON profile format also exists in the history, carrying alloy, melting point,
named stages, and a paste datasheet reference. No version of the firmware has
ever loaded it: the file is not valid JSON, and its declared melting point is
that of Sn63Pb37 rather than SAC305.

## Safety

The oven switches 120 VAC and the firmware is the only control over the elements
that has been identified. Its current safety characteristics:

- **No over-temperature limit.** Nothing bounds the commanded or measured
  temperature against an absolute maximum.
- **No sensor-fault detection.** An open, shorted, or disconnected thermocouple,
  or an I²C failure, is not checked. A fault reading low enlarges the error and
  increases relay on-time.
- **No watchdog.** If execution stalls with the relay energised, nothing
  independently turns it off.
- **No explicit safe state on stop.** Breaking out of the run loop (lines
  281–285) does not drive the relay pin false; the relay drops out via the pin
  being deinitialised on the next VM reset, which assumes a pulldown at the relay
  input.
- **Auto-reload is live during runs.** Writing any file to `CIRCUITPY` restarts
  `code.py` mid-run, with the relay in an undefined state.
