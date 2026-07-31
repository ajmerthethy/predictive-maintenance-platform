# Engineering Log — Security Hardening, Tenant Isolation & Operations

**Date:** 2026-07-31 (same day as, but a later and separate work session from, [Pilot Sprint Complete](2026-07-31-pilot-sprint-complete.md))
**Branch:** `main` (reconciled with `production-refactor` during this session — see below)

---

## Executive Summary

Where the Pilot Sprint log left off ("no pilot customer, but the platform can safely demo to one"), this session asked a harder question: *can it safely take on a **second** one without the first customer's data leaking?* The answer was no — a full audit found **zero tenant isolation anywhere in the API**, a finding serious enough to fix immediately rather than defer. That, plus a live authentication gap, an insecure JWT fallback, and an under-configured email sender, made this a security-and-operations session rather than a feature session — consistent with the standing principle that engineering time right now should go to things that would cause real damage if ignored, not to new capability nobody has asked for yet.

Nothing here changes the standing business bottleneck: there is still no pilot customer lined up. This work exists so that when one appears, onboarding them (and a second, and a third) doesn't create a data breach between customers.

---

## What Changed, By Category

### Security fixes

- **`health.router` auth gap** (`fe7882d`, tests `4d94e9d`) — `GET /machines/{id}/health` and `/trend` were reachable with no login in production, exempted by mistake alongside the genuinely-public liveness check. Fixed, verified live (401 without a token, 200 with one), regression-tested.
- **Insecure JWT secret fallback removed** (`00cab2d`) — `JWT_SECRET_KEY` previously fell back to a hardcoded, publicly-visible default if unset. Now the app refuses to boot (loud `RuntimeError` at startup, not a silent forgeable-token vulnerability) unless a real secret ≥32 characters is configured. `.env.example` added (didn't exist before), CI updated with a throwaway secret, README updated.
- **Tenant/account data isolation** (`5f1ea40`) — the significant one. Audited every data-bearing endpoint (33 total) and found 29 of them returned or accepted data with zero scoping to who was logged in — any valid token could read or modify any other customer's machines, alerts, sensor data, or maintenance history by ID. Root cause: `Machine` (and everything hanging off it) had no owner column at all, and `get_current_user` was only ever used as a blanket auth gate, never to filter a query. Fixed with a real `Account` model, `account_id` on `users` and `machines`, and every router scoped to `current_user.account_id` — 404, not 403, on an ownership failure so a caller can't tell "doesn't exist" from "exists but isn't yours." Migration backfills all existing data into one "Default Account," so this shipped with zero behavior change for the current single customer. Verified live: existing access unchanged, and a genuine two-account cross-isolation test now passes for real (it started this work as an `xfail` documenting the gap).

### Configuration & operations

- **Resend email sender hardened** (`2853c73`) — sender address was already env-configurable (not hardcoded), just under an inconsistent name; renamed `EMAIL_FROM_ADDRESS` → `RESEND_FROM_EMAIL`. Added a loud (non-fatal) log, both at startup and at send-time, if email alerting is enabled while still on Resend's sandbox sender — previously this misconfiguration was invisible until an alert silently failed to reach anyone but the account owner.
- **Operational visibility audited, one gap closed** (`7daab44`) — API 5xx logging and alert-send-failure logging were both already adequate (verified live by forcing a real unhandled exception and a real Resend failure through the running app, not just by reading the code). Added `GET /health/db`: a genuine database-connectivity check, unauthenticated, distinct from the pure-liveness `/health` (kept dependency-free on purpose, so a container restart policy is never tied to DB reachability) and from the auth-gated per-machine `/machines/{id}/health`. Recommended (not implemented, per instruction) pointing an external uptime monitor — UptimeRobot's free tier — at `/health/db`.

### Repo hygiene & branch consolidation

- **Removed tracked placeholder-credential files and pycache** (`bfbc613`) — `.env.local_backup` and `backend/app/core/.env.local` (both contained only local dev placeholder values, confirmed via direct read and a full-history pickaxe search — no real secret has ever been committed to this repo), plus 67 tracked `__pycache__`/`.pyc` files. `.gitignore` tightened (`.env.*` with an explicit `!.env.example` exception, `.ruff_cache/`).
- **`main` and `production-refactor` reconciled** (`4ad6139`) — audited the full commit history in both directions: `production-refactor` had 23 commits `main` lacked, `main` had zero commits `production-refactor` lacked. Clean fast-forward, no merge/rebase decision needed, and a file-by-file check of every deletion confirmed none were unintentional regressions (all traced to an already-documented dead-code-removal commit). `main` fast-forwarded to match, both pushed, and the README now documents `main` as the single source of truth going forward. **Railway is still configured to deploy from `production-refactor`** — repointing it is a manual dashboard step the user has said they'll do later; both branches are being kept in sync with every push until then.

### Test coverage

Added 54 tests total across four files (`test_auth.py`, `test_alert_delivery.py`, `test_calculations.py`, plus 3 more in `test_health.py`), targeted at three areas by explicit priority: auth (token issuance, expiry, invalid/malformed/wrong-signature/unknown-subject tokens), alert delivery (threshold-boundary logic, and confirming a Resend failure is logged, never silently swallowed or allowed to break the request that triggered it), and ROI/downtime-cost calculations (hand-computed expected outputs plus edge cases). Two latent — not live — bugs were found and documented rather than fixed, since this was a coverage task: `calculate_downtime_cost` doesn't validate its `health_score` input, and `calculate_maintenance_roi`'s `potential_downtime_loss` isn't floored at zero the way `estimated_savings` is. Neither is reachable via the current router call chain.

---

## Current System Status

| Component | Status |
|---|---|
| Backend API | 🟢 Live, `main` and `production-refactor` in sync |
| Dashboard | 🟢 Live, unaffected by this session's changes |
| Database | 🟢 Supabase Postgres — now has real account-based tenant isolation |
| Auth | 🟢 Hardened: no insecure fallback, per-account data scoping enforced |
| Email alerting | 🟡 Working, loudly flags its own sandbox-sender limitation now |
| Operational visibility | 🟢 DB-connectivity health check live; error logging confirmed adequate |
| Test suite | 🟢 86 passing (was 32 at the start of this session) |
| Branch hygiene | 🟢 `main` and `production-refactor` reconciled, `main` documented as source of truth |
| Pilot customer | 🔴 Still none secured |

---

## Known Issues Superseded From the Prior Log

The [Pilot Sprint Complete](2026-07-31-pilot-sprint-complete.md) log's Known Issues #1 (health.router auth gap) and #2 (JWT insecure fallback) are both now fixed — see above. That log is left as-is per this repo's own documented policy (dated record, not a living document); this entry is the update.

## Known Issues / Technical Debt (current, as of this log)

1. Resend is still on its sandbox sender — domain verification is a manual step in the Resend dashboard the user has deferred intentionally, not forgotten.
2. Railway still deploys from `production-refactor`, not `main` — manual repointing deferred intentionally by the user.
3. No external uptime monitor configured yet — recommended (UptimeRobot → `/health/db`), awaiting a decision.
4. Two latent input-validation gaps in the ROI/downtime-cost calculation functions (see Test Coverage above) — not reachable today, worth a look if those functions are ever called with unvalidated input.
5. Router-level test coverage for `/downtime`, `/roi`, and `/health-score` is still thin — only the pure calculation functions underneath them are tested, not the HTTP layer (auth, tenancy, 404 handling).
6. No self-serve account-management UI — provisioning a new customer account is CLI-only (`create_user.py <account_name> ...`), matching the existing single-tier auth model. Fine at pilot scale, would need real work before self-serve signup.
7. Longer-standing, unchanged since the Pilot Sprint log: no rate limiting on login, no automated dashboard test suite, `datetime.utcnow()` deprecation warnings scattered across several files.

## Immediate Next Priorities

1. **Customer discovery is still the top priority.** Nothing in this session should be read as a pivot back to engineering — this work was defensive (preventing a real breach), not additive (new capability). The founder transition plan from earlier remains the active guidance.
2. When a second real pilot conversation gets close to an actual pilot, close out items 1–3 above (Resend domain, Railway repoint, uptime monitor) — all cheap, all currently fine to leave as-is with zero customers depending on them.
3. No further engineering is recommended right now beyond what a specific, real prospect asks for.
