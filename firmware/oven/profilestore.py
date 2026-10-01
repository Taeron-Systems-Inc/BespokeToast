# SPDX-License-Identifier: MIT
"""Changing what is in /profiles: versions, archiving, deleting.

Every argument that names something on the filesystem is matched against
the catalogue scan() produced, never used as a path. The set of legitimate
names is known, so there is nothing to sanitise and nothing to escape.

Deliberately nothing here selects a profile or starts one. Which profile
runs is still decided at the oven; this only changes what it is offered.

Pure stdlib: runs on CircuitPython and under CPython for tests. All of it
is lost on a deploy -- deploy.py mirrors /profiles from the repository and
removes what the repository does not have, versions and archive markers
included.
"""

import os

from oven.profile import ARCHIVED, latest, version_filename, versions_of


def _same_name(a, b):
    return str(a).strip().lower() == str(b).strip().lower()


def new_version_filename(refs, name, slug_filename):
    """(filename, version) an upload called *name* should be written to.

    A profile whose newest version carries the same name gets the next
    version. Otherwise the slug decides, as it always has -- two names
    that differ only in punctuation are the same profile -- and a slug
    nobody has used yet starts at version 1.

    The next number is one past the highest version still on the oven, so
    deleting the newest version and uploading again reuses its number.
    """
    stem = None
    for r in latest(refs):
        if _same_name(r.name, name):
            stem = r.stem
            break
    if stem is None:
        stem = slug_filename[:-5]
    have = versions_of(refs, stem)
    version = (have[-1].version + 1) if have else 1
    return (version_filename(stem, version), version)


def find_version(refs, filename):
    for r in refs:
        if r.filename == filename:
            return r
    return None


def has_profile(refs, stem):
    for r in refs:
        if r.stem == stem:
            return True
    return False


def set_archived(directory, refs, stem, archived):
    """Archive or unarchive one profile, all versions at once.

    Returns None, or why not. An archived profile is not offered at the
    oven and is otherwise untouched: its files, versions and downloads
    are exactly as they were.
    """
    if not has_profile(refs, stem):
        return "no such profile"
    if archived:
        f = open("%s/%s%s" % (directory, stem, ARCHIVED), "w")
        f.close()
    else:
        # Already unarchived is the outcome asked for, not an error.
        _drop_marker(directory, stem)
    return None


def delete_version(directory, refs, filename):
    """Remove one version. Returns None, or why not.

    Deleting the only version deletes the profile, archive marker and all,
    so no marker is left behind to archive a future upload of the same
    name without anyone having asked for that.
    """
    ref = find_version(refs, filename)
    if ref is None:
        return "no such version"
    os.remove(ref.path)
    if len(versions_of(refs, ref.stem)) == 1:
        _drop_marker(directory, ref.stem)
    return None


def delete_profile(directory, refs, stem):
    """Remove every version of one profile. Returns None, or why not."""
    have = versions_of(refs, stem)
    if not have:
        return "no such profile"
    for r in have:
        os.remove(r.path)
    _drop_marker(directory, stem)
    return None


def _drop_marker(directory, stem):
    if stem + ARCHIVED in os.listdir(directory):
        os.remove("%s/%s%s" % (directory, stem, ARCHIVED))


def bundle_chunks(refs, stem, chunk=512):
    """Every version of a profile as one JSON document, in pieces.

    ``{"profile": name, "versions": [{"version": n, "file": f,
    "profile": {...}}, ...]}``. Each version is copied in as the text on
    flash rather than re-serialised, so what is downloaded is what was
    stored. Yielded a piece at a time: a bundle is several times the size
    of the largest allocation this heap can be relied on for.
    """
    have = versions_of(refs, stem)
    head = '{"profile": %s, "versions": [' % _json_string(
        have[-1].name if have else stem)
    yield head
    for i, r in enumerate(have):
        yield ('%s{"version": %d, "file": %s, "profile": '
               % ("," if i else "", r.version, _json_string(r.filename)))
        f = open(r.path, "r")
        try:
            while True:
                piece = f.read(chunk)
                if not piece:
                    break
                yield piece
        finally:
            f.close()
        yield "}"
    yield "]}\n"


def _json_string(text):
    import json
    return json.dumps(str(text))
