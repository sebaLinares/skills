#!/usr/bin/env python3
"""Local spec-kit gates for the harness layered over spec-kit.

Subcommands:
    gate        full Execute gate: one active analyzed plan, plus tasks.md
    gate-lite   lite Execute gate: one active analyzed plan with a real verify:
    verify      run the active plan's verify: command
    loop        unattended-loop termination check
    closeout    re-check convergence, then set the plan to status: completed
    feature-dir print the resolved feature directory (single source of truth)
    doctor      assert this repo's harness invariants hold
    selftest    self-contained behavioural tests
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path.cwd()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


def scalar(text: str, key: str) -> str:
    prefix = f"{key}:"
    for line in frontmatter(text):
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip().strip("'\"")
    return ""


def active_plan_dirs(root: Path) -> list[Path]:
    dirs: list[Path] = []
    for plan in sorted((root / "specs").glob("*/plan.md")):
        if scalar(read_text(plan), "status") == "active":
            dirs.append(plan.parent)
    return dirs


def feature_from_json(root: Path) -> Path | None:
    feature_json = root / ".specify/feature.json"
    if not feature_json.exists():
        return None
    try:
        data = json.loads(read_text(feature_json))
    except json.JSONDecodeError as exc:
        raise SystemExit(f".specify/feature.json is invalid JSON: {exc}") from exc
    feature_dir = data.get("feature_directory")
    if not feature_dir:
        return None
    path = Path(feature_dir)
    if not path.is_absolute():
        path = root / path
    return path


def feature_from_env(root: Path) -> Path | None:
    env_dir = os.environ.get("SPECIFY_FEATURE_DIRECTORY")
    if not env_dir:
        return None
    path = Path(env_dir)
    return path if path.is_absolute() else root / path


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def plan_status(feature_dir: Path) -> str:
    plan = feature_dir / "plan.md"
    if not plan.exists():
        return ""
    return scalar(read_text(plan), "status")


def feature_hint(root: Path) -> tuple[Path, str] | None:
    """The feature spec-kit says is current, with the source that said so."""
    from_env = feature_from_env(root)
    if from_env is not None:
        if not (from_env / "plan.md").exists():
            raise SystemExit(f"SPECIFY_FEATURE_DIRECTORY has no plan.md: {from_env}")
        return from_env, "SPECIFY_FEATURE_DIRECTORY"

    from_json = feature_from_json(root)
    if from_json is not None:
        if not (from_json / "plan.md").exists():
            raise SystemExit(f"feature_directory has no plan.md: {from_json}")
        return from_json, ".specify/feature.json"

    return None


def resolve_feature_dir(root: Path) -> Path:
    # Precedence matches spec-kit's own resolution order (.specify/scripts/bash/common.sh):
    # SPECIFY_FEATURE_DIRECTORY env var, then .specify/feature.json, then a single
    # status: active plan. spec-kit decides *which* feature is current; the harness
    # only validates that the answer is still alive. A hint left pointing at a
    # completed or draft plan is stale — silently gating a finished feature is
    # worse than failing, so fall back to the single active plan when there is
    # exactly one, and refuse otherwise.
    hint = feature_hint(root)
    active = active_plan_dirs(root)

    if hint is not None:
        feature_dir, source = hint
        status = plan_status(feature_dir)
        if status == "active":
            return feature_dir
        if len(active) == 1:
            print(
                f"warning: {source} points at {rel(feature_dir, root)} "
                f"(status: {status or 'unset'}); using the single active plan "
                f"{rel(active[0], root)}",
                file=sys.stderr,
            )
            return active[0]
        detail = (
            "no specs/*/plan.md is status: active to fall back to"
            if not active
            else "multiple specs/*/plan.md are status: active, so there is no unambiguous fallback"
        )
        raise SystemExit(
            f"stale feature: {source} points at {rel(feature_dir, root)} "
            f"(status: {status or 'unset'}) and {detail}\n"
            f"  fix: point {source} at the current feature, or promote exactly "
            f"one specs/*/plan.md to status: active"
        )

    if len(active) == 1:
        return active[0]
    if not active:
        raise SystemExit("no active feature: set .specify/feature.json or promote one specs/*/plan.md to status: active")
    names = "\n".join(f"  - {rel(path, root)}" for path in active)
    raise SystemExit(f"multiple active features; set .specify/feature.json:\n{names}")


def plan_text(feature_dir: Path) -> str:
    plan = feature_dir / "plan.md"
    if not plan.exists():
        raise SystemExit(f"missing plan.md: {plan}")
    return read_text(plan)


def verify_command(feature_dir: Path) -> str:
    command = scalar(plan_text(feature_dir), "verify")
    if not command or command.startswith("<"):
        raise SystemExit(f"missing verify: in {feature_dir / 'plan.md'}")
    return command


def run_verify(feature_dir: Path, stream: bool) -> int:
    command = verify_command(feature_dir)
    if stream:
        return subprocess.run(command, cwd=repo_root(), shell=True).returncode
    result = subprocess.run(
        command,
        cwd=repo_root(),
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode


def wiring_warning() -> None:
    """Non-blocking check: is the plan-coverage sensor actually wired into pre-commit?

    feature.json / SPECIFY_FEATURE_DIRECTORY can resolve a single feature even
    when the mechanical sensor that would otherwise enforce it is disconnected
    (e.g. a hook manager like husky overwrote core.hooksPath). This never fails
    the gate — it only surfaces the disconnect so it isn't silently invisible.
    """
    sensor = Path(__file__).resolve().parent / "check_plan_coverage.py"
    if not sensor.exists():
        return
    result = subprocess.run(
        [sys.executable, str(sensor), "--doctor"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            "warning: plan-coverage sensor is not wired into pre-commit "
            "(run: python3 scripts/harness/check_plan_coverage.py --doctor)",
            file=sys.stderr,
        )


def gate() -> int:
    root = repo_root()
    wiring_warning()
    feature_dir = resolve_feature_dir(root)
    active = active_plan_dirs(root)
    text = plan_text(feature_dir)
    failures: list[str] = []
    if len(active) > 1:
        names = "\n".join(f"  - {path.relative_to(root)}" for path in active)
        failures.append(f"more than one active specs/*/plan.md (pre-commit will reject this):\n{names}")
    if scalar(text, "status") != "active":
        failures.append("plan.md must be `status: active`")
    if not scalar(text, "analyzed"):
        failures.append("plan.md must fill `analyzed:` with the review date")
    if not (feature_dir / "tasks.md").exists():
        failures.append("tasks.md must exist in the feature directory")

    if failures:
        print("harness gate failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print("fix: run /speckit-tasks and /speckit-analyze, then promote the plan", file=sys.stderr)
        return 1

    print(f"harness gate passed: {feature_dir.relative_to(root)}")
    return 0


def gate_lite() -> int:
    root = repo_root()
    wiring_warning()
    active = active_plan_dirs(root)
    if len(active) != 1:
        if not active:
            print("harness lite gate failed:", file=sys.stderr)
            print("  - exactly one active specs/*/plan.md is required", file=sys.stderr)
            return 1
        names = "\n".join(f"  - {path.relative_to(root)}" for path in active)
        print("harness lite gate failed:", file=sys.stderr)
        print("  - multiple active specs/*/plan.md files found:", file=sys.stderr)
        print(names, file=sys.stderr)
        return 1

    feature_dir = active[0]
    text = plan_text(feature_dir)
    failures: list[str] = []
    if scalar(text, "status") != "active":
        failures.append("plan.md must be `status: active`")
    if not scalar(text, "analyzed"):
        failures.append("plan.md must fill `analyzed:` with the review date")
    verify = scalar(text, "verify")
    if not verify or verify.startswith("<"):
        failures.append("plan.md must fill a real `verify:` command")

    if failures:
        print("harness lite gate failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(f"harness lite gate passed: {feature_dir.relative_to(root)}")
    return 0


TASK_RE = re.compile(r"^\s*-\s+\[\s\]\s+(T\d{3})\s+(.*)$")


def unchecked_tasks(feature_dir: Path) -> list[tuple[str, str]]:
    tasks = feature_dir / "tasks.md"
    if not tasks.exists():
        raise SystemExit(f"missing tasks.md: {tasks}")
    unchecked: list[tuple[str, str]] = []
    for line in read_text(tasks).splitlines():
        match = TASK_RE.match(line)
        if match:
            task_id, description = match.groups()
            unchecked.append((task_id, description.strip()))
    return unchecked


def loop() -> int:
    root = repo_root()
    feature_dir = resolve_feature_dir(root)
    state_path = feature_dir / ".loop-state.json"
    try:
        state = json.loads(read_text(state_path)) if state_path.exists() else {}
    except json.JSONDecodeError:
        state = {}
    iteration = int(state.get("iteration", 0)) + 1
    state_path.write_text(json.dumps({"iteration": iteration}, indent=2) + "\n", encoding="utf-8")

    remaining = unchecked_tasks(feature_dir)
    verify_green = False
    if not remaining:
        verify_green = run_verify(feature_dir, stream=False) == 0

    if not remaining and verify_green:
        # Converging is not finishing: a green loop that leaves the plan at
        # status: active blocks the next feature's gate. Name the closing move.
        print("stop-converged")
        print()
        print("Required final action - run:")
        print("  python3 scripts/harness/speckit_gate.py closeout")
        return 0
    if iteration >= 5:
        print("stop-cap")
        print()
        print("Remaining work - resume with `/speckit-implement`")
        if remaining:
            for task_id, description in remaining:
                print(f"- {task_id}: {description}")
        else:
            print("- No unchecked tasks remain, but `verify:` is still failing.")
        return 0

    print("continue")
    return 0


def set_plan_status(feature_dir: Path, status: str) -> None:
    plan = feature_dir / "plan.md"
    lines = read_text(plan).splitlines()
    if not lines or lines[0].strip() != "---":
        raise SystemExit(f"plan.md has no frontmatter to update: {plan}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise SystemExit(f"plan.md frontmatter is unterminated: {plan}") from exc
    for index in range(1, end):
        if lines[index].strip().startswith("status:"):
            lines[index] = f"status: {status}"
            break
    else:
        lines.insert(1, f"status: {status}")
    plan.write_text("\n".join(lines) + "\n", encoding="utf-8")


def closeout() -> int:
    root = repo_root()
    feature_dir = resolve_feature_dir(root)
    text = plan_text(feature_dir)
    failures: list[str] = []

    if scalar(text, "status") != "active":
        failures.append(f"plan.md is `status: {scalar(text, 'status') or 'unset'}`, not `active`")
    if (feature_dir / "tasks.md").exists():
        remaining = unchecked_tasks(feature_dir)
        if remaining:
            listed = "\n".join(f"      {task_id}: {description}" for task_id, description in remaining)
            failures.append(f"tasks.md still has unchecked tasks:\n{listed}")
    if run_verify(feature_dir, stream=True) != 0:
        failures.append("`verify:` is not green")

    if failures:
        print("harness closeout refused:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    set_plan_status(feature_dir, "completed")
    print(f"harness closeout: {rel(feature_dir, root)}/plan.md set to `status: completed`")
    print()
    print("Remaining session-exit steps (docs/processes/harness.md § Session Exit):")
    print("  - index every new/edited doc in docs/README.md")
    print("  - move load-bearing chat-only knowledge into the repo")
    print("  - log follow-up work to docs/tech-debt-tracker.md")
    return 0


GITIGNORE_REQUIRED = (
    "__pycache__/",
    "**/__pycache__/",
    "*.py[cod]",
    ".claude/settings.local.json",
    "specs/**/.loop-state.json",
)
REQUIRED_HOOKS = (
    "before_plan",
    "after_tasks",
    "before_implement",
    "after_implement",
    "after_converge",
)
HARNESS_SKILLS = ("harness-gate", "harness-verify", "harness-loop", "harness-implement-lite")
# Files a past harness version shipped and a later one retired. A repo that
# still has one never actually finished the upgrade its .harness-version claims.
RETIRED_FILES = ("scripts/harness/tasks_to_issues.sh",)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def doctor() -> int:
    """Assert the harness invariants hold in this repo.

    The version marker is written on trust: nothing else proves a scaffold or
    upgrade step actually landed. This is that proof, and the reason the skill
    refuses to advance `.harness-version` until it passes.
    """
    root = repo_root()
    results: list[tuple[str, bool, str]] = []

    def record(name: str, ok: bool, fix: str = "") -> None:
        results.append((name, ok, fix))

    marker = root / ".harness-version"
    marker_ok = marker.exists() and bool(SEMVER_RE.match(read_text(marker).strip()))
    record("harness-version", marker_ok, "write the applied semver to .harness-version")

    gitignore = root / ".gitignore"
    ignore_text = read_text(gitignore) if gitignore.exists() else ""
    ignore_lines = {line.strip() for line in ignore_text.splitlines()}
    missing_ignores = [entry for entry in GITIGNORE_REQUIRED if entry not in ignore_lines]
    record(
        "gitignore-entries",
        not missing_ignores,
        f"append to .gitignore: {', '.join(missing_ignores)}",
    )

    extensions = root / ".specify/extensions.yml"
    extensions_text = read_text(extensions) if extensions.exists() else ""
    missing_hooks = [hook for hook in REQUIRED_HOOKS if f"{hook}:" not in extensions_text]
    record(
        "extensions-hooks",
        extensions.exists() and not missing_hooks,
        "add the missing hooks to .specify/extensions.yml: "
        + (", ".join(missing_hooks) if missing_hooks else "file is absent"),
    )

    template = root / ".specify/templates/plan-template.md"
    template_text = read_text(template) if template.exists() else ""
    record(
        "plan-template-frontmatter",
        "covers:" in "\n".join(frontmatter(template_text)),
        "prepend the harness frontmatter to .specify/templates/plan-template.md",
    )
    record(
        "plan-template-constitution-check",
        "Constitution compliance:" in template_text,
        "add the harness Constitution Check gate to .specify/templates/plan-template.md",
    )

    missing_skills = [
        name for name in HARNESS_SKILLS if not (root / ".agents/skills" / name / "SKILL.md").exists()
    ]
    record(
        "harness-skills",
        not missing_skills,
        f"copy the missing skills into .agents/skills/: {', '.join(missing_skills)}",
    )
    unlinked = [name for name in HARNESS_SKILLS if not (root / ".claude/skills" / name).exists()]
    record(
        "harness-skill-symlinks",
        not unlinked,
        f"symlink into .claude/skills/: {', '.join(unlinked)}",
    )

    present_retired = [path for path in RETIRED_FILES if (root / path).exists()]
    record(
        "retired-files-removed",
        not present_retired,
        f"delete files retired by a newer harness version: {', '.join(present_retired)}",
    )

    try:
        hint = feature_hint(root)
    except SystemExit as exc:
        hint, hint_error = None, str(exc)
    else:
        hint_error = ""
    if hint_error:
        record("feature-hint-resolves", False, hint_error)
    elif hint is None:
        record("feature-hint-resolves", True)
    else:
        feature_dir, source = hint
        status = plan_status(feature_dir)
        record(
            "feature-hint-resolves",
            status == "active",
            f"{source} points at {rel(feature_dir, root)} (status: {status or 'unset'}); "
            "repoint it or promote that plan",
        )

    sensor = root / "scripts/harness/check_plan_coverage.py"
    if not sensor.exists():
        record("pre-commit-wired", False, "scripts/harness/check_plan_coverage.py is missing")
    else:
        wired = subprocess.run(
            [sys.executable, str(sensor), "--doctor"], capture_output=True, text=True
        )
        if wired.returncode == 2:
            # Usage error, not an unwired hook: this sensor predates --doctor,
            # so the repo is running a stale copy whatever .harness-version says.
            record(
                "pre-commit-wired",
                False,
                "scripts/harness/check_plan_coverage.py does not support --doctor; "
                "it predates harness 2.0.0 — copy the current sensor into place",
            )
        else:
            record(
                "pre-commit-wired",
                wired.returncode == 0,
                "run: python3 scripts/harness/check_plan_coverage.py --doctor",
            )

    for name, ok, fix in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok and fix:
            print(f"  fix: {fix}", file=sys.stderr)

    failed = [name for name, ok, _ in results if not ok]
    if failed:
        print(f"doctor: FAIL ({len(failed)}/{len(results)} checks)", file=sys.stderr)
        return 1
    print(f"doctor: PASS ({len(results)} checks)")
    return 0


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "selftest@example.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Self Test"], cwd=path, check=True)


def run_self_case(
    root: Path, args: list[str], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )


def expect(name: str, actual: bool) -> bool:
    print(f"{name}: {'PASS' if actual else 'FAIL'}")
    return actual


def scaffold_healthy_repo(root: Path) -> None:
    """Build the minimum repo state `doctor` should call clean."""
    init_git_repo(root)
    write(root / ".harness-version", "9.9.9\n")
    write(root / ".gitignore", "\n".join(GITIGNORE_REQUIRED) + "\n")
    write(
        root / ".specify/extensions.yml",
        "hooks:\n" + "".join(f"  {hook}:\n    - extension: harness\n" for hook in REQUIRED_HOOKS),
    )
    write(
        root / ".specify/templates/plan-template.md",
        "---\nstatus: draft\ncovers: []\nverify: <command>\n---\n\n- Constitution compliance: yes\n",
    )
    for name in HARNESS_SKILLS:
        write(root / ".agents/skills" / name / "SKILL.md", f"# {name}\n")
        write(root / ".claude/skills" / name / "SKILL.md", f"# {name}\n")
    shutil.copy(
        Path(__file__).resolve().parent / "check_plan_coverage.py",
        write_dir(root / "scripts/harness") / "check_plan_coverage.py",
    )
    write(
        write_dir(root / ".git/hooks") / "pre-commit",
        "#!/bin/sh\npython3 scripts/harness/check_plan_coverage.py\n",
    )


def write_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def doctor_selftest() -> bool:
    ok = True
    with tempfile.TemporaryDirectory(prefix="speckit-doctor-") as tmp:
        root = Path(tmp)
        scaffold_healthy_repo(root)
        result = run_self_case(root, ["doctor"])
        ok = expect("doctor-clean-repo-passes", result.returncode == 0) and ok

        gitignore = root / ".gitignore"
        gitignore.write_text(
            "\n".join(entry for entry in GITIGNORE_REQUIRED if "loop-state" not in entry) + "\n",
            encoding="utf-8",
        )
        result = run_self_case(root, ["doctor"])
        ok = expect(
            "doctor-detects-missing-gitignore-line",
            result.returncode == 1 and "gitignore-entries: FAIL" in result.stdout,
        ) and ok
        write(gitignore, "\n".join(GITIGNORE_REQUIRED) + "\n")

        # The exact drift found in the reference repo: marker says a version
        # whose delta retires this file, but the file is still there.
        write(root / RETIRED_FILES[0], "#!/usr/bin/env bash\n")
        result = run_self_case(root, ["doctor"])
        ok = expect(
            "doctor-detects-retired-file",
            result.returncode == 1 and "retired-files-removed: FAIL" in result.stdout,
        ) and ok
        (root / RETIRED_FILES[0]).unlink()

        write(root / "specs/001-demo/plan.md", "---\nstatus: completed\n---\n# Plan\n")
        write(root / ".specify/feature.json", json.dumps({"feature_directory": "specs/001-demo"}) + "\n")
        result = run_self_case(root, ["doctor"])
        ok = expect(
            "doctor-detects-stale-feature-json",
            result.returncode == 1 and "feature-hint-resolves: FAIL" in result.stdout,
        ) and ok
    return ok


def selftest() -> int:
    if not shutil.which("git"):
        print("selftest: git not found", file=sys.stderr)
        return 1

    ok = doctor_selftest()
    with tempfile.TemporaryDirectory(prefix="speckit-gate-") as tmp:
        root = Path(tmp)
        init_git_repo(root)
        feature = root / "specs/001-demo"
        write(feature / "plan.md", """---
status: draft
analyzed:
verify: true
---
# Plan
""")
        write(feature / "tasks.md", "- [ ] T001 Do one thing\n")
        result = run_self_case(root, ["gate"])
        ok = expect("gate-draft-blocks", result.returncode == 1) and ok

        write(feature / "plan.md", """---
status: active
analyzed:
verify: true
---
# Plan
""")
        result = run_self_case(root, ["gate"])
        ok = expect("gate-missing-analyzed-blocks", result.returncode == 1) and ok

        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        result = run_self_case(root, ["gate"])
        ok = expect("gate-active-allows", result.returncode == 0) and ok

        (feature / "tasks.md").unlink()
        result = run_self_case(root, ["gate-lite"])
        ok = expect("gate-lite-active-analyzed-verify-allows-without-tasks", result.returncode == 0) and ok

        write(feature / "plan.md", """---
status: active
analyzed:
verify: true
---
# Plan
""")
        result = run_self_case(root, ["gate-lite"])
        ok = expect("gate-lite-missing-analyzed-blocks", result.returncode == 1) and ok

        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        write(feature / "tasks.md", "- [ ] T001 Do one thing\n")
        result = run_self_case(root, ["loop"])
        ok = expect("loop-continue", result.stdout.strip() == "continue") and ok

        write(feature / "tasks.md", "- [x] T001 Do one thing\n")
        result = run_self_case(root, ["loop"])
        ok = expect(
            "loop-stop-converged-names-closeout",
            result.stdout.startswith("stop-converged\n") and "closeout" in result.stdout,
        ) and ok

        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: false
---
# Plan
""")
        write(feature / "tasks.md", "- [ ] T001 Do one thing\n")
        write(feature / ".loop-state.json", '{"iteration": 4}\n')
        result = run_self_case(root, ["loop"])
        ok = expect("loop-stop-cap", result.stdout.startswith("stop-cap\n")) and ok

        # feature.json resolves unambiguously, but a second active plan exists
        # elsewhere: gate must still fail, because pre-commit's plan-coverage
        # sensor (which reads the index independently) will reject the commit.
        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        write(feature / "tasks.md", "- [ ] T001 Do one thing\n")
        write(root / "specs/002-other/plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        write(root / ".specify/feature.json", json.dumps({"feature_directory": "specs/001-demo"}) + "\n")
        result = run_self_case(root, ["gate"])
        ok = expect("gate-feature-json-resolves-but-two-active-blocks", result.returncode == 1) and ok

        # SPECIFY_FEATURE_DIRECTORY takes precedence over feature.json (matches
        # spec-kit's own resolution order). Demote the second plan first so
        # only the uniqueness check doesn't interfere with this case.
        write(root / "specs/002-other/plan.md", """---
status: draft
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        write(root / ".specify/feature.json", json.dumps({"feature_directory": "specs/002-other"}) + "\n")
        env = os.environ.copy()
        env["SPECIFY_FEATURE_DIRECTORY"] = "specs/001-demo"
        result = run_self_case(root, ["gate"], env=env)
        ok = expect("gate-env-var-wins-over-feature-json", result.returncode == 0) and ok

        # feature.json left pointing at a plan that is no longer active is a
        # stale hint, not an instruction to gate a finished feature. With one
        # active plan it falls back and warns; with none it must fail loudly.
        result = run_self_case(root, ["gate"])
        ok = expect(
            "gate-stale-feature-json-falls-back",
            result.returncode == 0 and "warning:" in result.stderr,
        ) and ok

        result = run_self_case(root, ["feature-dir"])
        ok = expect(
            "feature-dir-matches-fallback",
            result.stdout.strip().endswith("specs/001-demo"),
        ) and ok

        write(feature / "plan.md", """---
status: completed
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        result = run_self_case(root, ["gate"])
        ok = expect(
            "gate-stale-feature-json-no-active-fails",
            result.returncode == 1 and "stale feature" in result.stderr,
        ) and ok

        # closeout: convergence is re-checked, not trusted.
        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        write(feature / "tasks.md", "- [ ] T001 Do one thing\n")
        result = run_self_case(root, ["closeout"])
        ok = expect("closeout-refuses-unchecked-tasks", result.returncode == 1) and ok

        write(feature / "tasks.md", "- [x] T001 Do one thing\n")
        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: false
---
# Plan
""")
        result = run_self_case(root, ["closeout"])
        ok = expect("closeout-refuses-red-verify", result.returncode == 1) and ok

        write(feature / "plan.md", """---
status: active
analyzed: 2026-07-21
verify: true
---
# Plan
""")
        result = run_self_case(root, ["closeout"])
        ok = expect(
            "closeout-completes-plan",
            result.returncode == 0
            and scalar(read_text(feature / "plan.md"), "status") == "completed",
        ) and ok

    return 0 if ok else 1


COMMANDS = ("gate", "gate-lite", "verify", "loop", "closeout", "feature-dir", "doctor", "selftest")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: speckit_gate.py {{{'|'.join(COMMANDS)}}}", file=sys.stderr)
        return 2
    command = sys.argv[1]
    if command == "selftest":
        return selftest()
    if command == "doctor":
        return doctor()
    if command == "gate":
        return gate()
    if command == "gate-lite":
        return gate_lite()
    if command == "closeout":
        return closeout()
    feature_dir = resolve_feature_dir(repo_root())
    if command == "feature-dir":
        print(feature_dir)
        return 0
    if command == "verify":
        return run_verify(feature_dir, stream=True)
    if command == "loop":
        return loop()
    return 2


if __name__ == "__main__":
    sys.exit(main())
