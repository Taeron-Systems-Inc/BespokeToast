# SPDX-License-Identifier: MIT
"""The run state machine and the scheduler that drives it.

Two things this module exists to get right.

**Control cadence is not negotiable.** The previous firmware refreshed the
display inside its control loop, so every redraw stretched the control step.
Here ``tick`` is called as fast as the caller likes, but the control step
fires on a fixed 250 ms schedule measured against a monotonic clock, and
rendering happens with whatever time is left. If a redraw overruns, the next
control step is late by that much and the supervisor sees it -- which is
exactly what its stale-reading guard is for.

**Nothing heats without the supervisor.** The controller proposes a duty; the
supervisor holds a veto; the relay is only ever driven with both in agreement.
There is no path from profile to relay that bypasses it.

Pure stdlib -- runs on the device and under CPython for tests.
"""

from . import metrics
from .safety import Supervisor

STATE_IDLE = "idle"
STATE_PREHEAT = "preheat"
STATE_RUNNING = "running"
STATE_COOLDOWN = "cooldown"
STATE_REPORT = "report"
STATE_FAULT = "fault"

CONTROL_INTERVAL_S = 0.25

# How close to the profile's starting temperature the oven must be before the
# clock starts. Beginning a run from an arbitrary temperature is the largest
# avoidable source of run-to-run variation.
PREHEAT_TOLERANCE_C = 5.0
PREHEAT_TIMEOUT_S = 900.0

# Opening the door does not cool the probe for about a minute.
#
# Measured with an operator who opened the door within two seconds of the
# prompt: the reading kept RISING for 10 s on element inertia, then fell at
# -0.4 C/s -- indistinguishable from a shut door -- for a further 50 s,
# and only then dropped at -5.2 C/s. The thermocouple follows the cavity
# walls, not the air, so the door's effect is delayed rather than weak.
#
# This was first read as operator reaction time, which was wrong and would
# have put the prompt 60 s too late.
DOOR_LAG_S = 60.0

# Below this the cooldown is finished and the oven is safe to open or reload.
COOLDOWN_TARGET_C = 60.0

# A warm start is normal for a tool in use: back-to-back boards, or a run
# begun shortly after the last. The profile simply holds heat off until its
# own curve catches up with wherever the oven already is.


class Event(object):
    """Something the UI, the log or the speaker should react to."""
    RUN_STARTED = "run_started"
    STAGE_CHANGED = "stage_changed"
    PEAK_REACHED = "peak_reached"
    ABOVE_LIQUIDUS = "above_liquidus"
    BELOW_LIQUIDUS = "below_liquidus"
    OPEN_THE_DOOR = "open_the_door"
    RUN_FINISHED = "run_finished"
    FAULTED = "faulted"
    ABORTED = "aborted"


class App(object):
    def __init__(self, relay, sensor, clock, controller_factory,
                 supervisor=None, on_event=None, sample=None):
        self.relay = relay
        self.sensor = sensor
        self.clock = clock
        self.controller_factory = controller_factory
        self.supervisor = supervisor or Supervisor()
        self.on_event = on_event or (lambda name, payload: None)
        self.sample = sample or (lambda row: None)

        self.state = STATE_IDLE
        self.profile = None
        self.controller = None
        self.metrics = None
        self.reading = None
        self.temperature = None
        self.target = None
        self.duty = 0.0
        self.elapsed = 0.0
        self.stage = None
        self.fault = None

        self._next_control = None
        self._state_entered = None
        self._run_started = None
        self._above = False
        self._door_prompted = False

    # -- lifecycle ---------------------------------------------------------

    def request_start(self, profile):
        """Begin a run. Returns None, or a Fault explaining the refusal."""
        if self.state not in (STATE_IDLE, STATE_REPORT):
            return None
        reading = self._read()
        problem = self.supervisor.check_start(reading)
        if problem is not None:
            return problem
        self.profile = profile
        self.controller = self.controller_factory(profile)
        self.metrics = metrics.RunMetrics(profile.liquidus_c or 0.0)
        self._above = False
        self._door_prompted = False
        self._enter(STATE_PREHEAT)
        return None

    def abort(self):
        if self.state in (STATE_PREHEAT, STATE_RUNNING):
            self.relay.set(False)
            self._emit(Event.ABORTED, {})
            self._enter(STATE_COOLDOWN)

    def acknowledge_fault(self):
        if self.state == STATE_FAULT:
            self.supervisor.acknowledge()
            self.fault = None
            self._enter(STATE_IDLE)

    # -- the loop ----------------------------------------------------------

    def tick(self):
        """Call as often as you like. The control step self-schedules."""
        now = self.clock.monotonic()
        if self._next_control is None:
            self._next_control = now
        if now < self._next_control:
            return False
        # Schedule from the deadline, not from now, so a slow render does not
        # let the cadence drift permanently late.
        self._next_control += CONTROL_INTERVAL_S
        if self._next_control < now - CONTROL_INTERVAL_S:
            self._next_control = now + CONTROL_INTERVAL_S
        self._control_step(now)
        return True

    def _control_step(self, now):
        relay_was_on = self.relay.is_on()
        self.reading = self._read()
        self.temperature = self.reading.hot if self.reading else None

        fault = self.supervisor.update(now, self.reading, relay_was_on)
        if fault is not None:
            self.relay.set(False)
            self.fault = fault
            self._emit(Event.FAULTED, {"fault": fault})
            self._enter(STATE_FAULT)
            return

        handler = getattr(self, "_in_" + self.state)
        handler(now)

        self.sample({"t": now, "state": self.state, "temp": self.temperature,
                     "target": self.target, "duty": self.duty,
                     "relay": self.relay.is_on(),
                     "cold": self.reading.cold if self.reading else None})

    # -- states ------------------------------------------------------------

    def _in_idle(self, now):
        self.relay.set(False)
        self.duty = 0.0
        self.target = None

    def _in_fault(self, now):
        self.relay.set(False)
        self.duty = 0.0

    def _in_report(self, now):
        self.relay.set(False)
        self.duty = 0.0

    def _in_preheat(self, now):
        """Hold at the profile's starting temperature, then start the clock."""
        start_c = self.profile.target_at(0.0)
        self.target = start_c
        temp = self.temperature
        if temp is None:
            self.relay.set(False)
            return
        if temp >= start_c - PREHEAT_TOLERANCE_C:
            self._begin_running(now)
            return
        if now - self._state_entered > PREHEAT_TIMEOUT_S:
            self.relay.set(False)
            self._emit(Event.ABORTED, {"reason": "preheat timed out"})
            self._enter(STATE_COOLDOWN)
            return
        # Gentle approach: never more than half power getting to the start.
        self.duty = 0.5 if temp < start_c - PREHEAT_TOLERANCE_C else 0.0
        self._drive(now, self.duty)

    @property
    def door_prompted(self):
        """Whether the operator has been asked to open the door.

        Exposed so the running screen can show it. An event on the serial
        console is invisible to someone standing at the oven, which is the
        only person who can act on it.
        """
        return self._door_prompted

    def _prompt_door_at_liquidus(self, temp):
        """Ask for the door as the oven crosses liquidus on the way up.

        That sounds far too early, and it is not, because the door takes
        about a minute to show up on the thermocouple. Measured with the
        door opened within two seconds of the prompt: the reading rose for
        another 10 s, fell at -0.4 C/s for 50 s more -- exactly as if the
        door were shut -- and only then dropped at -5.2 C/s. The probe
        follows the cavity walls rather than the air.

        So the prompt has to lead the effect by DOOR_LAG_S. Prompting at
        the peak, which is what this did first, put the drop 60 s late: the
        NC191 datasheet run held 95 s above liquidus against a 60-90 s
        window. Crossing liquidus on the way up is roughly one lag earlier,
        which lands it inside.

        Only for profiles that declare cooling_assumes_open_door. The rest
        are not asking for anything the closed oven cannot do.
        """
        if self._door_prompted or self.profile is None or temp is None:
            return
        if not getattr(self.profile, "cooling_assumes_open_door", False):
            return
        liquidus = self.profile.liquidus_c
        if liquidus is None or temp < liquidus:
            return
        self._door_prompted = True
        self._emit(Event.OPEN_THE_DOOR,
                   {"temp": temp,
                    "reason": "open now -- the door takes about a minute to "
                              "reach the probe"})

    def _begin_running(self, now):
        # Enter the profile where the oven already is, not always at zero.
        #
        # A warm oven started at t=0 opens with the target below it, so the
        # controller withholds heat while the profile burns through a ramp
        # already achieved. Not a bug fix: two back-to-back SAC305 runs from
        # ~50 C both met their J-STD windows without this. It shortens a
        # warm run and gives the controller a meaningful target from the
        # first second. Not yet validated on hardware.
        entry = 0.0
        if self.profile is not None and self.temperature is not None:
            entry = self.profile.entry_time_for(self.temperature)

        self._run_started = now - entry
        self.elapsed = entry
        self.supervisor.begin_run(
            now, expected_duration_s=(self.profile.duration - entry)
            if self.profile is not None else None)
        self.controller.reset(now)
        self._enter(STATE_RUNNING)
        payload = {"profile": self.profile.name}
        if entry > 0.0:
            # Worth saying out loud: it changes what the run means, and a
            # large skip is a sign the oven was not given time to cool.
            payload["entered_at_s"] = round(entry, 1)
            payload["oven_c"] = round(self.temperature, 1)
        self._emit(Event.RUN_STARTED, payload)

    def _in_running(self, now):
        self.elapsed = now - self._run_started
        temp = self.temperature
        self.target = self.profile.target_at(self.elapsed)
        self.metrics.add(self.elapsed, temp)
        self._track_stage()
        self._track_liquidus(temp)
        self._prompt_door_at_liquidus(temp)

        if self.elapsed >= self.profile.duration:
            self.relay.set(False)
            self._emit(Event.RUN_FINISHED, {})
            self._enter(STATE_COOLDOWN)
            return

        self.duty = self.controller.duty_for(self.elapsed, temp, now)
        self._drive(now, self.duty)

    def _in_cooldown(self, now):
        self.relay.set(False)
        self.duty = 0.0
        self.target = None
        temp = self.temperature
        if temp is None:
            return
        if self.metrics is not None:
            self.metrics.add(now - (self._run_started or now), temp)
        self._track_liquidus(temp)
        if not self._door_prompted and self.profile is not None:
            liq = self.profile.liquidus_c
            if liq is None or temp < liq:
                self._door_prompted = True
                self._emit(Event.OPEN_THE_DOOR, {"temp": temp})
        if temp <= COOLDOWN_TARGET_C:
            self.supervisor.end_run()
            self._enter(STATE_REPORT)

    # -- helpers -----------------------------------------------------------

    def _drive(self, now, duty):
        if not self.supervisor.allow_heat():
            self.relay.set(False)
            return
        if self.controller is not None:
            # Every heating state modulates through the same time-proportional
            # output. Preheat used to be a special case that bang-banged on
            # `duty > 0.5` -- while the only duty preheat ever asks for is
            # exactly 0.5, so the relay could never close. On hardware the
            # oven sat at 26.5 C with a 45 C target, reporting duty=0.500 each
            # step and cooling, and would have done so until the 900 s
            # timeout. Telemetry looked correct throughout, which is why this
            # went unnoticed through eleven runs: only profiles starting above
            # ambient enter preheat at all, and none of them had.
            self.relay.set(self.controller.relay_state(now, duty))
        else:
            self.relay.set(duty >= 0.5)

    def _read(self):
        try:
            return self.sensor.read()
        except Exception:
            return None

    def _track_stage(self):
        stages = self.profile.stages
        current = None
        for name, t0, t1 in stages:
            if t0 <= self.elapsed < t1:
                current = name
                break
        if current != self.stage:
            self.stage = current
            self._emit(Event.STAGE_CHANGED, {"stage": current})

    def _track_liquidus(self, temp):
        liq = self.profile.liquidus_c if self.profile else None
        if liq is None or temp is None:
            return
        above = temp >= liq
        if above and not self._above:
            self._above = True
            self._emit(Event.ABOVE_LIQUIDUS, {"temp": temp})
        elif not above and self._above:
            self._above = False
            self._emit(Event.BELOW_LIQUIDUS, {"temp": temp})

    def _enter(self, state):
        self.state = state
        self._state_entered = self.clock.monotonic()
        # Cooldown is entered from three places -- a finished profile, an
        # abort, and a preheat that timed out -- so the handover to the
        # cooldown clock is done here rather than at each of them.
        if state == STATE_COOLDOWN:
            self.supervisor.begin_cooldown(self._state_entered)

    def _emit(self, name, payload):
        try:
            self.on_event(name, payload)
        except Exception as e:
            # A broken UI must never stop the control loop -- but it should
            # not be able to hide either.
            print("# WARNING event handler failed for %s: %r" % (name, e))
