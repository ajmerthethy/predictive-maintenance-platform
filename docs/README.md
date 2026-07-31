# Documentation

An index of everything under `docs/`. Each file is written for a specific reader — pick the one that matches who you are right now.

| File | Read this if you're... | What's in it |
|---|---|---|
| [`product/product-overview.md`](product/product-overview.md) | A prospect, or explaining the product to one | What the platform is, who it's for, the problems it solves, and current MVP scope — written in business terms, no engineering jargon |
| [`sales-support/demo-overview.md`](sales-support/demo-overview.md) | About to get on a call with a prospect | A step-by-step demo script, key talking points, anticipated questions (with honest answers, including "pricing isn't finalized"), and limitations to know before you're asked live |
| [`roadmap/roadmap.md`](roadmap/roadmap.md) | Deciding what to work on next | Completed / Current Focus / Near-Term / Long-Term — ordered by "does this help get or run a pilot," not by engineering ambition |
| [`architecture/system-architecture.md`](architecture/system-architecture.md) | Working in or reviewing the codebase | System, backend, and dashboard architecture, database schema, API structure, auth flow, and deployment topology — with diagrams |
| [`engineering-log/`](engineering-log/) | Auditing what actually shipped and when | Dated engineering logs — the [Pilot Sprint completion log](engineering-log/2026-07-31-pilot-sprint-complete.md) covers everything through v1.0, including known issues and technical debt found during the audit |
| [`releases/v1.0-pilot-release.md`](releases/v1.0-pilot-release.md) | Checking what changed in a specific release | Formal release notes for v1.0 — new features, infra/database/security changes, known limitations, upgrade notes |

## Current state, in one line

The Pilot Sprint is complete — the platform is deployed, authenticated, seeded with demo data, and can take in a new customer's historical data, alert on critical risk by email, and walk a new machine through onboarding. The current bottleneck is customer discovery, not engineering — see the roadmap's **Current Focus** section.

## Note on the engineering log and release notes

Both documents describe a since-fixed authentication gap on the per-machine health/trend endpoints as an open issue (it was, when they were written). It was fixed and verified live in production the same day — see commit `fe7882d`. The docs are left as-is since they're dated records of the state at time of writing, not living documents.
