# SPDX-License-Identifier: MIT
"""The receiver's parsing and its refusal to lie about storing a run."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools",
                                "collector"))
import serve  # noqa: E402


def test_it_summarises_the_header_the_oven_writes():
    log = ("# bespoketoast run log\n"
           "# firmware,v2.0-dev\n"
           "# profile,SAC305 (this oven)\n"
           "# started_at,2026-09-03T01-19-09Z\n"
           "t,target_c,actual_c,relay,cold_c,cpu_c\n"
           "0.0,25.00,24.4,0,25.0,34.0\n"
           "# summary,peak=236.4 tal=96\n"
           "# rows,800\n")
    line = serve.summarise(log)
    assert "SAC305 (this oven)" in line
    assert "2026-09-03T01-19-09Z" in line
    assert "peak=236.4 tal=96" in line
    assert "800 rows" in line


def test_a_log_with_no_header_still_summarises():
    assert serve.summarise("t,a\n1,2\n") == "(no header)"


def test_filenames_from_the_network_are_not_trusted():
    for hostile in ("../../etc/passwd", "/etc/shadow", "a b;rm -rf /",
                    "..\\..\\win.ini"):
        safe = serve.SAFE.sub("_", os.path.basename(hostile))[:80]
        assert "/" not in safe and "\\" not in safe
        assert ".." not in safe or safe.strip("._") != ""
        assert ";" not in safe


def test_there_is_an_upload_size_limit():
    assert 0 < serve.MAX_BYTES <= 16 * 1024 * 1024
