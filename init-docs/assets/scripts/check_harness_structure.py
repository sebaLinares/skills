#!/usr/bin/env python3
"""Verify the structural invariants of a harness-scaffolded repo.

Reads the canonical manifest (_canonical_manifest.py) and asserts:

  1. Every path in EXISTENCE_REQUIRED is present on disk.
  2. Every path in FRONTMATTER_REQUIRED carries the 4-key YAML block.
  3. Every entry in REQUIRED_REFERENCES contains its required substrings.
  4. No forbidden ephemera under docs/ (FORBIDDEN_DOC_GLOBS).
  5. No absolute paths in scanned text files (ABSOLUTE_PATH_PATTERNS).
  6. docs/generated/ is not described as canonical knowledge.

Bypass: set HARNESS_BYPASS="<reason>" to short-circuit with exit 0.

The script is stdlib-only and discovers the repo root by walking up
from this file (assumes install path scripts/harness/).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import _canonical_manifest as manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_front_matter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end_marker = "\n---\n"
    end_index = content.find(end_marker, 4)
    if end_index == -1:
        return {}
    block = content[4:end_index]
    metadata: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata


def iter_text_sources() -> list[Path]:
    """Resolve every text file scanned for content checks."""
    files: set[Path] = set()
    for name in manifest.ROOT_TEXT_FILES:
        files.add(REPO_ROOT / name)
    for relative_root, patterns in manifest.TEXT_SCAN_ROOTS:
        root = REPO_ROOT / relative_root
        if not root.exists():
            continue
        for pattern in patterns:
            for path in root.rglob(pattern):
                if path.is_symlink():
                    continue
                if path.is_file():
                    files.add(path)
    script_path = Path(__file__).resolve()
    return sorted(p for p in files if p.is_file() and p.resolve() != script_path)


def check_existence() -> list[str]:
    errors: list[str] = []
    for relative_path in manifest.EXISTENCE_REQUIRED:
        target = REPO_ROOT / relative_path
        # symlinks count as present; lexists handles broken symlinks too
        if not (target.exists() or os.path.lexists(target)):
            errors.append(
                f"{relative_path}: missing required harness file. "
                "Re-run the init-docs skill in audit mode to restore it."
            )
    return errors


def check_frontmatter() -> list[str]:
    errors: list[str] = []
    required_keys = set(manifest.REQUIRED_METADATA_KEYS)
    for relative_path in manifest.FRONTMATTER_REQUIRED:
        target = REPO_ROOT / relative_path
        if not target.exists():
            # existence check already flagged it
            continue
        metadata = parse_front_matter(target)
        missing = sorted(required_keys - set(metadata))
        if missing:
            errors.append(
                f"{relative_path}: missing metadata keys "
                f"{', '.join(missing)}. Add YAML front matter with "
                "owner, status, last_reviewed, and update_trigger."
            )
    return errors


def check_required_references() -> list[str]:
    errors: list[str] = []
    for relative_path, references in manifest.REQUIRED_REFERENCES.items():
        target = REPO_ROOT / relative_path
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        for reference in references:
            if reference not in content:
                errors.append(
                    f"{relative_path}: missing required harness reference "
                    f"`{reference}`. Keep the root indices aligned with "
                    "the harness map."
                )
    return errors


def check_forbidden_docs() -> list[str]:
    errors: list[str] = []
    docs_root = REPO_ROOT / "docs"
    if not docs_root.exists():
        return errors
    for pattern in manifest.FORBIDDEN_DOC_GLOBS:
        for path in sorted(docs_root.glob(pattern)):
            if path.is_symlink() or not path.is_file():
                continue
            errors.append(
                f"{relative(path)}: forbidden ephemeral artifact under "
                "docs/. Move it to docs/generated/ or output/."
            )
    return errors


def check_text_content() -> list[str]:
    errors: list[str] = []
    absolute_re = [re.compile(p) for p in manifest.ABSOLUTE_PATH_PATTERNS]
    output_re = [
        re.compile(p, re.IGNORECASE) for p in manifest.OUTPUT_CANONICAL_PATTERNS
    ]
    for path in iter_text_sources():
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for regex in absolute_re:
            match = regex.search(content)
            if match:
                errors.append(
                    f"{relative(path)}: found local absolute path "
                    f"`{match.group(0)}`. Replace with a repo-relative "
                    "path, placeholder, or env var."
                )
                break
        for regex in output_re:
            match = regex.search(content)
            if match:
                errors.append(
                    f"{relative(path)}: docs/generated/ is being described "
                    "as canonical knowledge. Keep generated/ regenerable."
                )
                break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the structural invariants of a harness repo."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report findings to stderr but always exit 0. Used by the "
        "init-docs skill self-verification step to detect a bad install "
        "without halting the audit.",
    )
    args = parser.parse_args()

    bypass = os.environ.get("HARNESS_BYPASS", "").strip()
    if bypass:
        sys.stderr.write(
            f"HARNESS_BYPASS set ({bypass!r}); skipping harness "
            "structure check.\n"
        )
        return 0

    errors: list[str] = []
    errors.extend(check_existence())
    errors.extend(check_frontmatter())
    errors.extend(check_required_references())
    errors.extend(check_forbidden_docs())
    errors.extend(check_text_content())

    if errors:
        stream = sys.stderr if args.dry_run else sys.stdout
        stream.write("Harness structure check failed:\n\n")
        for error in errors:
            stream.write(f"- {error}\n")
        if args.dry_run:
            stream.write(
                "\n(dry-run: exit 0 despite findings)\n"
            )
            return 0
        return 1

    print("Harness structure check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
