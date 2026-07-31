# Documentation

An index of everything under `docs/`. Each file is written for a specific reader — pick the one that matches who you are right now.

| File | Read this if you're... | What's in it |
|---|---|---|
| [`product/product-overview.md`](product/product-overview.md) | A prospect, or explaining the product to one | What the platform is, who it's for, the problems it solves, and current MVP scope — written in business terms, no engineering jargon |
| [`sales-support/demo-overview.md`](sales-support/demo-overview.md) | About to get on a call with a prospect | A step-by-step demo script, key talking points, anticipated questions (with honest answers, including "pricing isn't finalized"), and limitations to know before you're asked live |
| [`roadmap/roadmap.md`](roadmap/roadmap.md) | Deciding what to work on next | Completed / Current Focus / Near-Term / Long-Term — ordered by "does this help get or run a pilot," not by engineering ambition |
| [`architecture/system-architecture.md`](architecture/system-architecture.md) | Working in or reviewing the codebase | System, backend, and dashboard architecture, database schema, API structure, auth flow, and deployment topology — with diagrams |
| [`engineering-log/`](engineering-log/) | Auditing what actually shipped and when | Dated engineering logs — the [Pilot Sprint completion log](engineering-log/2026-07-31-pilot-sprint-complete.md) covers everything through v1.0, and [Security Hardening & Operations](engineering-log/2026-07-31-security-hardening-and-operations.md) covers the tenant-isolation fix, auth hardening, and ops visibility work that followed it the same day |
| [`releases/v1.0-pilot-release.md`](releases/v1.0-pilot-release.md) | Checking what changed in a specific release | Formal release notes for v1.0 — new features, infra/database/security changes, known limitations, upgrade notes |

## Current state, in one line

The platform is deployed, authenticated, has real per-account data isolation (safe to onboard a second customer without their data leaking into a first customer's view), and can take in a new customer's historical data, alert on critical risk by email, and walk a new machine through onboarding. The current bottleneck is customer discovery, not engineering — see the roadmap's **Current Focus** section.

## Note on the engineering log and release notes

The Pilot Sprint log and the v1.0 release notes both describe a since-fixed authentication gap on the per-machine health/trend endpoints as an open issue (it was, when they were written) — fixed and verified live the same day (commit `fe7882d`). That same log's JWT-insecure-fallback issue is also since fixed (commit `00cab2d`). Both superseded by [Security Hardening & Operations](engineering-log/2026-07-31-security-hardening-and-operations.md), which also covers a more significant finding from later that day: the platform had zero tenant/account data isolation at all, since fixed. The older docs are left as-is — dated records of the state at time of writing, not living documents.
