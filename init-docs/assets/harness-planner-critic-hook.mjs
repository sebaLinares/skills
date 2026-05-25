#!/usr/bin/env node

/**
 * harness-planner critic hook — fires on SubagentStop, detaches a
 * codex adversarial-review against the just-written ExecPlan.
 *
 * Triggered only when subagent_type === "harness-planner". All other
 * subagents are silently passed through. The codex run is launched
 * detached and unref()'d, so this hook returns in <100ms regardless
 * of codex behaviour.
 *
 * Failure modes are all silent (exit 0): missing plugin, missing
 * plan, spawn error. Observability only — never blocks the agent
 * turn. Use `/codex:status` and `/codex:result <job-id>` to harvest
 * the verdict.
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execSync, spawn } from 'node:child_process';

function ok() { try { process.stdout.write('{}'); } catch (_) {} process.exit(0); }

function readCtx() {
  try {
    const raw = fs.readFileSync(0, 'utf-8');
    return raw ? JSON.parse(raw) : {};
  } catch (_) { return {}; }
}

function findCompanion() {
  const root = path.join(os.homedir(), '.claude', 'plugins');
  if (!fs.existsSync(root)) return null;
  try {
    const out = execSync(
      `find "${root}" -name codex-companion.mjs -type f 2>/dev/null | head -1`,
      { encoding: 'utf-8', timeout: 2000 }
    ).trim();
    return out || null;
  } catch (_) { return null; }
}

function newestPlan(cwd) {
  const dir = path.join(cwd, 'docs', 'exec-plans', 'active');
  if (!fs.existsSync(dir)) return null;
  try {
    const entries = fs.readdirSync(dir)
      .filter((f) => f.endsWith('.md') && f !== '_template.md')
      .map((f) => {
        const full = path.join(dir, f);
        return { path: full, mtime: fs.statSync(full).mtimeMs };
      })
      .sort((a, b) => b.mtime - a.mtime);
    return entries.length ? entries[0].path : null;
  } catch (_) { return null; }
}

function main() {
  const ctx = readCtx();
  if (ctx.subagent_type !== 'harness-planner') return ok();

  const companion = findCompanion();
  if (!companion) {
    process.stderr.write('harness-planner-critic-hook: codex-plugin-cc not installed; skipping\n');
    return ok();
  }

  const cwd = ctx.cwd || process.cwd();
  const planPath = newestPlan(cwd);
  if (!planPath) {
    process.stderr.write('harness-planner-critic-hook: no active ExecPlan found; skipping\n');
    return ok();
  }

  const rel = path.relative(cwd, planPath) || planPath;
  const focus =
    `Adversarial review of the ExecPlan draft at ${rel}. ` +
    `Challenge design choices, hidden assumptions, sequencing, and rollback. ` +
    `Question whether the chosen approach is correct, not just whether it is correctly implemented.`;

  try {
    const child = spawn(
      'node',
      [companion, 'adversarial-review', '--background', focus],
      { cwd, detached: true, stdio: 'ignore' }
    );
    child.unref();
  } catch (_) {}

  return ok();
}

try { main(); } catch (_) { ok(); }
