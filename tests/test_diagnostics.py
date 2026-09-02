"""Failures must be visible.

Three separate bugs in this project were caught late, or not at all, because
an exception handler swallowed something: the chart vanishing on MemoryError,
a font silently falling back to terminalio, and a run's telemetry capture
dying unnoticed. Catching is usually right. Being quiet about it is not.

Any handler that neither logs, re-raises, nor returns a signalling value has
to be listed here with a reason.
"""

import ast
import os

JUSTIFIED_SILENT = {
    # Sets FAULT_BUS on the reading, so the supervisor refuses heat and says
    # why. The effect is the opposite of silent.
    "oven/hardware.py": "sets a fault flag the supervisor acts on",
    # display.root_group replaced display.show() in CircuitPython 9. This is
    # a version branch, not an error path.
    "oven/ui/display.py": "CircuitPython 8/9 compatibility branch",
    # Per-candidate `continue` while searching two paths; exhausting both
    # does log.
    "oven/ui/layout.py": "one of several candidate paths; total failure logs",
    # The SNTP poll keeps the last error and reports once after the retries
    # are exhausted. Warning on every poll would say the same thing twenty
    # times while the co-processor is simply not ready yet.
    "oven/radio.py": "retry loop reports once after exhausting attempts",
}

# Reporting a failure through an injected callback counts as speaking. It is
# what print does, and a test can assert on it -- which is why logstore takes
# its reporter as an argument instead of printing. The names are deliberately
# few: this recognises deliberate reporting, not any method that happens to
# be called in a handler.
REPORTERS = ("_warn", "_fail", "warn", "log", "note_memory_failure")

FIRMWARE = os.path.join(os.path.dirname(__file__), "..", "firmware")


def _silent_handlers():
    out = []
    for base, dirs, names in os.walk(FIRMWARE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in sorted(names):
            if not n.endswith(".py"):
                continue
            path = os.path.join(base, n)
            rel = os.path.relpath(path, FIRMWARE).replace(os.sep, "/")
            for node in ast.walk(ast.parse(open(path).read())):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                body = node.body
                # Walk the whole handler, not just its top level: a
                # report that only fires on the last retry sits inside an
                # if, and reporting conditionally is still reporting.
                speaks = any(
                    isinstance(x, ast.Call)
                    and (getattr(x.func, "id", "") == "print"
                         or getattr(x.func, "attr", "") in REPORTERS
                         or getattr(x.func, "id", "") in REPORTERS)
                    for stmt in body for x in ast.walk(stmt))
                signals = any(isinstance(x, (ast.Raise, ast.Return))
                              for x in body)
                if not (speaks or signals):
                    out.append((rel, node.lineno))
    return out


def test_no_new_silent_exception_handlers():
    unexplained = [(f, n) for f, n in _silent_handlers()
                   if f not in JUSTIFIED_SILENT]
    assert not unexplained, (
        "these handlers swallow an exception without logging, raising or "
        "returning a signal: %s. Either say something, or add the file to "
        "JUSTIFIED_SILENT with a reason." % unexplained)


def test_the_justified_list_has_not_gone_stale():
    """If a file stops having a silent handler, drop it from the list rather
    than leaving a licence lying around."""
    files = {f for f, _ in _silent_handlers()}
    stale = set(JUSTIFIED_SILENT) - files
    assert not stale, "no longer has silent handlers, remove: %s" % stale


def test_losing_the_measured_model_is_loud():
    """Running on a guessed oven model instead of the measured one is the
    most consequential silent degradation available, so it must announce
    itself."""
    src = open(os.path.join(FIRMWARE, "code.py")).read()
    idx = src.index("def load_characterisation")
    body = src[idx:src.index("def load_profiles")]
    assert "WARNING" in body and "ESTIMATED" in body


def test_the_detector_still_catches_a_bare_pass():
    """The rule above must not have been widened into a loophole."""
    import ast as _ast
    tree = _ast.parse("try:\n    x()\nexcept Exception:\n    pass\n")
    handler = [n for n in _ast.walk(tree)
               if isinstance(n, _ast.ExceptHandler)][0]
    body = handler.body
    speaks = any(isinstance(x, _ast.Expr) and isinstance(x.value, _ast.Call)
                 and (getattr(x.value.func, "id", "") == "print"
                      or getattr(x.value.func, "attr", "") in REPORTERS)
                 for x in body)
    signals = any(isinstance(x, (_ast.Raise, _ast.Return)) for x in body)
    assert not (speaks or signals)


def test_an_unrelated_method_call_does_not_count_as_speaking():
    import ast as _ast
    tree = _ast.parse("try:\n    x()\nexcept Exception:\n    self.reset()\n")
    handler = [n for n in _ast.walk(tree)
               if isinstance(n, _ast.ExceptHandler)][0]
    speaks = any(isinstance(x, _ast.Expr) and isinstance(x.value, _ast.Call)
                 and (getattr(x.value.func, "id", "") == "print"
                      or getattr(x.value.func, "attr", "") in REPORTERS)
                 for x in handler.body)
    assert not speaks


def test_the_detector_sees_a_report_nested_in_a_branch():
    """A warning that only fires on the last retry still counts.

    radio.connect() retries three times and reports once, on the final
    failure, so its report lives inside an if. Only inspecting the
    handler's top-level statements missed it.
    """
    import ast as _ast
    src = ("try:\n    x()\n"
           "except Exception as e:\n"
           "    if last:\n        self._warn('gave up: %r' % e)\n"
           "    sleep(1)\n")
    handler = [n for n in _ast.walk(_ast.parse(src))
               if isinstance(n, _ast.ExceptHandler)][0]
    speaks = any(
        isinstance(x, _ast.Call)
        and (getattr(x.func, "id", "") == "print"
             or getattr(x.func, "attr", "") in REPORTERS
             or getattr(x.func, "id", "") in REPORTERS)
        for stmt in handler.body for x in _ast.walk(stmt))
    assert speaks


def test_the_detector_still_rejects_a_silent_branch():
    """Widening the search must not let a genuinely silent handler pass."""
    import ast as _ast
    src = ("try:\n    x()\n"
           "except Exception:\n    if last:\n        cleanup()\n")
    handler = [n for n in _ast.walk(_ast.parse(src))
               if isinstance(n, _ast.ExceptHandler)][0]
    speaks = any(
        isinstance(x, _ast.Call)
        and (getattr(x.func, "id", "") == "print"
             or getattr(x.func, "attr", "") in REPORTERS
             or getattr(x.func, "id", "") in REPORTERS)
        for stmt in handler.body for x in _ast.walk(stmt))
    signals = any(isinstance(x, (_ast.Raise, _ast.Return))
                  for stmt in handler.body for x in _ast.walk(stmt))
    assert not (speaks or signals)
