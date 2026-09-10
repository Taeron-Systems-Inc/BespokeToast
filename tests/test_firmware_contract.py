"""display.py and code.py are never imported by this suite -- they need a
board -- so nothing else here would notice a name disappearing from them.

That is not hypothetical. Moving one function out of display.py cut a span
that also contained _font() and preload(), deleting both. Every test passed,
the deploy reported success, and the firmware died on boot with
"ImportError: cannot import name preload". These checks parse the modules
instead of importing them, so board-only code still gets verified.
"""

import ast
import os

FIRMWARE = os.path.join(os.path.dirname(__file__), "..", "firmware")


def _tree(rel):
    return ast.parse(open(os.path.join(FIRMWARE, rel)).read())


def _defined(tree):
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
    return names


def _imported_from(tree, module):
    wanted = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            wanted.update(a.name for a in node.names)
    return wanted


def _calls_named(node, name):
    return any(isinstance(n, ast.Call) and getattr(n.func, "id", None) == name
               for n in ast.walk(node))


def test_code_py_only_imports_names_that_exist():
    code = _tree("code.py")
    for module, rel in (("oven.ui.display", "oven/ui/display.py"),
                        ("oven.ui.layout", "oven/ui/layout.py"),
                        ("oven.hardware", "oven/hardware.py"),
                        ("oven.app", "oven/app.py"),
                        ("oven.controller", "oven/controller.py"),
                        ("oven.profile", "oven/profile.py"),
                        ("oven.metrics", "oven/metrics.py")):
        wanted = _imported_from(code, module)
        if not wanted:
            continue
        have = _defined(_tree(rel))
        missing = wanted - have
        assert not missing, "code.py imports %s from %s, which does not define it" % (
            sorted(missing), rel)


def test_display_imports_names_that_exist():
    disp = _tree("oven/ui/display.py")
    wanted = _imported_from(disp, ".layout")
    have = _defined(_tree("oven/ui/layout.py"))
    missing = wanted - have
    assert not missing, "display.py imports %s from layout.py" % sorted(missing)


def test_display_still_defines_what_it_is_expected_to():
    """A blunt guard on the module that no test can import."""
    have = _defined(_tree("oven/ui/display.py"))
    for name in ("Display", "preload", "_font"):
        assert name in have, "display.py no longer defines %s" % name


def test_every_firmware_module_parses():
    for base, dirs, names in os.walk(FIRMWARE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in names:
            if n.endswith(".py"):
                ast.parse(open(os.path.join(base, n)).read())


def test_code_py_reserves_the_chart_buffer_at_startup():
    """The chart buffer is ~5.9 KB and used to be allocated on the first
    running screen -- after a run had already started, on whatever heap
    remained. A freshly booted device managed it; one that had been working a
    while failed with MemoryError and ran with no chart."""
    src = open(os.path.join(FIRMWARE, "code.py")).read()
    assert "reserve_chart" in src, "code.py must claim the chart buffer at boot"
    main = src[src.index("def main("):]
    reserve = main.index("reserve_chart")
    loop = main.index("while True:")
    assert reserve < loop, "the reservation must happen before the main loop"


def test_the_renderer_does_not_release_the_chart_buffer():
    """Releasing it when a chart-less screen appears means re-allocating on
    the next run, on a heap that has meanwhile fragmented -- which is the
    failure that releasing it was meant to avoid."""
    src = open(os.path.join(FIRMWARE, "oven/ui/display.py")).read()
    rebuild = src[src.index("def _rebuild"):src.index("def _update")]
    assert "self._chart = None" not in rebuild, \
        "_rebuild must not drop the chart buffer"


def _code_py_tree():
    import ast
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "firmware", "code.py")
    return ast.parse(open(path).read())


def _guarded_calls(tree):
    """Names of functions called inside a try that handles MemoryError."""
    import ast
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        handles_memory = any(
            (isinstance(h.type, ast.Name) and h.type.id == "MemoryError")
            or (isinstance(h.type, ast.Tuple)
                and any(getattr(e, "id", "") == "MemoryError"
                        for e in h.type.elts))
            for h in node.handlers)
        if not handles_memory:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                f = inner.func
                out.add(getattr(f, "id", None) or getattr(f, "attr", None))
    return out


def test_the_display_path_cannot_kill_a_run():
    """A run died at 90 C, relay at full duty, on a 256-byte allocation.

    It was history.append in the main loop, and the MemoryError propagated
    out of main(). The relay was driven low on the way out so it failed
    safe, but the oven stopped controlling and stopped answering ABORT.
    Everything that only feeds the screen must be survivable.
    """
    guarded = _guarded_calls(_code_py_tree())
    for name in ("running", "fault", "render", "add", "_emit"):
        assert name in guarded, (
            "%s() is not inside a try that handles MemoryError; a failure "
            "there would stop the firmware mid-run" % name)


def test_the_control_step_is_not_swallowed():
    """app.tick() must NOT be wrapped: a fault there has to surface."""
    guarded = _guarded_calls(_code_py_tree())
    assert "tick" not in guarded, (
        "the control step is inside a MemoryError handler; safety logic "
        "must not be silently skipped")


def test_both_ways_of_starting_a_run_record_it():
    """The touchscreen path is the one most likely to be unattended.

    Logging was once wired into the console START and not into the touch
    handler, so a run begun by pressing START on the oven -- the case the
    log exists for -- would not have been recorded. Two call sites was the
    fix then.

    It is one call site now, and deliberately: the log opens on the
    run_started event, which the state machine emits however the run was
    begun. That also fixed a second bug, because request_start enters
    PREHEAT and the warm-start offset is not known until the transition
    into RUNNING -- opening at the old sites recorded the offset as zero.

    So the invariant is no longer "two calls". It is that the one call
    hangs off the event, and that no start path opens the log itself.
    """
    import ast
    tree = _code_py_tree()
    starts = [n for n in ast.walk(tree)
              if isinstance(n, ast.Call)
              and getattr(n.func, "attr", None) == "request_start"]
    assert len(starts) >= 2, (
        "expected a console and a touchscreen start path, found %d"
        % len(starts))

    opens = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", None)
             == "begin_log"]
    assert len(opens) == 1, (
        "begin_log is called %d times; it belongs on the run_started event "
        "so that every way of starting a run reaches it once" % len(opens))

    announce = [n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "announce"]
    assert announce, "code.py no longer has an event handler called announce"
    assert _calls_named(announce[0], "begin_log"), (
        "begin_log is not reached from the event handler, so a run started "
        "by touch may go unrecorded")

def test_boot_puts_the_relay_down_before_anything_that_can_raise():
    """boot.py has one job that outranks the other.

    It also decides filesystem ownership now, which touches storage and
    supervisor and can raise. None of that may come before the relay is
    driven low -- an exception above that line would leave the pulldown as
    the only thing holding the oven off.
    """
    import ast
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "firmware", "boot.py")
    tree = ast.parse(open(path).read())

    relay_line = None
    remount_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "deinit":
            relay_line = node.lineno if relay_line is None else relay_line
        if isinstance(node, ast.Call) and \
                getattr(node.func, "attr", None) == "remount":
            remount_line = node.lineno
    assert relay_line is not None, "boot.py never releases the relay pin"
    assert remount_line is not None, "boot.py never sets filesystem ownership"
    assert relay_line < remount_line, (
        "the filesystem work at line %d comes before the relay is safe at "
        "line %d" % (remount_line, relay_line))


def test_boot_takes_ownership_from_the_recorded_mode_not_from_usb():
    """boot.py must not ask usb_connected -- it lies there.

    CircuitPython starts USB after boot.py finishes, so the flag reads
    False with a cable attached. Sampling it, and then polling it for five
    seconds, both handed the filesystem to the oven while it was plugged in
    and locked the host out of its own volume.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "firmware", "boot.py")
    import ast
    source = open(path).read()
    tree = ast.parse(source)
    # The docstring explains why usb_connected is unusable here, so match
    # on attribute access rather than on the text.
    reads = [n for n in ast.walk(tree)
             if isinstance(n, ast.Attribute) and n.attr == "usb_connected"]
    assert not reads, (
        "boot.py reads usb_connected at line %s, which is False there even "
        "when a host is attached" % (reads[0].lineno if reads else "?"))
    calls = [getattr(n.func, "id", None) for n in ast.walk(tree)
             if isinstance(n, ast.Call)]
    assert "decode" in calls, "boot.py must use the recorded boot mode"


def test_the_default_boot_mode_keeps_the_volume_with_the_host():
    """Being wrong this way costs one unrecorded run. The other way costs
    a board nobody can program."""
    from oven.bootmode import HOST, decode, owns_filesystem
    assert decode(None) == HOST
    assert decode(bytearray((0xFF, 0xFF))) == HOST
    assert owns_filesystem(decode(None)) is False


def test_code_py_never_imports_a_module_inside_a_function():
    """A local import makes that name local to the ENTIRE function.

    code.py had "import gc" inside the MEM command handler, which made gc
    local to main(). Every other gc reference in main() -- the MemoryError
    guards, and select() -- then raised NameError instead of collecting,
    and the firmware died the first time a profile was selected.
    """
    import ast
    tree = _code_py_tree()
    module_level = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_level.add((alias.asname or alias.name).split(".")[0])

    offenders = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(func):
            if not isinstance(node, ast.Import):
                continue
            for alias in node.names:
                bound = (alias.asname or alias.name).split(".")[0]
                if bound in module_level:
                    offenders.append(
                        "%s() re-imports %s at line %d, which is already "
                        "imported at module scope"
                        % (func.name, bound, node.lineno))
    assert not offenders, (
        "a local import shadows the module-level one for the WHOLE "
        "function, including nested functions: %s" % offenders)


def test_the_parsed_characterisation_is_released_after_use():
    """Holding the JSON keeps the very lists the packing replaced.

    FeedForward copies the curves into array('f'); if code.py also keeps the
    parsed dict, both live for the whole run and the saving is negative.
    Measured: free fell from 30352 to 27056 until the dict was dropped.
    """
    import ast
    tree = _code_py_tree()
    released = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        targets = [getattr(t, "id", None) for t in node.targets]
        if "data" in targets and isinstance(node.value, ast.Constant) \
                and node.value.value is None:
            released = True
    assert released, (
        "code.py never releases the parsed characterisation; the packed "
        "rate tables then cost memory instead of saving it")


def test_a_run_does_not_bring_the_radio_down():
    """Closing the radio for a run costs 24.2 s of frozen loop to undo.

    Measured on the board: after a run returned the oven to idle, the main
    loop stopped for 24.22 s inside web.start() -- scan plus associate --
    with no telemetry, no touch and no render. That is the lag between
    pressing DONE and the home screen appearing, and it happened after
    every run.

    What actually has to be true during a run is that nobody polls the
    socket, which is what test_the_web_service_only_polls_while_idle
    checks. Staying associated costs 1472 bytes and no loop time at all,
    because the driver touches SPI only when it is called.

    An earlier version of this test asserted the opposite -- that
    "web.stop()" appears in code.py -- and so enforced the defect.
    """
    import ast
    tree = _code_py_tree()

    def stops_the_web(node):
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "stop"
                    and getattr(inner.func.value, "id", None) == "web"):
                return True
        return False

    def mentions_a_running_state(node):
        wanted = ("STATE_RUNNING", "STATE_PREHEAT", "STATE_IDLE",
                  "STATE_COOLDOWN")
        return any(isinstance(inner, ast.Name) and inner.id in wanted
                   for inner in ast.walk(node.test))

    offenders = [n.lineno for n in ast.walk(tree)
                 if isinstance(n, ast.If) and mentions_a_running_state(n)
                 and stops_the_web(n)]
    assert not offenders, (
        "code.py closes the radio on a state change (line %s). Bringing it "
        "back up blocks the main loop for ~24 s, which is what the DONE "
        "button lag was." % offenders)


def test_the_frame_is_drawn_before_the_radio_is_touched():
    """The screen is what says the oven is alive; it goes first.

    web.start() blocks for tens of seconds. Ahead of the render in the
    loop, that meant a cold boot showed nothing until the network was up.
    """
    import ast
    tree = _code_py_tree()
    main = [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "main"]
    assert main, "code.py has no main()"

    def line_of(pred):
        found = [n.lineno for n in ast.walk(main[0]) if pred(n)]
        return max(found) if found else None

    render = line_of(lambda n: isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)
                     and n.func.attr == "render")
    start = line_of(lambda n: isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "advance"
                    and getattr(n.func.value, "id", None) == "web")
    assert render is not None, "the loop never renders"
    assert start is not None, "the loop never starts the web service"
    assert start > render, (
        "web.advance() (line %d) runs before display.render() (line %d) in "
        "the loop, so a cold boot shows nothing until the radio is up "
        "instead of showing what it is doing" % (start, render))


def test_the_web_service_only_polls_while_idle():
    """Polling a socket costs up to 227 ms; the control loop has 250.

    Matched on the AST structurally. An earlier version of this test
    searched for the text "web.poll" inside ast.dump output, which never
    contains it -- attributes are rendered as nodes, not source. It passed
    nothing and proved nothing.
    """
    import ast
    source = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                               "code.py")).read()
    tree = ast.parse(source)

    # Both the names that reach the co-processor. advance() is the one the
    # loop calls; it polls the socket once the server is up and steps the
    # radio's bring-up before that, and either way it is SPI.
    TOUCHES_THE_RADIO = ("poll", "advance")

    def calls_poll(node):
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr in TOUCHES_THE_RADIO
                    and getattr(inner.func.value, "id", None) == "web"):
                return True
        return False

    def tests_idle(node):
        for inner in ast.walk(node.test):
            if isinstance(inner, ast.Name) and inner.id == "STATE_IDLE":
                return True
        return False

    assert calls_poll(tree), "nothing in code.py ever drives the web service"

    # Every one of them, not just one of them. A second unguarded call site
    # is exactly how this would come back.
    def guarded(call_node):
        for n in ast.walk(tree):
            if isinstance(n, ast.If) and tests_idle(n):
                for inner in ast.walk(n):
                    if inner is call_node:
                        return True
        return False

    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute)
             and n.func.attr in TOUCHES_THE_RADIO
             and getattr(n.func.value, "id", None) == "web"]
    unguarded = [n.lineno for n in calls if not guarded(n)]
    assert not unguarded, (
        "code.py touches the radio at line %s without testing the run "
        "state; SPI during a run puts network latency inside the loop that "
        "decides when the heater switches off" % unguarded)


def test_the_idle_screen_is_given_the_address_it_displays():
    """layout.home takes the address as a keyword with a default, so
    forgetting to pass it renders "no network" on a perfectly connected
    oven and nothing anywhere fails. That exact shape of silent breakage
    has happened once already, with open_the_door on the run screen.
    """
    code = _code_py_tree()
    calls = [n for n in ast.walk(code)
             if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "home"]
    assert calls, "code.py no longer renders the idle screen"
    for call in calls:
        names = [k.arg for k in call.keywords]
        assert "address" in names, (
            "L.home is called without address=, so the oven will show "
            "'no network' whatever its real state")
        value = [k.value for k in call.keywords if k.arg == "address"][0]
        assert isinstance(value, ast.Attribute) and value.attr == "address", (
            "address= must come from the web service, not a constant")


def test_boot_does_not_restart_the_program():
    """The oven booted twice on every power cycle.

    Setting the RTC used to call supervisor.reload(), to give back the
    7280 bytes the WiFi imports left in sys.modules. That reason has
    expired twice: the radio now stays associated for the whole session, so
    the modules are resident whatever happens, and the frozen build leaves
    60368 free with the server up. What the restart still cost was a second
    cold boot with the self-test panel frozen on screen for the first one --
    which is what "it boots up twice and looks hung" was.
    """
    import ast
    tree = _code_py_tree()
    reloads = [n.lineno for n in ast.walk(tree)
               if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute)
               and n.func.attr == "reload"
               and getattr(n.func.value, "id", None) == "supervisor"]
    assert not reloads, (
        "code.py restarts itself at line %s; boot pays for the whole "
        "startup twice" % reloads)


def test_the_radio_comes_up_once_at_boot_not_twice():
    """The clock and the page each used to bring the radio up from scratch
    -- two scans, two joins, a restart between them, and about fifty seconds
    of it. The clock is now fetched on the connection the page is already
    making."""
    import ast
    tree = _code_py_tree()
    constructions = [n.lineno for n in ast.walk(tree)
                     if isinstance(n, ast.Call)
                     and getattr(n.func, "id", None) == "Radio"]
    assert len(constructions) <= 1, (
        "Radio() is constructed at %s. Each one is a co-processor reset, a "
        "scan and a join." % constructions)


def test_setting_the_clock_is_wired_to_the_bring_up():
    """Otherwise the RTC is never set and every log is stamped from boot --
    which fails silently, and only shows up when somebody reads a log."""
    import ast
    tree = _code_py_tree()
    wired = [n for n in ast.walk(tree)
             if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Attribute) and t.attr == "on_epoch"
                     for t in n.targets)]
    assert wired, "nothing assigns web.on_epoch, so the clock is never set"
    assert any(getattr(n.value, "id", None) == "set_rtc" for n in wired), (
        "web.on_epoch is assigned something other than set_rtc")


def test_a_cable_left_in_does_not_cost_the_oven_its_logging():
    """remember_boot_mode used to write HOST whenever it saw a cable.

    An oven with a programming cable left in could then never record a run:
    every boot rewrote the mode to HOST, so every following boot came up
    with the volume owned by the host and logging off, showing as a red FAIL
    on the power-on screen of a perfectly healthy oven. Taking the volume is
    now something a person asks for once, with deploy.py, and it sticks.
    """
    import ast
    tree = _code_py_tree()
    fn = [n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "remember_boot_mode"]
    assert fn, "remember_boot_mode is gone"
    names = {n.id for n in ast.walk(fn[0]) if isinstance(n, ast.Name)}
    assert "STANDALONE" in names, "it no longer records standalone at all"
    assert "HOST" not in names, (
        "remember_boot_mode references HOST again; the only automatic "
        "direction is towards the oven owning its own filesystem")
