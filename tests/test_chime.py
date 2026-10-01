"""The end-of-run sounds: short, distinct, and unable to hurt the oven."""

import os

import pytest

from oven import chime, hal
from oven.chime import Chime, DONE, FAULT, REST


class Clock(object):
    def __init__(self):
        self.t = 100.0

    def monotonic(self):
        return self.t


class Relay(hal.Interlocked):
    """The real interlock over a fake pin, so ``pin`` is what the relay
    coil would see."""

    def __init__(self):
        hal.Interlocked.__init__(self)
        self.pin = False

    def _drive(self, on):
        self.pin = on


class Voice(object):
    """Records each call, and the relay as it was at that instant."""

    def __init__(self, relay=None):
        self.calls = []
        self.relay = relay
        self.relay_at_call = []

    def _note(self, what):
        self.calls.append(what)
        if self.relay is not None:
            self.relay_at_call.append((self.relay.pin, self.relay.held))

    def tone(self, hz):
        self._note(hz)

    def quiet(self):
        self._note(None)


class BrokenVoice(object):
    def tone(self, hz):
        raise OSError("DAC gone")

    def quiet(self):
        raise OSError("DAC gone")


def play_through(melody, step=0.01):
    clock, voice = Clock(), Voice()
    c = Chime(voice, clock, Relay())
    c.play(melody)
    while c.playing:
        clock.t += step
        c.tick()
    return voice.calls


def test_both_sounds_are_under_two_seconds():
    assert chime.length(DONE) < 2.0
    assert chime.length(FAULT) < 2.0


def test_success_and_fault_are_told_apart():
    """Done rises, a fault falls -- and they share no pitch."""
    done = [hz for hz, _ in DONE if hz]
    fault = [hz for hz, _ in FAULT if hz]
    assert done == sorted(done)
    assert fault[0] > fault[1]
    assert not set(done) & set(fault)


def test_every_note_sounds_in_order_and_it_ends_quiet():
    calls = play_through(DONE)
    assert calls == [hz for hz, _ in DONE] + [None]


def test_rests_are_silence():
    calls = play_through(FAULT)
    expected = [hz if hz != REST else None for hz, _ in FAULT] + [None]
    assert calls == expected


def test_a_slow_loop_pass_does_not_push_back_the_whole_tune():
    """Notes are timed from the start: one late pass skips ahead, it does
    not stretch everything after it."""
    clock, voice = Clock(), Voice()
    c = Chime(voice, clock, Relay())
    c.play(DONE)
    clock.t += 0.30          # a slow render, landing in the third note
    c.tick()
    assert voice.calls == [DONE[0][0], DONE[2][0]]
    clock.t += chime.length(DONE)
    c.tick()
    assert not c.playing


def test_a_new_sound_replaces_the_one_playing():
    clock, voice = Clock(), Voice()
    c = Chime(voice, clock, Relay())
    c.play(DONE)
    clock.t += 0.05
    c.play(FAULT)
    assert voice.calls[-1] == FAULT[0][0]


def test_tick_does_nothing_between_note_changes():
    clock, voice = Clock(), Voice()
    c = Chime(voice, clock, Relay())
    c.play(DONE)
    for _ in range(5):
        clock.t += 0.01
        c.tick()
    assert voice.calls == [DONE[0][0]]


def test_no_speaker_is_silent_not_an_error():
    c = Chime(None, Clock(), Relay())
    c.play(DONE)
    c.tick()
    assert not c.playing


def test_a_failing_speaker_cannot_stop_the_loop(capsys):
    clock = Clock()
    relay = Relay()
    c = Chime(BrokenVoice(), clock, relay)
    c.play(FAULT)
    for _ in range(200):
        clock.t += 0.01
        c.tick()
    c.play(DONE)
    assert not c.playing
    # Said once, not on every pass.
    assert capsys.readouterr().out.count("speaker failed") == 1
    # Nothing will drive the speaker again, so heat is allowed back.
    assert not relay.held


def test_the_firmware_plays_them_on_the_events_that_matter():
    """code.py is board-only, so this checks the wiring by reading it."""
    src = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                            "code.py")).read()
    announce = src[src.index("def announce("):]
    announce = announce[:announce.index("\n    def ") if "\n    def "
                        in announce else 2000]
    assert '"run_finished"' in announce and "chime_mod.DONE" in announce
    assert '"faulted"' in announce and "chime_mod.FAULT" in announce
    loop = src[src.index("    while True:"):]
    assert "chime.tick()" in loop[:200]


# -- no heat while the speaker is in use -----------------------------------
#
# There is no watchdog. A speaker call that hung while the relay was closed
# would leave the oven heating with nothing able to stop it. So the relay is
# driven open before every speaker call, and held open from the first note
# of a sound until the speaker is quiet again.

def rig(relay_on=False):
    clock, relay = Clock(), Relay()
    voice = Voice(relay)
    relay.set(relay_on)
    return Chime(voice, clock, relay), clock, voice, relay


def run_to_the_end(c, clock, step=0.01):
    while c.playing:
        clock.t += step
        c.tick()


@pytest.mark.parametrize("melody", [DONE, FAULT], ids=["done", "fault"])
def test_every_speaker_call_is_made_with_the_relay_held_open(melody):
    c, clock, voice, relay = rig()
    c.play(melody)
    run_to_the_end(c, clock)
    assert len(voice.relay_at_call) == len(melody) + 1
    assert all(pin is False and held for pin, held in voice.relay_at_call)


def test_heat_is_off_before_the_first_note_even_if_it_was_on():
    c, clock, voice, relay = rig(relay_on=True)
    assert relay.pin
    c.play(FAULT)
    assert voice.relay_at_call[0] == (False, True)
    assert not relay.is_on()


def test_heat_cannot_come_on_while_a_sound_plays():
    c, clock, voice, relay = rig()
    c.play(DONE)
    while c.playing:
        relay.set(True)          # whatever the controller asks for
        assert relay.pin is False
        clock.t += 0.01
        c.tick()


def test_heat_is_allowed_again_once_the_sound_is_over():
    c, clock, voice, relay = rig()
    c.play(DONE)
    run_to_the_end(c, clock)
    assert not relay.held
    relay.set(True)
    assert relay.pin is True


def test_stopping_a_sound_quiets_the_speaker_before_heat_is_allowed():
    """The order a run start depends on: quiet, then release."""
    c, clock, voice, relay = rig()
    c.play(FAULT)
    clock.t += 0.1
    c.tick()
    c.stop()
    assert voice.calls[-1] is None
    assert voice.relay_at_call[-1] == (False, True)
    assert not relay.held


def test_a_new_sound_over_an_old_one_keeps_the_hold_throughout():
    c, clock, voice, relay = rig()
    c.play(DONE)
    clock.t += 0.2
    c.play(FAULT)
    assert relay.held
    run_to_the_end(c, clock)
    assert not relay.held


class StuckRelay(Relay):
    """Closed, and every write to the pin from now on fails."""

    def __init__(self):
        Relay.__init__(self)
        self.set(True)
        self.writes = []

    def _drive(self, on):
        if hasattr(self, "writes"):
            self.writes.append(on)
            raise OSError("pin write failed")
        self.pin = on


def test_a_relay_that_cannot_be_driven_open_means_no_sound_and_no_heat(capsys):
    clock, relay = Clock(), StuckRelay()
    voice = Voice(relay)
    c = Chime(voice, clock, relay)
    c.play(FAULT)
    assert voice.calls == []
    assert not c.playing
    assert "could not hold the relay open" in capsys.readouterr().out
    # It does not pretend the write worked.
    assert relay.is_on()
    # The hold stands: every later request for heat is turned into a
    # request to open.
    assert relay.held
    with pytest.raises(OSError):
        relay.set(True)
    assert True not in relay.writes


def test_no_speaker_takes_no_hold():
    clock, relay = Clock(), Relay()
    c = Chime(None, clock, relay)
    c.play(DONE)
    assert not relay.held


# -- the interlock itself ----------------------------------------------------

def test_a_hold_opens_the_relay_at_once():
    r = Relay()
    r.set(True)
    r.hold_off("a")
    assert r.pin is False and not r.is_on()


def test_every_holder_must_release_before_heat():
    r = Relay()
    r.hold_off("a")
    r.hold_off("b")
    r.release("a")
    r.set(True)
    assert r.pin is False
    r.release("b")
    r.set(True)
    assert r.pin is True


def test_holding_twice_and_releasing_once_releases():
    r = Relay()
    r.hold_off("a")
    r.hold_off("a")
    r.release("a")
    assert not r.held


def test_releasing_what_was_never_held_is_harmless():
    r = Relay()
    r.release("nobody")
    r.set(True)
    assert r.pin is True


def test_every_sound_event_is_announced_with_the_relay_already_open():
    """What makes playing on these events safe: App opens the relay before
    it announces them. Checked with the relay closed just beforehand."""
    from oven import hal
    from oven.app import App, Event, CONTROL_INTERVAL_S
    from oven.safety import Supervisor, Limits

    class FakeRelay(object):
        def __init__(self):
            self._on = False

        def set(self, on):
            self._on = bool(on)

        def is_on(self):
            return self._on

    class Sensor(object):
        temp = 25.0
        faults = hal.FAULT_NONE

        def read(self):
            return hal.Reading(self.temp, cold=30.0, faults=self.faults)

    class Profile(object):
        name = "test"
        liquidus_c = None
        duration = 20.0
        stages = ()
        points = ()
        start_c = 25.0

        def target_at(self, t):
            return self.start_c + 5.0 * t

        def entry_time_for(self, temp):
            return 0.0

    class Ctl(object):
        def reset(self, now):
            pass

        def duty_for(self, elapsed, temp, now, element_z=None):
            return 1.0

        def relay_state(self, now, duty):
            return True

    SOUNDED = (Event.FAULTED, Event.RUN_FINISHED, Event.ABORTED)

    def rig():
        clock, relay, sensor = Clock(), FakeRelay(), Sensor()
        seen = []

        def on_event(name, payload):
            if name in SOUNDED:
                seen.append((name, relay.is_on()))

        # Heating flat out on a sensor that does not move is a frozen probe
        # after 5 s. These runs are about the events, not that guard.
        app = App(relay, sensor, clock, lambda p: Ctl(),
                  supervisor=Supervisor(Limits(max_rate_c_per_s=1e6,
                                               sensor_frozen_s=1e6,
                                               stall_window_s=1e6)),
                  on_event=on_event)
        return app, clock, relay, sensor, seen

    def run(app, clock, seconds, sensor=None, warming_c_per_s=0.0):
        for _ in range(int(seconds / CONTROL_INTERVAL_S)):
            clock.t += CONTROL_INTERVAL_S
            if sensor is not None:
                sensor.temp += warming_c_per_s * CONTROL_INTERVAL_S
            app.tick()

    # A run to the end, heating flat out.
    app, clock, relay, sensor, seen = rig()
    app.request_start(Profile())
    run(app, clock, 1.0)
    assert relay.is_on()
    run(app, clock, 25.0)
    assert (Event.RUN_FINISHED, False) in seen

    # A fault while heating.
    app, clock, relay, sensor, seen = rig()
    app.request_start(Profile())
    run(app, clock, 2.0)
    assert relay.is_on()
    sensor.faults = hal.FAULT_BUS
    run(app, clock, 2.0)
    assert (Event.FAULTED, False) in seen

    # A preheat that gives up: warming, but too slowly to arrive in time.
    app, clock, relay, sensor, seen = rig()
    p = Profile()
    p.start_c = 150.0
    app.request_start(p)
    closed = False
    for _ in range(1000):
        run(app, clock, 1.0, sensor, warming_c_per_s=0.1)
        closed = closed or relay.is_on()
    assert closed
    assert (Event.ABORTED, False) in seen

    assert all(not on for _, on in seen)


def test_the_firmware_gives_the_chime_the_real_relay():
    src = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                            "code.py")).read()
    assert "chime_mod.Chime(hw.speaker, hw.clock, hw.relay)" in src
    # Silenced before every start, so the hold does not delay the run.
    starts = [i for i in range(len(src)) if src.startswith(
        "app.request_start(profile) if profile else None", i)]
    assert starts
    for at in starts:
        assert "chime.stop()" in src[at - 200:at]


def test_the_relay_is_the_interlocked_one_and_the_speaker_loads_held():
    src = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                            "oven", "hardware.py"), encoding="utf-8").read()
    assert "class Relay(hal.Interlocked):" in src
    relay = src[src.index("class Relay("):src.index("class Thermocouple")]
    # Only the pin write is its own; set() must be the interlocked one.
    assert "def set(" not in relay
    hw = src[src.index("class Hardware("):]
    held = hw.index('self.relay.hold_off("speaker setup")')
    made = hw.index("self.speaker = Speaker()")
    freed = hw.index('self.relay.release("speaker setup")')
    assert hw.index("self.relay = Relay()") < held < made < freed
