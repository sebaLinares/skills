#!/usr/bin/env python3
"""Plan-coverage check — the one mechanical tooth of the lightweight harness.

Refuses a commit whose staged source files are not authorised by the
``covers:`` frontmatter of a plan in ``docs/exec-plans/active/``. This is the
in-repo enforcement of the hard constraint "no edits outside the active plan's
covers:" (see AGENTS.md § Hard constraints, docs/PLANS.md → covers:).

Stdlib only (Python >= 3.9), no third-party YAML. Wire it as the last step of
your pre-commit hook — see docs/processes/dev-setup.md § Plan-coverage check.
A Go/Node re-implementation is fine; the contract below is what matters.

Contract:
  - Reads staged, added/copied/modified files via ``git diff --cached``.
  - Files under ``docs/`` and the root anchors (AGENTS.md, CLAUDE.md,
    ARCHITECTURE.md, SECURITY.md, README.md) are always allowed.
  - Every other staged file must be prefix-matched by a ``covers:`` entry of
    some plan in ``docs/exec-plans/active/*.md``. Prefix match is literal; a
    trailing ``/`` covers a directory and everything under it.
  - On any uncovered file: print remediation to stderr, exit 1.
  - Bypass: ``HARNESS_BYPASS="<reason>" git commit ...`` (skips only this
    check; the reason is echoed).
"""
from __future__ import annotations

import os
import subprocess
import sys

ALWAYS_ALLOWED_ROOT = {
    "AGENTS.md",
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    "README.md",
    ".harness-version",
}
# Harness infrastructure paths — always allowed (not application source under a plan).
ALWAYS_ALLOWED_PREFIXES = ("docs/", "scripts/harness/")
EXEC_PLANS_DIR = "docs/exec-plans"


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def read_staged(path: str) -> str:
    """Read a path's content from the git index (the staged version)."""
    return _git(["show", f":{path}"])


def staged_files() -> list[str]:
    """Staged paths to check, including deletes/renames (D), not just A/C/M.

    A staged delete of an application file is still an edit outside the plan's
    covers: and must be authorised. Rename detection is off, so a rename shows
    as delete(old) + add(new) and both paths are checked.
    """
    out = _git(["diff", "--cached", "--name-only", "--diff-filter=ACMD"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def staged_plan_files() -> list[str]:
    """Plan files present in the *index* (committed + staged this commit).

    Reads from the index, not the worktree, so unstaged edits to a plan's
    covers: cannot authorise a commit. Both the active plan
    (docs/exec-plans/active/*.md) and completed plans moved to the
    docs/exec-plans/ root grant coverage — this is what makes the documented
    "move the plan out of active/, then commit" completion flow committable.
    Templates (leading underscore) are skipped.
    """
    out = _git(["ls-files", "--cached", "--", f"{EXEC_PLANS_DIR}/"])
    plans: list[str] = []
    for path in (line.strip() for line in out.splitlines() if line.strip()):
        if not path.endswith(".md"):
            continue
        rel = path[len(EXEC_PLANS_DIR) + 1:]  # strip "docs/exec-plans/"
        name = rel.split("/")[-1]
        if name.startswith("_"):
            continue  # _template.md
        # only the active dir and the exec-plans root hold plans
        if rel == name or rel == f"active/{name}":
            plans.append(path)
    return plans


def parse_covers(text: str) -> list[str]:
    """Extract the ``covers:`` list from a plan's YAML frontmatter text.

    Hand-parsed (stdlib only): the frontmatter is the block between the first
    two ``---`` lines; ``covers:`` is a block list of ``- <path>`` items.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    # frontmatter ends at the next '---'
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    fm = lines[1:end]

    covers: list[str] = []
    in_covers = False
    for line in fm:
        stripped = line.strip()
        if not in_covers:
            if stripped.startswith("covers:"):
                inline = stripped[len("covers:"):].strip()
                if inline and inline != "[]":
                    # flow list: `covers: [a, b]`
                    covers.extend(
                        p for p in (
                            x.strip() for x in inline.strip("[]").split(",")
                        ) if p
                    )
                    return [normalize(p) for p in covers]
                # `covers:` or `covers: []` → a block list (or nothing) follows
                in_covers = inline == ""
            continue
        # inside the block list
        if stripped.startswith("- "):
            covers.append(stripped[2:].strip())
        elif stripped and not line.startswith((" ", "\t")):
            break  # a new top-level key ends the covers block
    return [normalize(p) for p in covers if p]


def normalize(p: str) -> str:
    # strip a trailing YAML inline comment (` # ...`) before quotes/whitespace
    hash_idx = p.find(" #")
    if hash_idx != -1:
        p = p[:hash_idx]
    p = p.strip().strip("'\"")
    if p.startswith("./"):
        p = p[2:]
    return p


def covered(path: str, prefixes: list[str]) -> bool:
    for pre in prefixes:
        if pre.endswith("/"):
            if path == pre.rstrip("/") or path.startswith(pre):
                return True
        elif path == pre or path.startswith(pre + "/"):
            return True
    return False


def main() -> int:
    bypass = os.environ.get("HARNESS_BYPASS")
    if bypass:
        print(f"→ plan-coverage: BYPASSED — reason: {bypass}", file=sys.stderr)
        return 0

    files = staged_files()
    # filter out always-allowed paths
    to_check = [
        f
        for f in files
        if not f.startswith(ALWAYS_ALLOWED_PREFIXES) and f not in ALWAYS_ALLOWED_ROOT
    ]
    if not to_check:
        return 0

    plan_paths = staged_plan_files()
    prefixes: list[str] = []
    for plan in plan_paths:
        prefixes.extend(parse_covers(read_staged(plan)))

    uncovered = [f for f in to_check if not covered(f, prefixes)]
    if not uncovered:
        return 0

    print("✗ plan-coverage: staged files not authorised by any plan's covers:", file=sys.stderr)
    for f in uncovered:
        print(f"    {f}", file=sys.stderr)
    if not plan_paths:
        print(f"  no plan found in {EXEC_PLANS_DIR}/active/ — write and approve one first", file=sys.stderr)
    else:
        print(f"  covered prefixes: {prefixes or '(none)'}", file=sys.stderr)
    print("  fix: extend the active plan's covers:, log to docs/tech-debt-tracker.md, or drop the change", file=sys.stderr)
    print('  bypass: HARNESS_BYPASS="<reason>" git commit ...', file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
