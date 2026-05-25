---
owner: {{REPO_NAME}}
status: stable
last_reviewed: 2026-05-26
update_trigger: on-security-policy-change
---

# Security

Current security posture of this service. Intentionally light — will
grow as auth, data-handling, and compliance patterns are wired in.

> Fill each section for this project. Replace placeholders. Do not
> ship to production with placeholders still in place.

## Reporting

Report vulnerabilities privately via the team's internal channels. Do
not open public issues for security-sensitive reports.

*Fill in:* the disclosure procedure (security inbox, PGP key,
organisation-wide policy).

## Dependency scanning

*Fill in:* the CI workflow or scheduled job that scans dependencies,
where it lives in this repo, what triggers it, and which branches it
runs against. If scanning is delegated to an organisation-wide
workflow, name it.

Prefer stable libraries; verify lockfile changes are explainable before
merging.

## Secrets

Secrets are never committed to this repo.

*Fill in:* where configuration is loaded from, what file patterns are
gitignored, how local developers supply credentials, and how deployed
environments inject secrets (platform secret store, mounted files,
environment injection).

If a secret is committed by accident, **rotate it immediately** — git
history retention means deletion alone is not enough.

## Authentication and authorisation

**TBD.** Auth is not yet wired into this service. When it is, this
section expands to document the provider, token format, public vs.
protected routes, and how identity propagates to downstream calls.

Until then, assume routes are effectively public in non-production
environments. Do not ship to production without filling this section.

## Threat model (sketch)

Primary risks at the current stage:

- **Injection of untrusted input into downstream calls.** Mitigation:
  parse request bodies into typed structs / validated DTOs at the
  handler boundary; never pass raw input to downstream queries.
- **Unauthenticated access in deployed environments.** Mitigation:
  *fill in the gateway, proxy, or platform-level control that enforces
  auth before requests reach this service.*
- **Dependency compromise.** Mitigation: the dependency-scanning
  workflow above.

Expand this section as the service matures.
