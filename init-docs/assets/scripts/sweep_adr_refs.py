#!/usr/bin/env python3
"""Rewrite numeric ADR references in repo docs to slug form.

Walks `docs/decisions/` to learn each ADR's identity (slug + current
filename number + optional `legacy_numbers:` from frontmatter). Then
scans the repo's text-source set (see manifest.TEXT_SCAN_ROOTS) and
rewrites:

  - Prose:        `ADR 003`        →  `ADR evaluator-gate`
  - Hyphen form:  `ADR-003`        →  `ADR evaluator-gate`
  - Link text:    `[ADR 003](...)` →  `[ADR evaluator-gate](...)`
  - Stale URLs:   `decisions/003-evaluator-gate.md` →
                  `decisions/<current-NNN>-evaluator-gate.md` (when the
                  ADR was renumbered locally and `legacy_numbers:`
                  records the old number).

Files in the writers' own contract are skipped (the ADR files themselves
edit their own `id:`/`legacy_numbers:` headers manually). Dry-run by
default; pass `--write` to apply.

After the sweep is clean (no more numeric ADR refs in the target repo),
the operator can delete each ADR's `legacy_numbers:` frontmatter — the
field is migration-only.

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
    legacy_numbers: tuple[int, ...]


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


def parse_legacy_numbers(raw: str) -> tuple[int, ...]:
    """Parse `[3, 5]` or `[]` from the frontmatter value."""
    raw = raw.strip()
    if not raw or raw == "[]":
        return ()
    inner = raw.strip("[]").strip()
    if not inner:
        return ()
    nums: list[int] = []
    for piece in inner.split(","):
        piece = piece.strip()
        if not piece:
            continue
        try:
            nums.append(int(piece))
        except ValueError:
            pass
    return tuple(nums)


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
            # No number prefix; can't sweep numeric refs by filename.
            # Still readable for slug + legacy_numbers.
            current_number = -1
        else:
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
        legacy = parse_legacy_numbers(metadata.get("legacy_numbers", ""))
        adrs.append(
            AdrIdentity(
                slug=slug,
                current_number=current_number,
                current_path=path,
                legacy_numbers=legacy,
            )
        )
    return adrs, errors


def build_number_to_slug(adrs: list[AdrIdentity]) -> dict[int, str]:
    """Both current and legacy numbers map to the slug. On collision
    (two ADRs claim the same number), prefer the current-number owner."""
    mapping: dict[int, str] = {}
    # First pass: legacy numbers (lower priority).
    for adr in adrs:
        for n in adr.legacy_numbers:
            mapping[n] = adr.slug
    # Second pass: current numbers (overwrite legacy if collision).
    for adr in adrs:
        if adr.current_number >= 0:
            mapping[adr.current_number] = adr.slug
    return mapping


def build_url_rewrites(adrs: list[AdrIdentity]) -> dict[str, str]:
    """For each ADR with legacy_numbers, map legacy URLs to current URL."""
    rewrites: dict[str, str] = {}
    for adr in adrs:
        if adr.current_number < 0:
            continue
        current_name = adr.current_path.name  # e.g. 006-pre-approval-critic-gate.md
        for legacy_n in adr.legacy_numbers:
            legacy_name = f"{legacy_n:03d}-{adr.slug}.md"
            if legacy_name != current_name:
                # Match `decisions/<legacy_name>` regardless of leading path.
                rewrites[legacy_name] = current_name
    return rewrites


def iter_target_files() -> list[Path]:
    """Files eligible for rewriting. Excludes ADRs themselves and the
    skill's own assets (which use canonical numbering)."""
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
                # Skip ADR files themselves and the harness's own
                # validator/sweep scripts — their headers, docstrings,
                # and example refs are out of scope for an automated
                # sweep.
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
    url_rewrites: dict[str, str],
) -> tuple[str, list[str]]:
    """Return (new_content, list_of_change_summaries)."""
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return "", []
    changes: list[str] = []
    content = original

    def replace_number(match: re.Match[str]) -> str:
        number = int(match.group(1))
        slug = number_to_slug.get(number)
        if not slug:
            return match.group(0)
        changes.append(f"`{match.group(0)}` → `ADR {slug}`")
        return f"ADR {slug}"

    content = ADR_NUMBER_RE.sub(replace_number, content)

    for legacy_name, current_name in url_rewrites.items():
        if legacy_name in content:
            count = content.count(legacy_name)
            content = content.replace(legacy_name, current_name)
            changes.append(
                f"`{legacy_name}` → `{current_name}` ({count} URL hit"
                f"{'s' if count != 1 else ''})"
            )
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
            "No ADRs found under docs/decisions/. Nothing to sweep.\n"
        )
        return 0

    number_to_slug = build_number_to_slug(adrs)
    url_rewrites = build_url_rewrites(adrs)

    total_files = 0
    changed_files = 0
    total_changes = 0
    for path in iter_target_files():
        new_content, changes = sweep_file(path, number_to_slug, url_rewrites)
        if not changes:
            continue
        total_files += 1
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
