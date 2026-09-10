import pytest



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


def test_a_rate_is_not_reported_from_a_fraction_of_a_second():
    """Run 0004 reported "max ramp up FAILED 3.20 C/s" against a 2.5 limit.

    That rate is 73% above anything this oven has ever produced -- the step
    tests peak at 1.85 C/s near 80 C -- it does not appear in the run's own
    log, and simulating the same profile end to end gives 1.84. Every other
    run that day reported 1.87 to 2.03.

    What could produce it is the rate window having no lower bound: the scan
    takes the oldest sample within 5 s, and for the first seconds of a run
    that is a fraction of a second, where a degree of thermocouple noise is
    several degrees per second. The 4 Hz samples that produced 3.20 were
    never captured, so this is the mechanism and not a proof about that run.
    Either way a rate measured over a third of a second is not a ramp rate.
    """
    from oven.metrics import RunMetrics

    noisy = RunMetrics(217.0)
    for i in range(8):                       # two seconds at 4 Hz
        noisy.add(i * 0.25, 100.0 + (1.0 if i % 2 else 0.0))
    assert noisy.max_ramp_up == 0.0
    assert noisy.max_ramp_down == 0.0


def test_a_real_ramp_is_still_measured():
    """The floor must not cost the metric its job."""
    from oven.metrics import RunMetrics

    m = RunMetrics(217.0)
    for i in range(200):                     # 50 s at 4 Hz, a clean 1.2 C/s
        m.add(i * 0.25, 25.0 + 1.2 * i * 0.25)
    assert 1.15 < m.max_ramp_up < 1.25


def test_the_floor_changes_nothing_on_a_run_logged_at_1_hz():
    """Every shipped log samples at 1 s or slower, so the window is already
    past the floor by the second sample and the guard is invisible there."""
    from oven.metrics import RunMetrics

    with_floor = RunMetrics(137.0)
    without = RunMetrics(137.0, min_window_s=0.0)
    for i in range(120):
        t, c = i * 1.0, 25.0 + 1.1 * i
        with_floor.add(t, c)
        without.add(t, c)
    assert with_floor.max_ramp_up == pytest.approx(without.max_ramp_up)
