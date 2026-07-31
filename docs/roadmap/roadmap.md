# Roadmap

**Last updated:** 2026-07-31

**Governing principle:** every item below is ordered by one question — *does this help get or run a real pilot customer?* Engineering effort is deliberately capped right now in favor of customer discovery. Nothing here should be read as a backlog to work through regardless of what real prospects say; near-term and long-term items are directional, not commitments, and are expected to shift once real conversations happen.

---

## Completed

**Architecture refactor** (pre-Pilot-Sprint)
CI pipeline, isolated test infrastructure, dead-code removal, Alembic migration repair, N+1 query fixes, API pagination, dashboard converted to a native multipage app, risk classification unified across the codebase.

**Pilot Sprint** — 10/10 issues closed and verified
- Public deployment to Railway (backend + dashboard, both live)
- Single-customer authentication (login-gated dashboard and API)
- Production database seeded with realistic demo data
- CSV bulk upload for historical sensor data, with a downloadable template
- Automatic email alerting on critical-risk alerts
- Guided onboarding flow (add machine → upload data → summary)
- Demo-quality polish (empty states, hidden debug output, consistent branding)

The platform is live, reachable, and demo-able today. This is not a prototype anymore — it's a working system a real company could evaluate.

---

## Current Focus

**Customer discovery. Not engineering.**

The platform can already do everything a first pilot needs. The unresolved risk isn't the product — it's that no manufacturing company has yet confirmed the pain is real enough to pay for. The current priority is getting the first 20 real conversations with plant managers, maintenance managers, and reliability engineers at small-to-mid-size manufacturers running rotating equipment, to confirm or deny that directly.

While this is underway:
- No new features are being added, regardless of how obvious an idea seems mid-conversation.
- Engineering time is capped to emergency/breakage response only.
- The one exception is a live security gap (see **Near-Term**) that should be closed regardless of sales activity, since it's a data-exposure issue, not a feature.

---

## Near-Term

Ordered by what's actually pending, not by ambition. Most of this section is conditional on real signal from customer conversations — it should not be executed as a checklist independent of what prospects actually say.

**Should happen regardless of sales progress:**
- Close the known authentication gap on the per-machine health/trend endpoints (currently reachable without a login in production) — a contained bug fix, not new scope.
- Add a startup-time guard so the insecure JWT secret fallback can never silently apply outside local development.
- Reconcile the `main` and `production-refactor` branches so the repository's default branch reflects what's actually deployed.

**Conditional on an actual committed pilot prospect:**
- Verify a sending domain with the email provider so alert emails can reach a real customer's inbox (currently limited to the account owner's own address).
- Provision that customer's login and walk them through the existing onboarding flow live.
- Only *after* a specific pilot customer asks for something the platform can't yet do — evaluate building it, scoped exactly to what they asked for, not a generalized version of it.

**Explicitly not in scope here unless a real prospect asks for it directly:** anything from the Long-Term list below.

---

## Long-Term

Deferred until there is real pilot or paying-customer signal that justifies the investment — not because these are bad ideas, but because building them now would be optimizing for a customer that doesn't exist yet.

- Multi-tenant, self-serve signup for multiple customer companies at once
- Real-time sensor integration (IoT, OPC-UA, or direct historian connections) in place of CSV upload
- Automated regression tests for the authentication flow and a committed dashboard test suite
- Rate limiting and brute-force protection on login
- External uptime/error monitoring on the deployed services
- Additional alert channels (SMS, Slack, Teams) beyond email
- A technician-facing mobile app and maintenance scheduling
- Equipment-specific or industry-specific risk models beyond the current general rotating-equipment model
- Deeper integration with customers' existing CMMS systems
- Billing, SSO, RBAC, and other enterprise-scale concerns — explicitly out of scope until there's product-market fit to protect
