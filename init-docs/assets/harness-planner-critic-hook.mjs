#!/usr/bin/env node

/**
 * harness-planner critic hook — fires on SubagentStop, runs codex
 * adversarial-review synchronously against the just-written ExecPlan,
 * and writes the verdict into the plan's "## Pre-approval critic
 * transcript" section. See ADR 006.
 *
 * Triggered only when subagent_type === "harness-planner". All other
 * subagents are silently passed through (exit 0).
 *
 * Blocks the agent turn for the duration of the critic run (typically
 * 30-90s on a non-trivial plan; hard-capped at TIMEOUT_MS). The pause
 * is at the draft -> approval transition where nothing else is
 * happening; the trade is visible latency for a populated verdict on
 * first read.
 *
 * Failure modes write a BLOCKED: <reason> placeholder into the section
 * in place of a verdict:
 *   - codex-plugin-cc not installed on this machine
 *   - codex-companion.mjs spawn failure
 *   - codex adversarial-review timeout
 *   - codex adversarial-review non-zero exit
 *   - codex stdout empty (unexpected; emit stderr tail for diagnostics)
 *
 * The empty-section gate (PLANS.md -> "The `Pre-approval critic
 * transcript` section") fires loudly on BLOCKED — the lead does not
 * approve a plan whose section is empty or BLOCKED.
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execSync, spawnSync } from 'node:child_process';

const SECTION_HEADING = '## Pre-approval critic transcript';
const CRITIC_CMD = 'codex:adversarial-review';
const TIMEOUT_MS = 10 * 60 * 1000;
const PLACEHOLDER_STUB = /^\s*_No runs yet\._\s*$/m;

function ok() {
  try { process.stdout.write('{}'); } catch (_) {}
  process.exit(0);
}

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

function utcStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}Z`;
}

function countRuns(sectionBody) {
  const matches = sectionBody.match(/^\*\*Run \d+\b/gm) || [];
  return matches.length;
}

function indent(body, spaces) {
  const pad = ' '.repeat(spaces);
  return body.split('\n').map((l) => l ? pad + l : l).join('\n');
}

function formatRun(n, stamp, body) {
  return `**Run ${n} — ${stamp} — ${CRITIC_CMD}**\n\n${body.trim()}\n`;
}

function writeRun(planPath, verdictBody) {
  const stamp = utcStamp();
  const original = fs.readFileSync(planPath, 'utf-8');
  const lines = original.split('\n');
  const startIdx = lines.findIndex((l) => l.trim() === SECTION_HEADING);

  let updated;
  if (startIdx === -1) {
    const block = formatRun(1, stamp, verdictBody);
    const trimmed = original.replace(/\s+$/, '');
    updated = `${trimmed}\n\n${SECTION_HEADING}\n\n${block}\n`;
  } else {
    let endIdx = lines.length;
    for (let i = startIdx + 1; i < lines.length; i++) {
      if (lines[i].startsWith('## ')) { endIdx = i; break; }
    }
    const sectionBody = lines.slice(startIdx + 1, endIdx).join('\n');
    const runN = countRuns(sectionBody) + 1;
    const block = formatRun(runN, stamp, verdictBody);

    const cleanedBody = sectionBody.replace(PLACEHOLDER_STUB, '').trim();
    const newBody = cleanedBody
      ? `${cleanedBody}\n\n${block}`
      : block;

    const before = lines.slice(0, startIdx + 1).join('\n');
    const after = endIdx < lines.length
      ? '\n' + lines.slice(endIdx).join('\n')
      : '';
    updated = `${before}\n\n${newBody}\n${after}`;
  }

  const tmp = `${planPath}.tmp`;
  fs.writeFileSync(tmp, updated);
  fs.renameSync(tmp, planPath);
}

function main() {
  const ctx = readCtx();
  if (ctx.subagent_type !== 'harness-planner') return ok();

  const cwd = ctx.cwd || process.cwd();
  const planPath = newestPlan(cwd);
  if (!planPath) {
    process.stderr.write('harness-planner-critic-hook: no active ExecPlan found; skipping\n');
    return ok();
  }

  const companion = findCompanion();
  if (!companion) {
    writeRun(
      planPath,
      'BLOCKED: codex-plugin-cc not installed on this contributor\'s machine.\n\n' +
      'Install per `docs/processes/dev-setup.md` § Toolchain, or run the critic ' +
      'out-of-band and paste the verdict here before requesting lead approval.'
    );
    process.stderr.write('harness-planner-critic-hook: codex-plugin-cc not installed; wrote BLOCKED placeholder\n');
    return ok();
  }

  const rel = path.relative(cwd, planPath) || planPath;
  const focus =
    `Adversarial review of the ExecPlan draft at ${rel}. ` +
    `Challenge design choices, hidden assumptions, sequencing, and rollback. ` +
    `Question whether the chosen approach is correct, not just whether it is correctly implemented.`;

  let result;
  try {
    result = spawnSync(
      'node',
      [companion, 'adversarial-review', focus],
      { cwd, encoding: 'utf-8', timeout: TIMEOUT_MS, stdio: ['ignore', 'pipe', 'pipe'] }
    );
  } catch (err) {
    writeRun(planPath, `BLOCKED: hook failed to spawn codex-companion — ${err.message || String(err)}.`);
    return ok();
  }

  if (result.error) {
    const code = result.error.code || 'unknown';
    if (code === 'ETIMEDOUT') {
      writeRun(
        planPath,
        `BLOCKED: codex adversarial-review timed out after ${TIMEOUT_MS / 1000}s.\n\n` +
        'Run the critic out-of-band and paste the verdict here, or shrink the plan ' +
        'and re-invoke harness-planner.'
      );
    } else {
      writeRun(planPath, `BLOCKED: codex adversarial-review spawn error (${code}) — ${result.error.message || ''}`);
    }
    return ok();
  }

  if (result.status !== 0) {
    const stderrTail = (result.stderr || '').trim().slice(-500) || '(no stderr)';
    writeRun(
      planPath,
      `BLOCKED: codex adversarial-review exited ${result.status}.\n\n` +
      `Stderr tail:\n\n${indent(stderrTail, 4)}`
    );
    return ok();
  }

  const verdict = (result.stdout || '').trim();
  if (!verdict) {
    const stderrTail = (result.stderr || '').trim().slice(-500) || '(no stderr)';
    writeRun(
      planPath,
      'BLOCKED: codex adversarial-review returned empty stdout. ' +
      'This usually means the codex command is configured for async ' +
      '(--background) output; check codex-plugin-cc installation.\n\n' +
      `Stderr tail:\n\n${indent(stderrTail, 4)}`
    );
    return ok();
  }

  writeRun(planPath, verdict);
  return ok();
}

try { main(); } catch (_) { ok(); }
