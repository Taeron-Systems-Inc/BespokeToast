"""The figures the documentation quotes, held against the data it cites.

docs/control-loop.md states a number for each of these runs. The runs are
in this repository and tools/score_runs.py recomputes them, so a figure
that drifts from its data fails here instead of quietly becoming a claim
nobody can check. If one of these moves, the document moves with it.

Tolerances are the last printed digit, not an opinion about what is close
enough.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import score_runs  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def capture(name):
    return os.path.join(ROOT, "data", "plant-id", name)


def runlog(name):
    return os.path.join(ROOT, "data", name)


# (capture, documented rms, documented worst lag)
HEATING = [
    ("run-0013-ts391snl-hot.csv", 13.06, -32.0),
    ("run-0014-ts391lt.csv", 2.46, -6.6),
    ("run-0016-ts391snl-hot-precharge.csv", 1.57, -5.1),
    ("run-0017-ts391lt-hot-precharge.csv", 2.24, -5.2),
    ("run-0018-ts391snl-warm-predictive.csv", 1.87, -5.2),
    ("run-0020-ts391lt-hot-predictive.csv", 0.77, -2.4),
    ("run-0021-ts391snl-cold-predictive.csv", 0.95, -2.5),
    ("run-0022-ts391snl-hot-predictive.csv", 1.12, -3.8),
]


def test_the_heating_phase_figures_are_what_the_documentation_says():
    for name, rms, lag in HEATING:
        got_rms, got_lag, _charge, _entered = score_runs.heating(capture(name))
        assert abs(got_rms - rms) < 0.005, (name, got_rms, rms)
        assert abs(got_lag - lag) < 0.05, (name, got_lag, lag)


# (run log, rms, mean, minutes, closures/min, peak)
HOLDS = [
    ("bake-125c-run-0009-2026-09-09.csv", 0.264, +0.002, 240.0, 8.26, 127.2),
    ("bake-125c-run-0015-2026-09-10.csv", 0.552, -0.146, 3.2, 8.80, 125.4),
    ("bake-125c-run-0024-2026-09-16.csv", 0.240, +0.141, 240.0, 8.19, 125.9),
]


def test_the_bake_figures_are_what_the_documentation_says():
    for name, rms, mean, minutes, closures, peak in HOLDS:
        got = score_runs.hold(runlog(name))
        assert abs(got[0] - rms) < 0.0005, (name, got[0], rms)
        assert abs(got[1] - mean) < 0.0005, (name, got[1], mean)
        assert abs(got[2] - minutes) < 0.05, (name, got[2], minutes)
        assert abs(got[3] - closures) < 0.005, (name, got[3], closures)
        assert abs(got[4] - peak) < 0.05, (name, got[4], peak)


def test_the_bake_does_not_drift_across_its_four_hours():
    """The documented hourly rms, and the claim that rests on it."""
    hourly = score_runs.by_hour(
        runlog("bake-125c-run-0024-2026-09-16.csv"))
    assert [round(v, 3) for v in hourly] == [0.263, 0.237, 0.226, 0.233]
    assert max(hourly) - min(hourly) < 0.05, "that would be drift"


def test_every_run_the_documentation_cites_is_actually_here():
    """The point of the exercise: a fresh clone must not meet a citation
    it cannot follow. If a document names a run, its record is in the
    tree, and data/README.md says where."""
    import re
    cited = set()
    docs = [os.path.join(ROOT, "docs", f)
            for f in os.listdir(os.path.join(ROOT, "docs"))
            if f.endswith(".md")]
    for path in docs:
        for m in re.finditer(r"runs? (\d{4})", open(path).read()):
            cited.add(m.group(1))
    # 0012 and the no-heat fixtures are named only as things that exist,
    # not as evidence; nothing quotes a figure from them.
    cited -= {"0012", "0025", "0026"}
    present = set()
    for base in (os.path.join(ROOT, "data"),
                 os.path.join(ROOT, "data", "plant-id")):
        for name in os.listdir(base):
            m = re.search(r"run-?(\d{4})", name)
            if m:
                present.add(m.group(1))
    missing = sorted(cited - present)
    assert not missing, (
        "documentation cites runs with no record in the repository: %s"
        % ", ".join(missing))
