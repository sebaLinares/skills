#!/usr/bin/env python3
"""Rewrite numeric ADR references in repo docs to slug form.

One-way legacy-migration tool. Walks `docs/decisions/` to learn each
ADR's identity (slug from frontmatter `id:` plus its current filename
number, parsed from a `NNN-<slug>.md` filename if still present). Then
scans the repo's text-source set (see manifest.TEXT_SCAN_ROOTS) and
rewrites:

  - Prose:        `ADR 003`        →  `ADR evaluator-gate`
  - Hyphen form:  `ADR-003`        →  `ADR evaluator-gate`
  - Link text:    `[ADR 003](...)` →  `[ADR evaluator-gate](...)`

Once the operator has renamed `NNN-<slug>.md` files to `<slug>.md` (per
the migration entry in the harness CHANGELOG), the number→slug map is
empty and this tool is a no-op. The skill no longer ships ADRs with
filename numbers — this tool exists for one-shot migration from the
pre-slug-canonical harness model.

Files under `docs/decisions/` and `scripts/harness/` are excluded from
the rewrite target set — their headers, docstrings, and example refs
are out of scope for an automated sweep. Dry-run by default; pass
`--write` to apply.

Bypass: `HARNESS_BYPASS="<reason>"` short-circuits exit 0.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import _canonical_manifest as manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AdrIdentity:
    slug: str
    current_number: int
    current_path: Path


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_front_matter(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}
    metadata: dict[str, str] = {}
    for raw_line in content[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata


FILENAME_NUMBER_RE = re.compile(r"^(\d+)-(.+)\.md$")


def discover_adrs() -> tuple[list[AdrIdentity], list[str]]:
    adrs: list[AdrIdentity] = []
    errors: list[str] = []
    decisions_root = REPO_ROOT / "docs" / "decisions"
    if not decisions_root.exists():
        return adrs, errors
    for path in sorted(decisions_root.glob("*.md")):
        if path.is_symlink() or not path.is_file():
            continue
        if path.name.lower() == "readme.md":
            continue
        match = FILENAME_NUMBER_RE.match(path.name)
        if not match:
            # No number prefix; nothing to sweep from this file.
            continue
        current_number = int(match.group(1))
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            errors.append(f"{relative(path)}: cannot read; skipping.")
            continue
        metadata = parse_front_matter(content)
        slug = metadata.get("id", "").strip()
        if not slug:
            errors.append(
                f"{relative(path)}: missing `id:` frontmatter; skipping."
            )
            continue
        adrs.append(
            AdrIdentity(
                slug=slug,
                current_number=current_number,
                current_path=path,
            )
        )
    return adrs, errors


def build_number_to_slug(adrs: list[AdrIdentity]) -> dict[int, str]:
    return {adr.current_number: adr.slug for adr in adrs}


def iter_target_files() -> list[Path]:
    """Files eligible for rewriting. Excludes ADRs themselves and the
    skill's own scripts."""
    files: set[Path] = set()
    for name in manifest.ROOT_TEXT_FILES:
        target = REPO_ROOT / name
        if target.is_file() and not target.is_symlink():
            files.add(target)
    for relative_root, patterns in manifest.TEXT_SCAN_ROOTS:
        root = REPO_ROOT / relative_root
        if not root.exists():
            continue
        for pattern in patterns:
            for path in root.rglob(pattern):
                if path.is_symlink() or not path.is_file():
                    continue
                rel = relative(path)
                if rel.startswith("docs/decisions/"):
                    continue
                if rel.startswith("scripts/harness/"):
                    continue
                files.add(path)
    return sorted(files)


# `ADR 3`, `ADR 03`, `ADR 003`, `ADR-003` — capture the number group.
ADR_NUMBER_RE = re.compile(r"\bADR[\s-]+0*(\d+)\b")


def sweep_file(
    path: Path,
    number_to_slug: dict[int, str],
) -> tuple[str, list[str]]:
    """Return (new_content, list_of_change_summaries)."""
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return "", []
    changes: list[str] = []

    def replace_number(match: re.Match[str]) -> str:
        number = int(match.group(1))
        slug = number_to_slug.get(number)
        if not slug:
            return match.group(0)
        changes.append(f"`{match.group(0)}` → `ADR {slug}`")
        return f"ADR {slug}"

    content = ADR_NUMBER_RE.sub(replace_number, original)
    return content, changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite numeric ADR references in repo docs to slug form.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply rewrites in place. Default is dry-run (preview only).",
    )
    args = parser.parse_args()

    bypass = os.environ.get("HARNESS_BYPASS", "").strip()
    if bypass:
        sys.stderr.write(
            f"HARNESS_BYPASS set ({bypass!r}); skipping ADR sweep.\n"
        )
        return 0

    adrs, discover_errors = discover_adrs()
    if discover_errors:
        sys.stderr.write("ADR discovery issues:\n")
        for err in discover_errors:
            sys.stderr.write(f"- {err}\n")

    if not adrs:
        sys.stderr.write(
            "No numbered ADRs found under docs/decisions/. Nothing to sweep "
            "(slug-only filenames are the steady state).\n"
        )
        return 0

    number_to_slug = build_number_to_slug(adrs)

    changed_files = 0
    total_changes = 0
    for path in iter_target_files():
        new_content, changes = sweep_file(path, number_to_slug)
        if not changes:
            continue
        changed_files += 1
        total_changes += len(changes)
        print(f"\n{relative(path)}:")
        for change in changes:
            print(f"  {change}")
        if args.write:
            path.write_text(new_content, encoding="utf-8")

    if changed_files == 0:
        print("No numeric ADR references found.")
        return 0

    suffix = "applied" if args.write else "preview only (dry-run)"
    print(
        f"\nSummary: {total_changes} change"
        f"{'s' if total_changes != 1 else ''} across {changed_files} file"
        f"{'s' if changed_files != 1 else ''} — {suffix}."
    )
    if not args.write:
        print("Re-run with `--write` to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
