# SPDX-License-Identifier: MIT
"""What the oven will serve, and what it must refuse.

The oven is the only machine present in normal operation, so this page is
how a run log gets off it. It is also reachable by anything on the shop
network, which is why what it cannot do matters as much as what it can.
"""

import pytest

from oven.webapp import (MAX_PROFILE_BYTES, index_page, route, safe_log_name)


def test_the_index_lists_runs_with_download_links():
    page = index_page("idle, 24 C", [("0001-a.csv", 26601)], [("SAC305", True)])
    assert "0001-a.csv" in page
    assert "/logs/0001-a.csv" in page
    assert "26601" in page
    assert "SAC305" in page


def test_an_oven_with_no_runs_says_so_rather_than_showing_nothing():
    page = index_page("idle", [], [("SAC305", True)])
    assert "no runs recorded yet" in page


def test_the_page_says_it_cannot_start_a_run():
    """Stated on the page because someone will look for the button."""
    page = index_page("idle", [], [])
    assert "cannot start" in page.lower()


def test_a_hostile_profile_name_cannot_inject_markup():
    page = index_page("idle", [], [("<script>alert(1)</script>", False)])
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_a_hostile_run_name_cannot_inject_markup():
    page = index_page("idle", [("<img src=x onerror=y>", 1)], [])
    assert "<img" not in page
    assert "&lt;img" in page


@pytest.mark.parametrize("path,kind", [
    ("/", "index"),
    ("/index.html", "index"),
    ("/logs", "index"),
    ("/status", "status"),
    ("/logs/0001-a.csv", "log"),
    ("/nope", "not-found"),
])
def test_routing(path, kind):
    assert route("GET", path)[0] == kind


@pytest.mark.parametrize("name", [
    "../wifi.json", "..%2fwifi.json", "a/b", "/etc/passwd", "",
])
def test_a_path_that_climbs_out_is_refused(name):
    kind, _ = route("GET", "/logs/" + name)
    assert kind in ("bad-name", "not-found"), (
        "%r routed to something servable" % name)


def test_only_names_the_store_actually_lists_are_served():
    """Refusing by allowlist rather than by sanitising a string."""
    known = ["0001-a.csv", "0002-b.csv.sent"]
    assert safe_log_name("0001-a.csv", known) == "0001-a.csv"
    assert safe_log_name("wifi.json", known) is None
    assert safe_log_name("0003-c.csv", known) is None


def test_the_credentials_file_cannot_be_served():
    """wifi.json holds the network passwords and sits on the same volume.

    Routing and serving are separate steps and the test has to cover both:
    /logs/wifi.json is a syntactically fine log name, and what stops it is
    that the store does not list it.
    """
    known = ["0001-a.csv", "0002-b.csv"]
    for path in ("/wifi.json", "/settings.toml", "/../wifi.json",
                 "/logs/../wifi.json"):
        kind, _ = route("GET", path)
        assert kind in ("not-found", "bad-name"), "%s was routable" % path
    kind, name = route("GET", "/logs/wifi.json")
    assert kind == "log"
    assert safe_log_name(name, known) is None, (
        "wifi.json would have been served")


@pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH", "TRACE"])
def test_methods_that_could_change_things_are_refused(method):
    assert route(method, "/")[0] == "bad-method"


def test_there_is_no_route_that_starts_a_run():
    """Remote start was excluded when the network features were agreed.

    Checked by exhausting the routes rather than by reading the code: a
    route added later that begins a run has to fail this.
    """
    kinds = set()
    for method in ("GET", "POST", "HEAD"):
        for path in ("/", "/start", "/run", "/logs", "/profiles", "/status",
                     "/abort", "/logs/x.csv"):
            kinds.add(route(method, path)[0])
    for kind in kinds:
        assert kind not in ("start", "run", "abort"), (
            "a route resolves to %r" % kind)


def test_an_uploaded_profile_has_a_size_limit():
    assert 0 < MAX_PROFILE_BYTES <= 64 * 1024
