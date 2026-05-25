"""Canonical-file manifest for the init-docs harness.

Single source of truth for the two validators:

- check_harness_structure.py — existence + frontmatter + cross-reference checks
- garbage_collect_docs.py    — metadata staleness, orphan and ephemeral-doc scans

Every future init-docs CHANGELOG entry that adds, renames, or removes a
canonical file MUST update this module in the same entry. The skill's
"How to update this skill" ritual treats manifest drift as an audit failure.

All paths are repo-root-relative POSIX strings.
"""

from __future__ import annotations


# Files that MUST exist in a scaffolded repo. Validators report missing
# entries as errors. Includes the scripts themselves (self-reference is
# intentional — the manifest doubles as a deployment receipt).
EXISTENCE_REQUIRED: list[str] = [
    # Repo-root anchors
    "AGENTS.md",
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    # docs/ catalog + ledgers
    "docs/README.md",
    "docs/PLANS.md",
    "docs/FEATURES.md",
    "docs/tech-debt-tracker.md",
    # docs/processes/
    "docs/processes/harness.md",
    "docs/processes/dev-setup.md",
    "docs/processes/model-policy.md",
    # docs/decisions/
    "docs/decisions/001-harness-design.md",
    "docs/decisions/002-session-exit.md",
    "docs/decisions/003-evaluator-gate.md",
    "docs/decisions/004-fleet-model-policy.md",
    "docs/decisions/005-hard-constraints.md",
    "docs/decisions/007-harness-validators.md",
    # docs/references/ + docs/generated/ (READMEs only)
    "docs/references/README.md",
    "docs/generated/README.md",
    # Subagent configs (shipped 2026-05-24)
    ".claude/agents/harness-analyst.md",
    ".claude/agents/harness-planner.md",
    # Hooks (shipped 2026-05-25)
    ".claude/hooks/harness-planner-critic-hook.mjs",
    ".claude/hooks/verify-covers-hook.sh",
    # Validators (shipped 2026-05-26)
    "scripts/harness/check_harness_structure.py",
    "scripts/harness/garbage_collect_docs.py",
    "scripts/harness/_canonical_manifest.py",
    # Version marker
    ".harness-version",
]


# Subset of EXISTENCE_REQUIRED that must additionally carry the 4-key YAML
# frontmatter block (owner / status / last_reviewed / update_trigger).
#
# Excluded by design:
#   - CLAUDE.md (symlink to AGENTS.md; would double-count)
#   - .claude/agents/*.md (own Claude Code subagent frontmatter schema;
#     verify schema compatibility before extending)
#   - .claude/hooks/*.{sh,mjs} (executables; YAML in shebang line breaks)
#   - scripts/harness/*.py (Python modules; metadata lives in this manifest)
#   - .harness-version (one-line ISO date marker; no frontmatter)
FRONTMATTER_REQUIRED: list[str] = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    "docs/README.md",
    "docs/PLANS.md",
    "docs/FEATURES.md",
    "docs/tech-debt-tracker.md",
    "docs/processes/harness.md",
    "docs/processes/dev-setup.md",
    "docs/processes/model-policy.md",
    "docs/decisions/001-harness-design.md",
    "docs/decisions/002-session-exit.md",
    "docs/decisions/003-evaluator-gate.md",
    "docs/decisions/004-fleet-model-policy.md",
    "docs/decisions/005-hard-constraints.md",
    "docs/decisions/007-harness-validators.md",
    "docs/references/README.md",
    "docs/generated/README.md",
]


REQUIRED_METADATA_KEYS: frozenset[str] = frozenset(
    {"owner", "status", "last_reviewed", "update_trigger"}
)


# Cross-reference assertions — universal only. Every entry is a file that
# MUST mention every reference string verbatim. Repos extend this themselves.
REQUIRED_REFERENCES: dict[str, list[str]] = {
    "AGENTS.md": [
        "ARCHITECTURE.md",
        "SECURITY.md",
        "docs/README.md",
        "docs/PLANS.md",
        "docs/FEATURES.md",
        "docs/processes/harness.md",
    ],
    "docs/README.md": [
        "ARCHITECTURE.md",
        "SECURITY.md",
        "PLANS.md",
        "FEATURES.md",
        "tech-debt-tracker.md",
        "decisions/",
        "processes/",
    ],
    "docs/processes/harness.md": [
        "../decisions/001-harness-design.md",
        "../PLANS.md",
    ],
}


# Forbidden docs under docs/ — universal ephemera that belong in
# docs/generated/ or output/ (not in versioned knowledge).
FORBIDDEN_DOC_GLOBS: list[str] = [
    "**/session-handoff-*.md",
    "**/*dashboard*.md",
    "**/daily-*.md",
]


# Regex patterns flagged in any scanned text file. Match → finding.
ABSOLUTE_PATH_PATTERNS: list[str] = [
    r"/Users/[^\s`\"')]+",
    r"/private/tmp/[^\s`\"')]+",
    r"/var/folders/[^\s`\"')]+",
    r"/home/[^\s`\"')]+",
]


# Patterns flagged when docs/generated/ is described as canonical knowledge.
# The convention (see docs/generated/README.md) is that generated/ is
# regenerable, not load-bearing.
OUTPUT_CANONICAL_PATTERNS: list[str] = [
    r"docs/generated/.*(only|canonical|stable) source of truth",
    r"(only|canonical|stable) source of truth.*docs/generated/",
]


# Roots walked by both validators when scanning text content. Each entry is
# (path-from-repo-root, glob-patterns).
TEXT_SCAN_ROOTS: list[tuple[str, tuple[str, ...]]] = [
    ("docs", ("*.md", "*.json", "*.csv")),
    ("scripts", ("*.py", "*.sh", "*.md")),
    (".claude/agents", ("*.md",)),
    (".claude/hooks", ("*.sh", "*.mjs", "*.js", "*.py")),
]


# Repo-root files included in text scans (top-level guides).
# CLAUDE.md is excluded — symlink to AGENTS.md.
ROOT_TEXT_FILES: list[str] = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
]


# Paths under docs/ excluded from the orphan-doc check. Files in these
# subtrees are allowed to be referenced only externally or not at all.
ORPHAN_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "docs/exec-plans/completed/",
    "docs/analysis/",
    "docs/tickets/",
)
