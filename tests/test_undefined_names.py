# SPDX-License-Identifier: MIT
"""Names used but never bound.

Twice in one session: a helper added to deploy.py referred to `io` where
the module imports nothing of the kind, and the call that wired it into
main() passed a `port` variable that does not exist there. Neither is
reachable from the test suite -- both live on paths that need a board --
so both shipped, and the second one only surfaced when a deploy against
real hardware died on it.

pyflakes would catch this and is not installable here, so this is the
part of pyflakes that matters for this codebase. It is deliberately
conservative: it reports a name only when nothing in any enclosing scope,
the module, or the builtins could possibly bind it.
"""

import ast
import builtins
import os

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
TARGETS = [
    os.path.join("firmware", "code.py"),
    os.path.join("firmware", "boot.py"),
    os.path.join("tools", "deploy.py"),
    os.path.join("tools", "release.py"),
    os.path.join("tools", "render_screens.py"),
]
for _d in ("firmware/oven", "firmware/oven/ui", "tools/device", "tools/collector"):
    full = os.path.join(ROOT, _d)
    if os.path.isdir(full):
        TARGETS += [os.path.join(_d, n) for n in sorted(os.listdir(full))
                    if n.endswith(".py")]

BUILTINS = set(dir(builtins)) | {"__name__", "__file__", "__doc__"}


_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _bindings(body):
    """Names bound by these statements, without descending into nested
    scopes.

    Walking the whole tree instead was the first version, and it put every
    function's parameters into the module's scope -- which made the check
    miss `port`, one of the two bugs it was written for. A scope has to
    stop where the next one starts.
    """
    out = set()

    def record(node):
        if isinstance(node, ast.Name) and isinstance(
                node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
        elif isinstance(node, ast.Global):
            out.update(node.names)

    def visit(node):
        if isinstance(node, _SCOPES):
            name = getattr(node, "name", None)
            if name:
                out.add(name)               # the name binds; its body does not
            return
        record(node)
        for child in ast.iter_child_nodes(node):
            visit(child)

    for stmt in body:
        visit(stmt)
    return out


def _params(fn):
    a = fn.args
    got = set()
    for group in (a.args, a.posonlyargs, a.kwonlyargs):
        got.update(arg.arg for arg in group)
    for extra in (a.vararg, a.kwarg):
        if extra:
            got.add(extra.arg)
    return got


def _loaded(fn):
    """Names read inside this scope, not counting nested scopes' bodies."""
    out = []

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _SCOPES):
                continue
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                out.append((child.id, child.lineno))
            visit(child)

    visit(fn)
    return out


def _check(fn, enclosing, report):
    scope = set(enclosing) | _params(fn) | _bindings(fn.body)
    for name, line in _loaded(fn):
        if name not in scope and name not in BUILTINS:
            report.append((name, line))
    for node in ast.walk(fn):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node is not fn:
            _check(node, scope, report)


@pytest.mark.parametrize("rel", TARGETS)
def test_no_name_is_used_without_being_bound(rel):
    path = os.path.join(ROOT, rel)
    tree = ast.parse(open(path).read())
    module_scope = _bindings(tree.body)
    report = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _check(node, module_scope, report)
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    _check(sub, module_scope | _bindings(node.body), report)
    assert not report, "%s uses names nothing binds: %s" % (rel, report)
