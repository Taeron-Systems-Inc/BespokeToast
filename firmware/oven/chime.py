# SPDX-License-Identifier: MIT
"""Short sounds for the end of a run: one for done, one for a fault.

The screen is the only visual indicator on this oven -- the NeoPixel is
inside the enclosure -- and nobody watches a screen for the six minutes a
profile takes. A sound is what brings them back.

Two constraints decide the shape of this.

**Nothing here may block.** A tune played with sleeps between notes would
hold the main loop for its whole length, and the control step has a 250 ms
deadline. So a melody is a list of (frequency, seconds) and ``tick`` is
called every pass of the loop; it changes the note when the clock says so,
and returns at once otherwise. Notes are timed from the start of the melody,
not from the last change, so a slow pass delays one note boundary without
pushing every later one back.

**Nothing may be rendered in advance.** A sampled melody would be one buffer
of several kilobytes, and the largest free block on this heap has been
measured at a few. The voice behind this plays one looped waveform cycle at
whatever pitch it is told, which costs tens of bytes.

**The oven does not heat while a sound plays.** There is no watchdog on
this board. A speaker call that hung with the relay closed would stall the
loop that is the only thing able to open it, and the oven would heat without
bound. So a melody holds the relay open (hal.Interlocked) from the moment it
starts until the speaker is quiet again, and before every call to the
speaker the hold is taken again and the relay checked open. If the hold
cannot be taken, the speaker is not touched. If a call hangs, it hangs with
the oven cold.

Pure stdlib, like the rest of oven/. The voice is anything with ``tone(hz)``
and ``quiet()``; hardware.Speaker is the real one. The relay is anything
with ``hold_off``, ``release`` and ``is_on``; hardware.Relay is the real
one.
"""

# Pitches (Hz). Kept at 500 Hz and up: the PyPortal's speaker is a small
# one, and below that it is barely audible through an enclosure.
C6 = 1047
E6 = 1319
G6 = 1568
C7 = 2093
A5 = 880
DS5 = 622

REST = 0

# Done: a rising major arpeggio, about 0.7 s. Bright, brief, unmistakably
# "finished", and over before it can be irritating.
DONE = ((C6, 0.12), (E6, 0.12), (G6, 0.12), (C7, 0.32))

# Fault: a falling tritone, twice, about 1.3 s. Low and dissonant enough to
# read as "something is wrong" from across the room, without being an
# alarm that has to be silenced -- the fault screen does the explaining.
FAULT = ((A5, 0.22), (REST, 0.05), (DS5, 0.33), (REST, 0.15),
         (A5, 0.22), (REST, 0.05), (DS5, 0.33))


def length(melody):
    """Seconds the melody lasts."""
    return sum(d for _, d in melody)


class Chime(object):
    """Plays one melody at a time, a note per ``tick``.

    A failing speaker must never be able to stop the oven, so every call to
    the voice is guarded, and the first failure silences the chime for the
    rest of the boot rather than failing again four times a second.

    While a melody plays the relay is held open, so a run that starts in
    the middle of one gets no heat until it ends -- never more than two
    seconds. code.py stops the sound before it starts a run, so in practice
    a run does not wait at all.
    """

    def __init__(self, voice, clock, relay):
        self.voice = voice
        self.clock = clock
        self.relay = relay
        self._melody = None
        self._started = 0.0
        self._index = -1

    @property
    def playing(self):
        return self._melody is not None

    def play(self, melody):
        """Start *melody*, replacing whatever was playing."""
        if self.voice is None or not self._hold():
            return
        self._melody = melody
        self._started = self.clock.monotonic()
        self._index = -1
        self.tick()

    def stop(self):
        self._melody = None
        self._index = -1
        self._call("quiet")
        # Only once the speaker is quiet. If quiet() hung, the hold would
        # stay, and so would the oven's cold.
        self._release()

    def tick(self):
        """Call every pass of the loop. Cheap when there is nothing to do."""
        melody = self._melody
        if melody is None:
            return
        elapsed = self.clock.monotonic() - self._started
        index = None
        end = 0.0
        for i in range(len(melody)):
            end += melody[i][1]
            if elapsed < end:
                index = i
                break
        if index is None:
            self.stop()
            return
        if index == self._index:
            return
        self._index = index
        hz = melody[index][0]
        if hz:
            self._call("tone", hz)
        else:
            self._call("quiet")

    def _hold(self):
        """Hold the relay open and confirm it is. False: do not sound."""
        try:
            self.relay.hold_off(self)
            if not self.relay.is_on():
                return True
            print("# WARNING relay still closed after a hold; not sounding")
        except Exception as e:
            print("# WARNING could not hold the relay open (%r); not "
                  "sounding" % e)
        # The hold, if it was recorded, is kept: a relay that could not be
        # confirmed open is better refusing heat than trusted.
        self._melody = None
        return False

    def _release(self):
        try:
            self.relay.release(self)
        except Exception as e:
            print("# WARNING could not release the relay hold (%r)" % e)

    def _call(self, name, *args):
        if self.voice is None:
            return
        # Before every call, not only at play(): it costs one pin write, and
        # it does not depend on nothing having changed since.
        if not self._hold():
            return
        try:
            getattr(self.voice, name)(*args)
        except Exception as e:
            print("# WARNING speaker failed (%r); sounds are off until "
                  "reboot" % e)
            self.voice = None
            self._melody = None
            # Nothing will call the speaker again, so nothing can hang.
            self._release()
