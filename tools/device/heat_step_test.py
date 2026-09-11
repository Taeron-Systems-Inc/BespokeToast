# SPDX-License-Identifier: MIT
"""THIS ONE HEATS THE OVEN. Every other tool in this directory cannot.

`simulate.py`, `soak.py`, `bake.py`, `faults.py` and `touchtest.py` all
deliberately avoid importing `oven.hardware`, so the relay pin is never
claimed and no amount of misuse can make heat. This one claims it on
purpose, because identifying a plant needs the plant.

It will not run on import. It runs when someone calls `main()` with the
confirmation token, which exists so that reading the file on the board --
`import heat_step_test` -- cannot start a fire:

    import heat_step_test as h
    h.main(h.IDENTIFY_60_TO_240, confirm=h.CONFIRM)

## What it is for

The control loop's feed-forward inverts a plant model built from step tests
where duty was almost always 0 or 1. That is poor excitation: it pins down
the steady-state rate at each temperature, which is what the rate tables
are, and says very little about the DYNAMICS -- how long the element takes
to charge, which is the state the model is missing and the reason a warm
start lags 24-32 C.

So this drives duty directly on a schedule, holding a plateau and then
stepping around it, at several temperatures. One heating cycle gives the
local dynamics at every operating point it visits, which six profile runs
did not.

## What keeps it safe

Three independent things, and they are in this order deliberately.

1. **The schedule's own ceiling.** Every step carries a temperature above
   which its duty is forced to zero. This is inside the experiment: it is
   what stops an open-loop schedule going somewhere the author did not
   predict, and it acts long before anything else notices.
2. **The supervisor**, unmodified and running every step -- 260 C hard
   ceiling, 70 C enclosure, rate and stall guards. A fault ends the run and
   drives the relay low. It is a backstop, not the plan.
3. **A wall-clock limit** on the whole schedule, and `finally: relay.off()`
   around everything, so a crash, a KeyboardInterrupt or a host that walks
   away all end with the element de-energised.

The relay also has a hardware pulldown, which is what held when a run
crashed before the exit handler existed.

## Output

CSV on the console at the control cadence, same shape the firmware prints so
the same tools read it:

    t,state,temp_c,target_c,duty,relay,cold_c,cpu_c

`target_c` is blank -- there is no target, that is the point -- and `duty` is
what the schedule asked for, which is the input signal an identification
needs and which the oven's own run logs do not carry.
"""

import time

import board

from oven import hal
from oven.controller import TimeProportional
from oven.hardware import Hardware, cpu_temperature
from oven.safety import Supervisor, Limits

CONFIRM = "yes, heat the oven"

DT = 0.25
SETTLE_PRINT_S = 0.25


class Step(object):
    """Hold *duty* for *seconds*, but never above *ceiling_c*.

    __slots__ because this runs on a board with 60 kB of heap and a long
    schedule is a lot of little objects.
    """

    __slots__ = ("seconds", "duty", "ceiling_c", "label", "until_ceiling")

    def __init__(self, seconds, duty, ceiling_c, label="",
                 until_ceiling=False):
        if not 0.0 <= duty <= 1.0:
            raise ValueError("duty %r is not in 0..1" % (duty,))
        if ceiling_c > 250.0:
            raise ValueError(
                "ceiling %r is above what this oven has been characterised "
                "to; the supervisor stops at 260 and that is a backstop, not "
                "a plan" % (ceiling_c,))
        self.seconds = float(seconds)
        self.duty = float(duty)
        self.ceiling_c = float(ceiling_c)
        self.label = label
        # A climb ends when it arrives, not when its budget runs out. Without
        # this a schedule spends most of itself sitting at duty 0 above a
        # ceiling it reached in a fifth of the time it was given.
        self.until_ceiling = bool(until_ceiling)


# Element charge time constant, from tools/identify_plant.py across four
# runs. Used only to decide where a climb should stop.
ELEMENT_TAU_S = 14.0

# Full-power heating rate by temperature, the measured table thinned to what
# this needs. A charged element stores about rate * tau of further rise.
_HEAT_RATE = ((60.0, 1.69), (100.0, 1.75), (150.0, 1.29), (195.0, 0.96),
              (235.0, 0.69), (250.0, 0.56))


def _coast_margin(temp_c):
    rate = _HEAT_RATE[-1][1]
    for t, r in _HEAT_RATE:
        if temp_c <= t:
            rate = r
            break
    return rate * ELEMENT_TAU_S


def _plateau(setpoint_c, hold_duty, settle_s, amplitude, cycles, half_s,
             label):
    """Arrive at a plateau, settle, then square-wave the duty around it.

    The square wave is what carries the dynamics. Amplitude is small on
    purpose: a big step moves the operating point, and what comes back is
    then an average of the dynamics either side of it rather than the
    dynamics where the step started.

    The ceiling sits ABOVE the plateau, not on it. Held open loop at a duty
    that is only exactly right at one temperature, the oven drifts -- which
    is fine, and is information, as long as the drift is not clamped. A
    ceiling equal to the setpoint would force duty to zero on every upward
    half cycle and the excitation would be of the ceiling, not the oven.
    """
    # Capped, not just offset: the first run of this refused itself, because
    # 235 + 20 is 255 and the Step limit is 250. The limit was right and the
    # schedule was wrong. 15 C of headroom at the top plateau is enough for
    # a +/-0.15 duty square wave, which drifts a few degrees, not fifteen.
    ceiling = min(setpoint_c + 20.0, 250.0)
    # The climb stops SHORT of the plateau and the element carries the oven
    # the rest of the way. Stopping at the plateau itself put the first run
    # 22 C past it -- a saturated element stores that much -- so the whole
    # settle window sat above the ceiling with the excitation clamped. The
    # margin is the heating rate at that temperature times the element time
    # constant, which is what a charged element has left to give:
    #   60 C:  1.7 C/s * 14 s = 24 C   (measured coast was 22)
    #  235 C:  0.69     * 14 =  10 C
    stop_at = setpoint_c - _coast_margin(setpoint_c)
    out = [Step(600.0, 1.0, stop_at, "climb to %s" % label,
                until_ceiling=True),
           Step(settle_s, hold_duty, ceiling, "%s settle" % label)]
    for i in range(cycles):
        out.append(Step(half_s, min(1.0, hold_duty + amplitude), ceiling,
                        "%s up %d" % (label, i + 1)))
        out.append(Step(half_s, max(0.0, hold_duty - amplitude), ceiling,
                        "%s down %d" % (label, i + 1)))
    return out


def identification_schedule():
    """Plateaux at 60, 100, 150, 195 and 235 C, each with a duty square wave.

    Hold duties come from the measured table (u = -c/(h-c)); the climb
    between plateaux is full power with the ceiling doing the stopping,
    which is also a clean step response in its own right.

    About 50 minutes, ending hot. The cooldown that follows is free data:
    with the relay off it is a passive-cooling measurement across the whole
    range.
    """
    plan = []
    for setpoint, hold, label in ((60.0, 0.043, "60C"),
                                  (100.0, 0.079, "100C"),
                                  (150.0, 0.213, "150C"),
                                  (195.0, 0.433, "195C"),
                                  (235.0, 0.526, "235C")):
        plan.extend(_plateau(setpoint, hold, 180.0, 0.15, 3, 60.0, label))
    plan.append(Step(1800.0, 0.0, 30.0, "free cooling"))
    return plan


IDENTIFY_60_TO_240 = identification_schedule


def main(schedule=None, confirm=None, max_total_s=9000.0):
    """Run *schedule*. Returns the fault that ended it, or None."""
    if confirm != CONFIRM:
        print("# refused: this tool heats the oven. Pass confirm=CONFIRM.")
        return "not confirmed"
    steps = schedule() if callable(schedule) else schedule
    if not steps:
        print("# refused: empty schedule")
        return "empty"

    # Worst case: climbs are budgeted for the time they would take if they
    # never arrived, and in practice end far sooner.
    planned = sum(s.seconds for s in steps)
    if planned > max_total_s:
        print("# refused: schedule is %.0f s, limit is %.0f"
              % (planned, max_total_s))
        return "too long"

    hw = Hardware()
    sup = Supervisor(Limits())
    tpo = TimeProportional()
    started = hw.clock.monotonic()
    sup.begin_run(started, expected_duration_s=planned)
    tpo.reset(started)
    fault = None
    print("# heat step test, %d steps, %.0f s planned" % (len(steps), planned))
    print("# t,state,temp_c,target_c,duty,relay,cold_c,cpu_c")
    try:
        for step in steps:
            ends = hw.clock.monotonic() + step.seconds
            print("# step %s: duty %.3f, ceiling %.0f C, %.0f s"
                  % (step.label, step.duty, step.ceiling_c, step.seconds))
            arrived = False
            while hw.clock.monotonic() < ends and not arrived:
                now = hw.clock.monotonic()
                if now - started > max_total_s:
                    print("# stopping: wall clock limit")
                    return "wall clock"
                reading = hw.sensor.read()
                fault = sup.update(now, reading, hw.relay.is_on())
                if fault is not None:
                    print("# FAULT %s: %s" % (fault.kind, fault.message))
                    return fault
                temp = reading.hot if reading else None
                if temp is None:
                    duty = 0.0
                elif temp >= step.ceiling_c:
                    duty = 0.0
                    arrived = step.until_ceiling
                else:
                    duty = step.duty
                hw.relay.set(tpo.update(now, duty))
                print("%.2f,steptest,%s,,%.3f,%d,%s,%.2f"
                      % (now, "" if temp is None else "%.4f" % temp, duty,
                         1 if hw.relay.is_on() else 0,
                         "" if reading is None else "%.2f" % reading.cold,
                         cpu_temperature()))
                # Busy-wait rather than sleep: the point is a fixed cadence,
                # and sleep() on this board drifts under print load.
                while hw.clock.monotonic() - now < DT:
                    pass
        return None
    finally:
        # Whatever happened -- a fault, a stop, an interrupt, an exception --
        # the element is de-energised before this returns.
        try:
            hw.relay.off()
        except Exception as e:
            print("# WARNING could not drive the relay low (%r)" % e)
        print("# heat step test ended, relay off")
