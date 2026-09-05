# SPDX-License-Identifier: MIT
"""What the oven will serve, and what it must refuse.

The oven is the only machine present in normal operation, so this page is
how a run log gets off it. It is also reachable by anything on the shop
network, which is why what it cannot do matters as much as what it can.
"""

import pytest

from oven.webapp import (MAX_PROFILE_BYTES, display_name, human_size,
                         index_page, route, safe_log_name,
                         split_started_at)


RUN = ("0003-SAC305-this-oven.csv.sent", 35730,
       "2026-09-03T01-19-09Z", "SAC305 (this oven)")


def test_a_run_is_listed_by_when_it_happened_and_what_it_ran():
    """The four things someone came to the page for. The filename is not
    one of them -- it is an implementation detail of the log store."""
    page = index_page([RUN], ["SAC305 (this oven)"])
    assert "2026-09-03" in page
    assert "01:19:09" in page
    assert "SAC305 (this oven)" in page
    assert "34.9 kB" in page
    assert "/logs/0003-SAC305-this-oven.csv'" in page


def test_the_uploader_suffix_never_reaches_the_reader():
    """.sent records that this oven handed the run to an archive. That is
    housekeeping, and means nothing to whoever is fetching it."""
    page = index_page([RUN], [])
    assert ">0003-SAC305-this-oven.csv.sent<" not in page
    assert display_name("0001-a.csv.sent") == "0001-a.csv"
    assert display_name("0001-a.csv") == "0001-a.csv"


def test_the_page_does_not_report_a_state_that_is_always_the_same():
    """The web service only ever serves while the oven is idle, so saying
    so told nobody anything; and the selected profile cannot be changed or
    started from here. Both were on the page and both were removed."""
    page = index_page([RUN], ["SAC305 (this oven)"])
    assert "idle" not in page.lower()
    assert "selected" not in page.lower()


def test_the_page_is_named_for_the_machine_it_is():
    page = index_page([], [])
    assert "<title>Taeron Reflow Oven</title>" in page
    assert "BespokeToast" not in page


def test_a_run_written_before_the_clock_was_set_is_still_listed():
    """Not a hypothetical. The clock comes off the network, so the first
    run after a power cut has "monotonic+40" where its date should be, and
    it must not vanish from the page for it."""
    page = index_page([("0007-NC191-datasheet.csv", 812,
                        "monotonic+40", "NC191LTA10 (datasheet)")], [])
    assert "/logs/0007-NC191-datasheet.csv" in page
    assert "run 0007" in page
    assert "NC191LTA10 (datasheet)" in page
    assert "812 B" in page
    assert "monotonic" not in page


def test_a_run_with_no_header_at_all_still_offers_its_file():
    page = index_page([("0009-mystery.csv", 30, None, None)], [])
    assert "/logs/0009-mystery.csv" in page
    assert "run 0009" in page


def test_an_unset_clock_is_said_plainly_because_it_makes_dates_lies():
    page = index_page([RUN], [], warning="This oven's clock is not set")
    assert "clock is not set" in page
    assert "clock is not set" not in index_page([RUN], [])


def test_timestamps_survive_being_filename_safe():
    """Stored with dashes where a time has colons, because it is also a
    filename on FAT."""
    assert split_started_at("2026-09-03T01-19-09Z") == ("2026-09-03", "01:19:09")
    assert split_started_at(None) == ("", "")
    assert split_started_at("nonsense") == ("", "")


def test_sizes_are_readable_at_a_glance():
    assert human_size(35730) == "34.9 kB"
    assert human_size(812) == "812 B"
    assert human_size(None) == ""


def test_an_oven_with_no_runs_says_so_rather_than_showing_nothing():
    assert "no runs recorded yet" in index_page([], ["SAC305"])


def test_the_page_says_it_cannot_start_a_run():
    """Stated on the page because someone will look for the button."""
    assert "cannot start" in index_page([], []).lower()


def test_a_hostile_profile_name_cannot_inject_markup():
    page = index_page([], ["<script>alert(1)</script>"])
    assert "<script>alert" not in page
    assert "&lt;script&gt;" in page


def test_a_hostile_run_name_cannot_inject_markup():
    page = index_page([("<img src=x onerror=y>", 1, None, None)], [])
    assert "<img" not in page
    assert "&lt;img" in page


def test_a_hostile_profile_name_inside_a_run_cannot_inject_markup():
    """The profile column comes out of the log file's own header, which is
    a file this page will happily read from a volume anyone can write."""
    page = index_page([("0001-a.csv", 1, "2026-01-01T00-00-00Z",
                        "<img src=x onerror=y>")], [])
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


STORED = ["0001-NC191-datasheet.csv.sent", "0002-DIAGNOSTIC-fast.csv"]


def test_a_request_under_the_offered_name_finds_the_stored_file():
    """The page offers 0001-NC191-datasheet.csv; flash holds
    0001-NC191-datasheet.csv.sent. The link has to resolve."""
    assert safe_log_name("0001-NC191-datasheet.csv",
                         STORED) == "0001-NC191-datasheet.csv.sent"
    assert safe_log_name("0002-DIAGNOSTIC-fast.csv",
                         STORED) == "0002-DIAGNOSTIC-fast.csv"


def test_the_stored_name_still_resolves_for_anything_holding_an_old_link():
    assert safe_log_name("0001-NC191-datasheet.csv.sent",
                         STORED) == "0001-NC191-datasheet.csv.sent"


def test_a_name_the_store_does_not_list_is_refused():
    for hostile in ("../wifi.json", "/etc/passwd", "0003-nope.csv",
                    "0001-NC191-datasheet", "", ".sent"):
        assert safe_log_name(hostile, STORED) is None


def test_no_link_on_the_page_carries_the_uploader_suffix():
    """The URL is the last place .sent could leak out, and it is what
    ends up in a browser's download name."""
    page = index_page([("0001-NC191-datasheet.csv.sent", 812,
                        "2026-09-02T19-03-12Z", "NC191LTA10")], [])
    assert "/logs/0001-NC191-datasheet.csv'" in page
    assert ".sent" not in page
