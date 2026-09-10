

def test_a_profile_with_no_liquidus_is_not_judged_on_time_above_it():
    """The bake and the step test melt nothing and carry 0.0 as their
    liquidus, so every sample counted and the report showed a red FAILED
    for a check the run could neither pass nor fail. STEP 250 C reported
    "time above liquidus FAILED 1033 s" on an otherwise clean run."""
    from oven.metrics import RunMetrics, Limits as MLimits
    m = RunMetrics(0.0)
    for t in range(0, 200, 5):
        m.add(float(t), 100.0)
    names = [c[0] for c in m.check(MLimits())]
    assert "time above liquidus" not in names

    hot = RunMetrics(217.0)
    for t in range(0, 200, 5):
        hot.add(float(t), 230.0)
    assert "time above liquidus" in [c[0] for c in hot.check(MLimits())]


def test_a_profile_with_no_liquidus_accumulates_no_time_above_it():
    """The number itself, not just the check on it.

    Suppressing the check left the counter running: "temp_c >= 0" is true
    from the first sample, so run 0009 -- a 15201 s bake -- closed with
    "tal=15302", a time above liquidus longer than the run that produced
    it. The check was quiet and the log still carried the nonsense.
    """
    from oven.metrics import RunMetrics

    bake = RunMetrics(0)
    hot = RunMetrics(137.0)
    for i in range(200):
        t = i * 0.25
        bake.add(t, 125.0)
        hot.add(t, 125.0)
    assert bake.time_above_liquidus == 0.0
    assert hot.time_above_liquidus == 0.0

    for i in range(200, 400):
        t = i * 0.25
        hot.add(t, 150.0)
    assert hot.time_above_liquidus > 0.0
