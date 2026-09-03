# SPDX-License-Identifier: MIT
"""What gets uploaded, and what happens when the answer is not 200.

The failure that matters is marking a log as sent when it was not: the
oven's copy is then the only one, and the next run's eviction may delete
it. So anything short of a 2xx must leave it pending.
"""

import pytest

from oven.uploader import (MAX_ATTEMPTS, SENT_SUFFIX, pending, request,
                           sent_name, status_of, succeeded)


def test_pending_lists_unsent_logs_oldest_first():
    names = ["0003-c.csv", "0001-a.csv", "0002-b.csv"]
    assert pending(names) == ["0001-a.csv", "0002-b.csv", "0003-c.csv"]


def test_a_sent_log_is_not_offered_again():
    names = ["0001-a.csv", "0002-b.csv" + SENT_SUFFIX]
    assert pending(names) == ["0001-a.csv"]


def test_non_logs_are_ignored():
    assert pending(["boot_out.txt", "code.py", "0001-a.csv"]) == ["0001-a.csv"]


def test_marking_is_a_rename_not_an_index():
    """An index is a second thing to keep consistent with the directory,
    and the thing that is wrong after a power cut mid-write."""
    assert sent_name("0001-a.csv") == "0001-a.csv" + SENT_SUFFIX
    assert pending([sent_name("0001-a.csv")]) == []


def test_the_request_is_a_complete_http_post():
    body = b"t,temp\n0,25\n"
    raw = request("10.20.10.162", "/runs", "0001-a.csv", body, port=8788)
    text = raw.decode("utf-8")
    assert text.startswith("POST /runs HTTP/1.0\r\n")
    assert "Host: 10.20.10.162:8788\r\n" in text
    assert "Content-Length: %d\r\n" % len(body) in text
    assert "X-Run-Log: 0001-a.csv\r\n" in text
    assert raw.endswith(body)
    assert b"\r\n\r\n" in raw


def test_the_default_port_is_not_written_into_the_host_header():
    raw = request("example", "/runs", "a.csv", b"x")
    assert b"Host: example\r\n" in raw


def test_a_string_body_is_encoded():
    raw = request("h", "/p", "a.csv", "temp\n25\n")
    assert b"Content-Length: 8\r\n" in raw


@pytest.mark.parametrize("reply,code", [
    (b"HTTP/1.0 200 OK\r\n\r\n", 200),
    (b"HTTP/1.1 201 Created\r\n\r\n", 201),
    (b"HTTP/1.1 500 Internal Server Error\r\n\r\n", 500),
    (b"HTTP/1.1 404 Not Found\r\n\r\n", 404),
])
def test_the_status_line_is_read(reply, code):
    assert status_of(reply) == code


@pytest.mark.parametrize("reply", [
    None, b"", b"garbage", b"200 OK\r\n", b"HTTP/1.1\r\n",
    b"HTTP/1.1 not-a-number\r\n",
])
def test_an_unparseable_reply_is_not_a_success(reply):
    assert status_of(reply) is None
    assert succeeded(reply) is False


@pytest.mark.parametrize("code,ok", [
    (200, True), (204, True), (299, True),
    (300, False), (404, False), (500, False), (503, False),
])
def test_only_2xx_counts_as_delivered(code, ok):
    reply = b"HTTP/1.1 %d X\r\n\r\n" % code
    assert succeeded(reply) is ok


def test_there_is_a_retry_limit():
    """Unbounded retries against a receiver that is down would keep the
    radio up, which is the one thing this must not do during a run."""
    assert 1 <= MAX_ATTEMPTS <= 5


def test_a_real_run_log_is_far_larger_than_one_socket_buffer():
    """The reason post() sends in pieces.

    The co-processor's buffer is 4000 bytes. A ten-minute run is about
    26 kB, and handing send() the whole thing does not raise -- it never
    returns. Recorded here so the chunking is not later 'simplified' away.
    """
    ten_minute_run = 26601
    esp32_socket_buffer = 4000
    assert ten_minute_run > esp32_socket_buffer * 6
