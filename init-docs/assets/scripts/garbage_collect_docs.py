#!/usr/bin/env python3
"""Audit docs/ for entropy, orphans, and stale contracts.

Two-pass metadata model:

  - Strict pass on FRONTMATTER_REQUIRED — missing/invalid metadata → error.
  - Lenient pass on every other doc — missing metadata is silently
    accepted (analysis docs, exec-plans, etc., have their own
    lightweight schemas).

Other findings:

  - broken-reference  : a `docs/...` path mentioned in text doesn't exist.
  - ephemeral-doc     : matches FORBIDDEN_DOC_GLOBS.
  - orphan-doc        : no inbound references from repo-owned files,
                        excluding ORPHAN_EXCLUDED_PREFIXES.
  - stale-review      : last_reviewed older than --max-age-days.

Bypass: set HARNESS_BYPASS="<reason>" to short-circuit with exit 0.

The script is stdlib-only.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import _canonical_manifest as manifest


def discover_adr_files(repo_root: Path) -> dict[str, Path]:
    """Best-effort slug → file resolver for ADRs. Errors silenced —
    check_harness_structure.py is the authority for slug-uniqueness
    and missing-id reporting; the GC just needs the set of resolved
    files so it applies the strict frontmatter pass to them."""
    by_slug: dict[str, Path] = {}
    decisions_root = repo_root / "docs" / "decisions"
    if not decisions_root.exists():
        return by_slug
    for path in sorted(decisions_root.glob("*.md")):
        if path.is_symlink() or not path.is_file():
            continue
        if path.name.lower() == "readme.md":
            continue
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            continue
        end = content.find("\n---\n", 4)
        if end == -1:
            continue
        for line in content[4:end].splitlines():
            stripped = line.strip()
            if stripped.startswith("id:"):
                slug = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if slug and slug not in by_slug:
                    by_slug[slug] = path
                break
    return by_slug


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_REFERENCE_RE = re.compile(r"\bdocs/[A-Za-z0-9_./-]+\.(?:md|json|csv)\b")


@dataclass(frozen=True)
class Finding:
    severity: str  # "error" | "warning"
    category: str
    subject: str
    detail: str


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_front_matter(path: Path) -> dict[str, str]:
    content = read_text(path)
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
                files.add(path)
    return sorted(files)


def iter_docs_files() -> list[Path]:
    docs_root = REPO_ROOT / "docs"
    if not docs_root.exists():
        return []
    files: set[Path] = set()
    for pattern in ("*.md", "*.json", "*.csv"):
        for path in docs_root.rglob(pattern):
            if path.is_symlink() or not path.is_file():
                continue
            files.add(path)
    return sorted(files)


def build_inbound_index(
    sources: list[Path],
) -> tuple[dict[Path, set[Path]], list[Finding]]:
    inbound: dict[Path, set[Path]] = defaultdict(set)
    findings: list[Finding] = []
    for source in sources:
        try:
            content = read_text(source)
        except (UnicodeDecodeError, PermissionError):
            continue
        for match in DOC_REFERENCE_RE.finditer(content):
            raw_path = match.group(0)
            target = REPO_ROOT / raw_path
            if not target.exists():
                findings.append(
                    Finding(
                        severity="error",
                        category="broken-reference",
                        subject=relative(source),
                        detail=f"references missing path `{raw_path}`",
                    )
                )
                continue
            if target.resolve() == source.resolve():
                continue
            inbound[target.resolve()].add(source)
    return inbound, findings


def metadata_findings(
    docs_files: list[Path], max_age_days: int
) -> list[Finding]:
    findings: list[Finding] = []
    today = date.today()
    frontmatter_strict = {
        (REPO_ROOT / p).resolve() for p in manifest.FRONTMATTER_REQUIRED
    }
    # ADRs identified by slug are also strict — resolve and add.
    for slug, path in discover_adr_files(REPO_ROOT).items():
        if slug in manifest.ADR_SLUGS_REQUIRED:
            frontmatter_strict.add(path.resolve())
    required_keys = set(manifest.REQUIRED_METADATA_KEYS)

    candidates = set(docs_files)
    # Strict pass also covers FRONTMATTER_REQUIRED files outside docs/.
    for relative_path in manifest.FRONTMATTER_REQUIRED:
        target = REPO_ROOT / relative_path
        if target.is_file():
            candidates.add(target)

    for path in sorted(candidates):
        if path.suffix != ".md":
            continue
        strict = path.resolve() in frontmatter_strict
        metadata = parse_front_matter(path)
        missing = sorted(required_keys - set(metadata))

        if missing:
            if strict:
                findings.append(
                    Finding(
                        severity="error",
                        category="missing-metadata",
                        subject=relative(path),
                        detail=(
                            "missing metadata keys: "
                            f"{', '.join(missing)}"
                        ),
                    )
                )
            # lenient: silently accept missing metadata
            continue

        raw_last_reviewed = metadata.get("last_reviewed", "")
        try:
            reviewed = date.fromisoformat(raw_last_reviewed)
        except ValueError:
            findings.append(
                Finding(
                    severity="error" if strict else "warning",
                    category="invalid-last-reviewed",
                    subject=relative(path),
                    detail=(
                        f"invalid last_reviewed value `{raw_last_reviewed}`"
                    ),
                )
            )
            continue

        age_days = (today - reviewed).days
        if age_days > max_age_days:
            findings.append(
                Finding(
                    severity="warning",
                    category="stale-review",
                    subject=relative(path),
                    detail=f"last reviewed {age_days} days ago",
                )
            )
    return findings


def forbidden_docs_findings(docs_files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in docs_files:
        rel = relative(path).replace(os.sep, "/")
        # strip leading docs/ so the glob matches the documented form
        if rel.startswith("docs/"):
            inner = rel[len("docs/"):]
        else:
            inner = rel
        for pattern in manifest.FORBIDDEN_DOC_GLOBS:
            # Patterns are written relative to docs/ (e.g. "**/daily-*.md").
            # fnmatch with the bare path or with the parent path both work
            # because ** simply collapses to "any prefix".
            if fnmatch.fnmatch(inner, pattern.lstrip("*/")):
                findings.append(
                    Finding(
                        severity="error",
                        category="ephemeral-doc",
                        subject=rel,
                        detail=(
                            "ephemeral or derived artifact should live "
                            "in docs/generated/ or output/"
                        ),
                    )
                )
                break
            if fnmatch.fnmatch(path.name, pattern.split("/")[-1]):
                findings.append(
                    Finding(
                        severity="error",
                        category="ephemeral-doc",
                        subject=rel,
                        detail=(
                            "ephemeral or derived artifact should live "
                            "in docs/generated/ or output/"
                        ),
                    )
                )
                break
    return findings


def orphan_findings(
    docs_files: list[Path], inbound: dict[Path, set[Path]]
) -> list[Finding]:
    findings: list[Finding] = []
    excluded = manifest.ORPHAN_EXCLUDED_PREFIXES
    for path in docs_files:
        rel = relative(path).replace(os.sep, "/")
        if any(rel.startswith(prefix) for prefix in excluded):
            continue
        if path.suffix not in {".md", ".json", ".csv"}:
            continue
        if inbound.get(path.resolve()):
            continue
        findings.append(
            Finding(
                severity="warning",
                category="orphan-doc",
                subject=rel,
                detail=(
                    "no inbound references found from repo-owned docs, "
                    "scripts, agents, or hooks"
                ),
            )
        )
    return findings


def render_report(findings: list[Finding], max_age_days: int) -> str:
    lines = [
        "# Harness Garbage Collection Report",
        "",
        f"- Repository: `{REPO_ROOT.name}`",
        f"- Date: `{date.today().isoformat()}`",
        f"- Stale review threshold: `{max_age_days}` days",
        "",
    ]

    if not findings:
        lines.append("No garbage-collection findings.")
        return "\n".join(lines) + "\n"

    by_category: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        by_category[finding.category].append(finding)

    severity_order = {"error": 0, "warning": 1}
    ordered = sorted(
        findings,
        key=lambda f: (
            severity_order.get(f.severity, 99),
            f.category,
            f.subject,
        ),
    )

    error_count = sum(1 for f in findings if f.severity == "error")
    warning_count = sum(1 for f in findings if f.severity == "warning")

    lines.extend(
        [
            "## Summary",
            "",
            f"- Errors: `{error_count}`",
            f"- Warnings: `{warning_count}`",
            "",
            "## Findings",
            "",
        ]
    )
    for item in ordered:
        lines.append(f"- [{item.severity}] `{item.subject}`: {item.detail}")

    lines.extend(["", "## Categories", ""])
    for category in sorted(by_category):
        lines.append(f"- `{category}`: `{len(by_category[category])}`")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit docs/ for entropy, orphaned knowledge, and "
            "stale contracts."
        )
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=90,
        help="Flag docs whose last_reviewed is older than this many days.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path to write the markdown report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any finding (error or warning) is "
        "detected. Default returns non-zero only on errors.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Always exit 0 regardless of findings. Used by the "
        "init-docs skill self-verification step.",
    )
    args = parser.parse_args()

    bypass = os.environ.get("HARNESS_BYPASS", "").strip()
    if bypass:
        sys.stderr.write(
            f"HARNESS_BYPASS set ({bypass!r}); skipping garbage "
            "collection.\n"
        )
        return 0

    text_sources = iter_text_sources()
    docs_files = iter_docs_files()
    inbound, reference_findings = build_inbound_index(text_sources)

    findings: list[Finding] = []
    findings.extend(reference_findings)
    findings.extend(metadata_findings(docs_files, args.max_age_days))
    findings.extend(forbidden_docs_findings(docs_files))
    findings.extend(orphan_findings(docs_files, inbound))

    report = render_report(findings, args.max_age_days)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    print(report, end="")

    if args.dry_run:
        return 0
    if args.strict:
        return 1 if findings else 0
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
