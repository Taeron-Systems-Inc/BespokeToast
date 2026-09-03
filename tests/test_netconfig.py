# SPDX-License-Identifier: MIT
"""Network choice and the rule that keeps the radio out of a run.

Measured on the device: the WiFi stack needs 22.6 kB and a running oven has
16.3 kB free, so bringing the radio up mid-run cannot work. That is a real
constraint rather than a preference, so it is tested like one.
"""

import io
import json

import pytest

from oven import netconfig
from oven.netconfig import Network, choose, load, may_connect


def opener_for(text):
    def _open(path):
        return io.StringIO(text)
    return _open


def missing_opener(path):
    raise OSError(2, "No such file")


def test_networks_are_read_from_the_config():
    text = json.dumps({"networks": [{"ssid": "Voxelis", "password": "a"},
                                    {"ssid": "Taeron", "password": "b"}]})
    nets = load(opener=opener_for(text))
    assert [n.ssid for n in nets] == ["Voxelis", "Taeron"]


def test_a_missing_config_is_reported_and_leaves_the_oven_offline():
    warnings = []
    nets = load(opener=missing_opener, on_warning=warnings.append)
    assert nets == []
    assert len(warnings) == 1
    assert "stay off the network" in warnings[0]


def test_malformed_json_does_not_raise():
    warnings = []
    nets = load(opener=opener_for("{not json"), on_warning=warnings.append)
    assert nets == []
    assert warnings


def test_an_entry_without_a_password_is_skipped_not_guessed():
    text = json.dumps({"networks": [{"ssid": "Open"},
                                    {"ssid": "Good", "password": "x"}]})
    warnings = []
    nets = load(opener=opener_for(text), on_warning=warnings.append)
    assert [n.ssid for n in nets] == ["Good"]
    assert warnings


def test_the_strongest_known_network_wins_not_the_first_listed():
    nets = [Network("Voxelis", "a"), Network("Taeron", "b")]
    scan = [("Voxelis", -70), ("Taeron", -40), ("Someone else", -20)]
    assert choose(nets, scan).ssid == "Taeron"


def test_an_unknown_network_is_never_chosen_however_strong():
    nets = [Network("Voxelis", "a")]
    scan = [("Voxelis", -80), ("NeighbourWiFi", -20)]
    assert choose(nets, scan).ssid == "Voxelis"


def test_nothing_in_range_gives_nothing():
    assert choose([Network("Voxelis", "a")], [("Elsewhere", -30)]) is None
    assert choose([], [("Voxelis", -30)]) is None


@pytest.mark.parametrize("state", ["idle", "report"])
def test_the_radio_may_come_up_when_the_oven_is_doing_nothing(state):
    assert may_connect(state, heating=False) is True


@pytest.mark.parametrize("state", ["running", "preheat", "cooldown", "fault"])
def test_the_radio_stays_down_during_a_run(state):
    """22.6 kB needed against 16.3 kB free. This is arithmetic, not taste."""
    assert may_connect(state, heating=False) is False


def test_an_energised_relay_refuses_regardless_of_state():
    """A state this module has not been taught about must still be safe."""
    assert may_connect("idle", heating=True) is False
    assert may_connect("some-future-state", heating=True) is False


def test_an_unknown_state_is_refused_rather_than_allowed():
    assert may_connect("some-future-state", heating=False) is False


def test_the_measured_budget_is_recorded_where_it_will_be_read():
    """The numbers behind the rule live next to the rule.

    They are the whole reason for it, and a future reader who does not have
    them will reasonably assume the restriction is arbitrary.
    """
    doc = netconfig.__doc__
    for figure in ("30352", "14080", "18192", "22592"):
        assert figure in doc, "the measured %s is not recorded" % figure


def test_an_archive_endpoint_is_read_when_present():
    from oven.netconfig import archive
    text = json.dumps({"networks": [{"ssid": "a", "password": "b"}],
                       "archive": {"host": "10.20.10.162", "port": 8788,
                                   "path": "/runs"}})
    assert archive(opener=opener_for(text)) == ("10.20.10.162", 8788, "/runs")


def test_no_archive_configured_is_not_an_error():
    """An oven with nowhere to send runs still records them all itself."""
    from oven.netconfig import archive
    text = json.dumps({"networks": [{"ssid": "a", "password": "b"}]})
    warnings = []
    assert archive(opener=opener_for(text), on_warning=warnings.append) is None
    assert warnings == []


def test_an_archive_without_a_host_is_reported():
    from oven.netconfig import archive
    text = json.dumps({"networks": [], "archive": {"port": 8788}})
    warnings = []
    assert archive(opener=opener_for(text), on_warning=warnings.append) is None
    assert warnings


def test_a_bad_archive_port_is_refused_not_guessed():
    from oven.netconfig import archive
    text = json.dumps({"networks": [], "archive": {"host": "h",
                                                   "port": "eight"}})
    warnings = []
    assert archive(opener=opener_for(text), on_warning=warnings.append) is None
    assert warnings


def test_the_archive_path_defaults():
    from oven.netconfig import archive
    text = json.dumps({"networks": [], "archive": {"host": "h"}})
    assert archive(opener=opener_for(text)) == ("h", 80, "/runs")
