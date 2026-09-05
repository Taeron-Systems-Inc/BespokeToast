# SPDX-License-Identifier: MIT
"""Write a profile so it is readable AND fits through the oven's upload.

json.dumps(indent=2) puts every number of every point on its own line,
which turned a 60-point curve into 2 kB of whitespace. The fields stay
one per line; the points collapse to one point per line.
"""

import json
import sys


def dumps(profile):
    points = profile.get("points")
    body = dict(profile)
    body.pop("points", None)
    out = ["{"]
    for key in sorted(body):
        out.append("  %s: %s," % (json.dumps(key), json.dumps(body[key])))
    if points is not None:
        out.append('  "points": [')
        rows = ["    %s" % json.dumps(p) for p in points]
        out.append(",\n".join(rows))
        out.append("  ]")
    else:
        out[-1] = out[-1].rstrip(",")
    out.append("}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path) as f:
            data = json.load(f)
        with open(path, "w") as f:
            f.write(dumps(data))
        print("%s" % path)
