#!/usr/bin/env node

/**
 * harness-planner critic hook — fires on SubagentStop, runs codex
 * adversarial-review synchronously against the just-written ExecPlan,
 * and writes the verdict into the plan's "## Pre-approval critic
 * transcript" section. See ADR pre-approval-critic-gate.
 *
 * Triggered only when agent_type/subagent_type === "harness-planner".
 * All other subagents are passed through (exit 0).
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

function maybeDumpUnmatched(ctx) {
  try {
    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    const out = `/tmp/harness-hook-no-match-${ts}.json`;
    fs.writeFileSync(out, JSON.stringify(ctx, null, 2));
    process.stderr.write(`harness-planner-critic-hook: payload dumped to ${out}\n`);
  } catch (_) { /* never throw from a hook */ }
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

function criticSectionBody(planPath) {
  const original = fs.readFileSync(planPath, 'utf-8');
  const lines = original.split('\n');
  const startIdx = lines.findIndex((l) => l.trim() === SECTION_HEADING);
  if (startIdx === -1) return '';

  let endIdx = lines.length;
  for (let i = startIdx + 1; i < lines.length; i++) {
    if (lines[i].startsWith('## ')) { endIdx = i; break; }
  }
  return lines.slice(startIdx + 1, endIdx).join('\n');
}

function indent(body, spaces) {
  const pad = ' '.repeat(spaces);
  return body.split('\n').map((l) => l ? pad + l : l).join('\n');
}

function formatRun(n, stamp, body) {
  return `**Run ${n} — ${stamp} — ${CRITIC_CMD}**\n\n${body.trim()}\n`;
}

function formatCapReached(n, stamp) {
  return `**Run ${n} — ${stamp} — cap-reached**\n\n` +
    `CAP_REACHED: Pre-approval critic has already run twice on this plan\n` +
    `(see ADR pre-approval-critic-gate § Iteration cap). The lead must\n` +
    `choose one of:\n\n` +
    `1. **Ship with residuals.** Append the unresolved findings to the\n` +
    `   plan's Decision Log as accepted residuals, with rationale.\n` +
    `   Approve the plan and proceed.\n` +
    `2. **Scope-split.** Identify the milestone(s) that can ship now vs.\n` +
    `   defer. Create a new ExecPlan for the shipping slice; the deferred\n` +
    `   work returns to Phase 2 for a fresh analysis.\n` +
    `3. **Escalate to re-analysis.** The critic surfaced an unresolved\n` +
    `   design question. Halt Phase 5, write or amend the analysis doc,\n` +
    `   settle the question, then re-dispatch harness-planner under a\n` +
    `   reset scope.\n\n` +
    `To override (genuinely new scope, not iteration of the same scope),\n` +
    `re-dispatch harness-planner with HARNESS_CRITIC_FORCE="<reason>" set\n` +
    `in the env. The reason is logged in this section.\n`;
}

function appendRunBlock(planPath, block) {
  const original = fs.readFileSync(planPath, 'utf-8');
  const lines = original.split('\n');
  const startIdx = lines.findIndex((l) => l.trim() === SECTION_HEADING);

  let updated;
  if (startIdx === -1) {
    const trimmed = original.replace(/\s+$/, '');
    updated = `${trimmed}\n\n${SECTION_HEADING}\n\n${block}\n`;
  } else {
    let endIdx = lines.length;
    for (let i = startIdx + 1; i < lines.length; i++) {
      if (lines[i].startsWith('## ')) { endIdx = i; break; }
    }
    const sectionBody = lines.slice(startIdx + 1, endIdx).join('\n');

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

function writeRun(planPath, verdictBody) {
  const sectionBody = criticSectionBody(planPath);
  const runN = countRuns(sectionBody) + 1;
  appendRunBlock(planPath, formatRun(runN, utcStamp(), verdictBody));
}

function writeCapReachedBlock(planPath, runN) {
  appendRunBlock(planPath, formatCapReached(runN, utcStamp()));
}

function main() {
  const ctx = readCtx();
  // Claude Code documents agent_type; subagent_type is retained as a
  // compatibility fallback. See ADR pre-approval-critic-gate.
  const identity = ctx.agent_type ?? ctx.subagent_type;
  if (identity !== 'harness-planner') {
    maybeDumpUnmatched(ctx);
    return ok();
  }

  const cwd = ctx.cwd || process.cwd();
  const planPath = newestPlan(cwd);
  if (!planPath) {
    process.stderr.write('harness-planner-critic-hook: no active ExecPlan found; skipping\n');
    return ok();
  }

  const sectionBody = criticSectionBody(planPath);
  const existingRuns = countRuns(sectionBody);
  const forceReason = process.env.HARNESS_CRITIC_FORCE;
  if (existingRuns >= 2 && !forceReason) {
    writeCapReachedBlock(planPath, existingRuns + 1);
    process.stderr.write(
      'harness-planner-critic-hook: 2-round cap reached. ' +
      'Set HARNESS_CRITIC_FORCE="<reason>" to override.\n'
    );
    return ok();
  }
  const writeCriticRun = (body) => writeRun(
    planPath,
    existingRuns >= 2 && forceReason
      ? `HARNESS_CRITIC_FORCE: ${forceReason}\n\n${body}`
      : body
  );

  const companion = findCompanion();
  if (!companion) {
    writeCriticRun(
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
    writeCriticRun(`BLOCKED: hook failed to spawn codex-companion — ${err.message || String(err)}.`);
    return ok();
  }

  if (result.error) {
    const code = result.error.code || 'unknown';
    if (code === 'ETIMEDOUT') {
      writeCriticRun(
        `BLOCKED: codex adversarial-review timed out after ${TIMEOUT_MS / 1000}s.\n\n` +
        'Run the critic out-of-band and paste the verdict here, or shrink the plan ' +
        'and re-invoke harness-planner.'
      );
    } else {
      writeCriticRun(`BLOCKED: codex adversarial-review spawn error (${code}) — ${result.error.message || ''}`);
    }
    return ok();
  }

  if (result.status !== 0) {
    const stderrTail = (result.stderr || '').trim().slice(-500) || '(no stderr)';
    writeCriticRun(
      `BLOCKED: codex adversarial-review exited ${result.status}.\n\n` +
      `Stderr tail:\n\n${indent(stderrTail, 4)}`
    );
    return ok();
  }

  const verdict = (result.stdout || '').trim();
  if (!verdict) {
    const stderrTail = (result.stderr || '').trim().slice(-500) || '(no stderr)';
    writeCriticRun(
      'BLOCKED: codex adversarial-review returned empty stdout. ' +
      'This usually means the codex command is configured for async ' +
      '(--background) output; check codex-plugin-cc installation.\n\n' +
      `Stderr tail:\n\n${indent(stderrTail, 4)}`
    );
    return ok();
  }

  writeCriticRun(verdict);
  return ok();
}

try { main(); } catch (_) { ok(); }
