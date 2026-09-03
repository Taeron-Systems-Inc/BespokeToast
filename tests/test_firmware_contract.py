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

    Logging was wired into the console START and not into the touch
    handler, so a run begun by pressing START on the oven -- the case the
    log exists for -- would not have been recorded.
    """
    import ast
    tree = _code_py_tree()
    starts = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "attr", None) != "request_start":
            continue
        starts.append(node)
    assert len(starts) >= 2, (
        "expected a console and a touchscreen start path, found %d"
        % len(starts))

    calls = [getattr(c.func, "id", None) for c in ast.walk(tree)
             if isinstance(c, ast.Call)]
    assert calls.count("begin_log") >= 2, (
        "begin_log is called %d time(s); every way of starting a run must "
        "record it" % calls.count("begin_log"))


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


def test_the_web_service_is_torn_down_when_a_run_starts():
    """Polling a socket costs up to 227 ms; the control loop has 250.

    The teardown must be driven by the state leaving idle, not by anything
    the web code decides for itself.
    """
    import ast
    source = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                               "code.py")).read()
    assert "web.stop()" in source, "nothing ever stops the web service"
    tree = ast.parse(source)
    stops = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        body = ast.dump(node)
        if "web" in body and "stop" in body and "STATE_IDLE" in body:
            stops.append(node.lineno)
    assert stops, "the teardown is not guarded by the run state"


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

    def calls_poll(node):
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "poll"
                    and getattr(inner.func.value, "id", None) == "web"):
                return True
        return False

    def tests_idle(node):
        for inner in ast.walk(node.test):
            if isinstance(inner, ast.Name) and inner.id == "STATE_IDLE":
                return True
        return False

    assert calls_poll(tree), "web.poll() is never called"
    guards = [n for n in ast.walk(tree)
              if isinstance(n, ast.If) and calls_poll(n) and tests_idle(n)]
    assert guards, (
        "web.poll() is not inside any if that tests the run state; polling "
        "during a run would put network latency in the control loop")
