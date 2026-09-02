# Building the firmware with the oven's own code frozen

## Why

The PyPortal has 256 kB of RAM and no more. Python module bytecode loaded
from the filesystem lives in that RAM; bytecode frozen into the CircuitPython
image executes from flash and costs almost nothing. Measured on this board:

| | free | largest block |
|---|---|---|
| all ten profiles loaded, libraries shadowed | 16 384 | 1 696 |
| one profile loaded | 30 352 | 4 912 |
| rate curves packed into arrays | 34 160 | — |
| shadowing libraries moved aside | 36 032 | 2 608 |
| **oven package frozen into the firmware** | **77 952** | **7 024** |

Nearly five times the memory it started with. The largest contiguous block
matters as much as the total: every render failure in this project was a
few hundred bytes failing against a heap with plenty free and no hole big
enough.

## The rule that makes it work, and breaks it

**A file on CIRCUITPY shadows the frozen copy of the same module.** That is
how you undo all of this without any error appearing: everything still
works, on a third of the memory.

So a frozen build requires the volume NOT to contain:

- `oven/` — the firmware's own package
- `adafruit_display_text`, `adafruit_esp32spi`, `adafruit_bus_device`,
  `adafruit_portalbase`, `adafruit_requests`, `neopixel` — these are frozen
  into the stock PyPortal firmware already, and the Adafruit bundle puts
  copies on the volume

`tools/deploy.py` refuses to deploy when any of the libraries reappear, and
skips `oven/` entirely when it sees the board is running a frozen build.
The displaced copies are kept in `.shadowed/` on the volume.

## Building

The build host needs ~3 GB of disk and an ARM toolchain; this project uses
eridani, since the Pi that talks to the oven has neither.

    # toolchain, no root required
    mkdir -p ~/toolchains && cd ~/toolchains
    curl -LO https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz
    tar xf arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz
    pip3 install --user cascadetoml

    # source, matching the version already on the board
    mkdir -p ~/build && cd ~/build
    git clone --depth 1 --branch 8.0.5 https://github.com/adafruit/circuitpython.git
    cd circuitpython && make fetch-submodules

    # the oven's code, and the line that freezes it
    rsync -a firmware/oven/ ~/build/circuitpython/frozen/BespokeToast/oven/
    echo 'FROZEN_MPY_DIRS += $(TOP)/frozen/BespokeToast' \
      >> ports/atmel-samd/boards/pyportal/mpconfigboard.mk

    export PATH=$HOME/.local/bin:$HOME/toolchains/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin:$PATH
    cd ports/atmel-samd && make -j24 BOARD=pyportal

Result: `build-pyportal/firmware.uf2`.

### One patch is required

GCC 13.2 is newer than CircuitPython 8.0.5 and its new diagnostics — a
dangling-pointer warning in `py/stackctrl.c` — are fatal under the port's
hardcoded `-Werror`. There is no `WERROR` knob and `CFLAGS_EXTRA` is applied
too early to override it, so the blanket flag is removed from
`ports/atmel-samd/Makefile`:

    -Wall -Werror -std=gnu11   ->   -Wall -std=gnu11

`-Werror=missing-prototypes` is deliberately left in place. The alternative
is to fetch a GCC contemporary with 8.0.5.

## Flashing

The bootloader can be entered without touching the board, which matters
because the USB port is behind a panel:

    import microcontroller
    microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
    microcontroller.reset()

The volume reappears as `PORTALBOOT`; copy the `.uf2` onto it and the board
reboots itself.

## Rolling back

Two levels, cheapest first.

1. **Move `oven/` back** from `.shadowed/` on the volume. The filesystem
   copy shadows the frozen one, so the board runs the old code again with no
   reflash. This is why the flash and the switch are separate steps.
2. **Reflash the stock image**, kept alongside the build:
   `adafruit-circuitpython-pyportal-en_US-8.0.5.uf2` from
   downloads.circuitpython.org.

If CircuitPython will not boot at all, the bootloader is in a protected
region and survives; entering it then needs a physical double-tap on reset,
which means opening the panel.

## What changes about day-to-day work

Editing anything under `firmware/oven/` no longer takes effect by deploying.
It needs a rebuild and a reflash. `code.py`, `profiles/`, `assets/` and
`characterisation.json` still deploy normally, which covers most changes.
