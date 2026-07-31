# Engineering Log — Pilot Sprint Complete

**Date:** 2026-07-31
**Branch:** `production-refactor`
**Milestone:** [Pilot Sprint](https://github.com/ajmerthethy/predictive-maintenance-platform/milestone/1) — 10/10 issues closed

---

## Executive Summary

The Pilot Sprint (GitHub issues #2–#11) is complete. Starting from a refactored but undeployed codebase, the platform now has a public deployment, single-customer authentication, a seeded demo dataset, CSV-based historical data import, email alerting on critical failures, and a guided onboarding flow — the minimum set of capabilities for a manufacturing company to evaluate the product without anyone touching the API or database directly.

Every issue was closed only after end-to-end verification: against a disposable Postgres instance locally, and — for anything with a production surface (auth, CSV upload, email alerting) — against the live Railway deployment itself, not just local/CI. That process surfaced and fixed several real bugs along the way (a passlib/bcrypt incompatibility, a numpy/psycopg2 type error, two pandas parsing bugs, a Railway build-context misconfiguration) and, during the audit for this log, one live security gap that is still open (see **Known Issues #1**).

The business bottleneck at this point is not engineering. There is no pilot customer lined up yet; the immediate priority is customer discovery, not further feature work.

---

## Current System Status

| Component | Status |
|---|---|
| Backend API | 🟢 Live — `https://predictive-maintenance-platform-production.up.railway.app` |
| Dashboard | 🟢 Live — `https://predictive-maintenance-platform-production-523c.up.railway.app` |
| Database | 🟢 Supabase Postgres, seeded with demo data |
| Auth | 🟢 Single pilot user provisioned (`ajmerthethy`) |
| Email alerting | 🟢 Verified delivering (Resend sandbox sender) |
| CI | 🟢 Lint + test passing on push to `main` / `production-refactor` |
| Pilot customer | 🔴 None secured yet |

---

## Technologies Used

**Backend**
- Python 3.12, FastAPI 0.139.2, Uvicorn
- SQLAlchemy 2.0.51 (ORM), Alembic 1.18.5 (migrations), psycopg2-binary
- PyJWT 2.13.0, passlib[bcrypt] 1.7.4 + bcrypt 4.0.1 (pinned down from 5.0.0 — bcrypt ≥4.1 removed an attribute passlib 1.7.4 depends on)
- pandas, python-multipart (CSV bulk upload)
- `requests` (outbound HTTP to Resend)

**Machine Learning**
- scikit-learn 1.9.0 — `RandomForestClassifier` trained on the AI4I 2020 Predictive Maintenance dataset
- SHAP 0.52.0 (`TreeExplainer`) for per-prediction feature-importance explanations
- Model artifacts (`failure_model.pkl`, `feature_importance.pkl`) loaded once at process start via `joblib`

**Dashboard**
- Streamlit 1.60.0 (native multipage `pages/` convention)
- Plotly 6.9.0, pandas 3.0.5, reportlab (PDF report generation), matplotlib

**Database**
- PostgreSQL, hosted on Supabase (pooler connection) in production; disposable Docker Postgres for local dev/CI

**Infrastructure**
- Docker + Docker Compose (local dev)
- Railway (production hosting — two independent services from the same repo/branch)
- GitHub Actions CI (`.github/workflows/ci.yml`) — ruff lint + pytest against a disposable Postgres service container

**Testing/Tooling**
- pytest 9.1.1, httpx 0.28.1, ruff 0.16.0 (scoped to pyflakes + syntax errors only, per `ruff.toml`)

---

## Architecture Overview

Monorepo, three top-level concerns:

```
predictive-maintenance-platform/
├── backend/app/
│   ├── routers/       17 FastAPI routers
│   ├── services/      business logic (risk, health score, alerting, notifications, ROI, downtime)
│   ├── models/         SQLAlchemy ORM (6 tables)
│   ├── schemas/        Pydantic request/response models
│   ├── ml/              prediction pipeline (RandomForest + SHAP)
│   └── core/            config, security (JWT/bcrypt), logging
├── dashboard/
│   ├── streamlit_app.py + pages/   7-page native multipage app
│   └── lib/                          api_client, auth, business_rules, report, upload_widget
├── alembic/            migrations — lives at repo root, not under backend/
├── tests/               pytest suite — also at repo root
└── scripts/             seed_database.py, create_user.py
```

**Request flow:** Streamlit page → `lib/api_client.py` (attaches bearer token from `st.session_state`) → FastAPI router (behind `get_current_user` dependency) → service layer → SQLAlchemy → Postgres. Predictions additionally load the RandomForest model in-process and return SHAP-based feature importance alongside the probability.

**Deployment topology:** two independent Railway services built from the same GitHub repo and branch, each with a distinct Dockerfile path but a shared repo-root build context (both Dockerfiles were rewritten this sprint to be repo-root-context-aware — see commit `9d519f0`).

---

## Backend Features

17 routers, grouped by capability:

- **Machines** — create, list
- **Sensor Readings** — single create (auto-runs prediction), per-machine list, **bulk CSV upload + downloadable template** (new, #6)
- **Predictions** — create, latest-by-machine, history, feature-importance explanation
- **Alerts** — list, acknowledge, resolve, history
- **Maintenance** — create/start/complete work orders, plus Maintenance Summary, Maintenance Intelligence, and Maintenance ROI
- **Analytics** — summary stats, risk ranking
- **Health Monitoring** — per-machine health status + sensor trend (⚠ see Known Issues #1)
- **Health Score** — 0–100 asset health score with a business-friendly rating (Excellent/Good/Monitor/At Risk/Critical)
- **Downtime** — cost estimate per machine
- **Executive** — executive summary
- **Fleet Risk** — fleet-wide risk summary
- **History** — machine history
- **Recommendations** — maintenance recommendation
- **Auth** — login (JWT issuance), test endpoint
- **Notifications** — Resend email dispatch on every newly-created CRITICAL alert (new, #7)

---

## Dashboard Features

7 pages (Streamlit native multipage, alphanumeric prefix controls sidebar order):

- **`0_Onboarding.py`** (new, #8) — guided add-machine → upload-CSV → summary flow; the only place a machine can be created from the UI at all
- **`streamlit_app.py`** — Fleet Overview: risk ranking, maintenance intelligence, fleet status breakdown, analytics summary
- **`1_Machine_Detail.py`** — machine selector, sensor history charts, live prediction, health score, downtime/ROI, maintenance history, AI explanation (debug JSON hidden behind `SHOW_DEBUG_INFO`, off by default — #10)
- **`2_Executive_Dashboard.py`** — executive summary + fleet risk
- **`3_Alerts.py`** — active alerts, acknowledge/resolve, alert history, create a maintenance task directly from an alert
- **`4_Maintenance.py`** — work order list, start/complete actions
- **`5_Upload_Data.py`** (new, #6) — standalone CSV bulk upload (machine selector, template download, row preview, upload); shares `lib/upload_widget.py` with the onboarding page rather than duplicating the logic

All 7 pages are gated behind `lib/auth.require_login()` (#5).

---

## Database Status

- PostgreSQL via SQLAlchemy 2.0, Alembic-managed, 12 migrations
- 6 tables: `machines`, `sensor_readings`, `predictions`, `alerts`, `maintenance_tasks`, `users`
- Production (Supabase) currently seeded via `backend/scripts/seed_database.py`: 5 demo machines (healthy/aging/critical sensor profiles), ~2,160 sensor readings per machine (90 days × 24h), matching predictions, and 1 active CRITICAL alert
- Local/CI: disposable Postgres in Docker; tests run each in its own SAVEPOINT-based transaction that's rolled back after, so app-level `commit()` calls don't leak between tests

---

## Authentication

Single-customer, single-tier model (#5) — explicitly not multi-tenant, no RBAC, no self-serve signup:

- `POST /auth/login` verifies a bcrypt-hashed password (`passlib`) and issues an HS256 JWT (24h expiry, configurable)
- `get_current_user` is applied via `dependencies=` at router-registration time in `main.py`, covering every router except `auth` and `health`
- Users are provisioned only via `backend/scripts/create_user.py` (CLI) — there is no signup endpoint by design
- Dashboard: `lib/auth.require_login()` gates all 7 pages; the token lives in `st.session_state` and is attached to every backend call via `lib/api_client.py`'s internal `_get`/`_post`/`_patch` wrappers
- `JWT_SECRET_KEY` has a hardcoded insecure fallback for local dev (loudly commented) — correctly overridden in Railway today, but nothing at startup prevents the fallback from silently being used again if the env var were ever removed (see Technical Debt)

---

## Deployment Status

- **Backend:** Railway, Root Directory `.`, Dockerfile `backend/Dockerfile`, binds to Railway's dynamic `$PORT`
- **Dashboard:** Railway, Root Directory `.`, Dockerfile `dashboard/Dockerfile` (rewritten this sprint to build from repo-root context — Railway's Dockerfile Path setting has no separate build-context override on this plan)
- Both auto-deploy on every push to **`production-refactor`**, which is **not** the repository's default branch (`main` is still at the pre-refactor MVP state — see Known Issues #5)
- Database: Supabase Postgres, seeded, one live login user provisioned
- Email: Resend, sandbox sender (`onboarding@resend.dev`) — verified delivering to the Resend account owner's inbox; no custom domain verified yet

---

## Testing Status

- 17 tests across `test_alerts`, `test_analytics`, `test_health`, `test_machines`, `test_maintenance`, `test_prediction`, `test_sensor_readings` — last verified passing 2026-07-30 (no test files have changed since; today's re-verification was blocked only by Docker Desktop not running locally, not by any code change)
- Auth is bypassed in tests via a `get_current_user` dependency override in `conftest.py` — the suite exercises business logic, not the login flow itself
- `ruff check .` passes as of this log (pyflakes + syntax-error rules only — see `ruff.toml`)
- CI (`.github/workflows/ci.yml`) runs lint and the full pytest suite against a disposable Postgres service container, on push to `main`/`production-refactor` and on pull requests
- **Gaps:** no automated test coverage for the auth flow itself (login success/failure, expired/invalid tokens, per-route gating — verified manually this sprint via curl and `AppTest`, never committed as regression tests); no dashboard test suite committed to the repo (verification scripts using `streamlit.testing.v1.AppTest` were written ad hoc and deleted after each use)

---

## Completed Milestones

All ten Pilot Sprint issues, closed and verified:

| # | Issue | Verified |
|---|---|---|
| #2 | Deploy backend + dashboard to a public URL | Both services live, health-checked, auth round-trip confirmed |
| #3 | Seed realistic demo data on the deployed environment | Ran against live Supabase DB; confirmed mixed risk levels, 1 active alert, populated history |
| #4 | Fix health-rating label mismatch | Dashboard now matches the backend's actual 5-tier rating |
| #5 | Minimal single-customer authentication | Full backend + dashboard auth gate; verified 401/200 paths live in production |
| #6 | CSV upload for historical sensor data | All-or-nothing validation verified locally and against production; caught 2 real bugs in the process |
| #7 | Email alerting on critical alerts | Real Resend delivery confirmed to the user's inbox from a live production prediction |
| #8 | Basic onboarding flow | Full add-machine → upload → summary flow verified via a real multipage test session |
| #9 | Empty-state messaging | Bundled polish commit `c310868` |
| #10 | Hide developer-facing prediction JSON | Bundled polish commit `c310868` |
| #11 | Basic branding pass | Bundled polish commit `c310868` |

---

## Known Issues

1. **🔴 Security — `health.router` is reachable without authentication in production right now.** `GET /machines/{id}/health` and `GET /machines/{id}/trend` return `200` with real sensor data and no bearer token, confirmed live against production (`curl` round-trip during this audit). The exemption comment in `main.py` ("`/health` and `/auth` are the only unauthenticated routes") is broader than intended — it exempts the entire `health.router`, not just a liveness check, because that router happens to share a name with the actually-public `/health` endpoint defined separately in `main.py` itself. **This should be fixed before any real customer data is in the system.**
2. `JWT_SECRET_KEY` falls back to a hardcoded insecure default if the env var is ever unset, with no startup-time guard against that fallback being used outside local dev.
3. Email alerting uses Resend's sandbox sender with no verified domain — can only deliver to the Resend account owner's own address today, not yet usable for a real pilot customer.
4. Exactly one login user exists, provisioned via CLI — by design for this phase, but there's no path to add a second user without local/CLI access to the production database.
5. GitHub's default branch (`main`) is far behind `production-refactor` — every commit's `Closes #N` in this sprint had to be closed manually, since GitHub only auto-closes issues from commits reachable on the default branch.
6. Two tracked files look like accidental commits of local environment config: `.env.local_backup` (repo root) and `backend/app/core/.env.local`. Contents are just placeholder local dev credentials (`postgres`/`postgres`), not real secrets, but they shouldn't be version-controlled.
7. 67 compiled `__pycache__`/`.pyc` files are tracked in git despite `__pycache__/` being in `.gitignore` — committed before the ignore rule existed.

---

## Technical Debt

- No automated regression tests for the authentication flow (see Testing Status gaps)
- No committed dashboard test suite
- Minor dependency drift: backend pins `pandas==3.0.3`, dashboard pins `pandas==3.0.5`
- `datetime.utcnow()` is used across several models/routers and is deprecated upstream (SQLAlchemy/Python both warn on it) — functional today, will need a pass to timezone-aware datetimes
- A couple of Pydantic schemas (`machine.py`, `user.py`) still use v1-style `class Config` instead of `ConfigDict`, producing a deprecation warning
- No rate limiting or brute-force protection on `POST /auth/login`
- No external uptime/error monitoring on the deployed services — only in-app email alerting for ML predictions exists; if the backend itself crashed, nothing would notify anyone
- `ruff.toml` is deliberately scoped to pyflakes + syntax errors only, with no formatter or broader style enforcement — an explicit, documented deferral, not an oversight

---

## Immediate Next Priorities

1. **Fix the `health.router` auth gap (Known Issues #1)** — small, contained change, highest priority given it's a live data exposure.
2. **Customer discovery, not more engineering.** The founder's current focus is getting the first 20 industry conversations; further product work should wait for real prospect signal (see the separate founder transition plan produced this same session).
3. Verify a custom domain with Resend once a real pilot customer needs to receive alert emails at their own address.
4. Add a startup-time guard so `JWT_SECRET_KEY`'s insecure fallback can never silently apply outside local development.
5. Reconcile `main` and `production-refactor` so the repository's default branch reflects what's actually deployed.
