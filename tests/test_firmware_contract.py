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
