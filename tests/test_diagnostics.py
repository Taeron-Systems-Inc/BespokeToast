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
}

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
                speaks = any(
                    isinstance(x, ast.Expr) and isinstance(x.value, ast.Call)
                    and getattr(x.value.func, "id", "") == "print"
                    for x in body)
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
