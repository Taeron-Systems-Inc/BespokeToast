

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
