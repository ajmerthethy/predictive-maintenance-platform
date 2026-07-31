# Demo Overview

**Purpose:** what to say and show on a call with a prospect. Read this before the call, keep the demo script open during it.

---

## Product Summary

A predictive maintenance platform that turns equipment sensor data into early warnings — so a maintenance team finds out a machine is likely to fail *before* it happens, not after. It scores failure risk continuously, explains *why* a machine is at risk in plain terms, automatically alerts the right person when risk turns critical, and turns that alert into a trackable work order.

Built for small-to-mid-size manufacturers (roughly 50–500 employees) running rotating or mechanical equipment — CNC machines, pumps, turbines, compressors, conveyors — who don't have predictive maintenance today.

---

## Demo Script

The seeded demo environment has five machines with deliberately different risk profiles, so the story tells itself without needing to explain away an empty dashboard.

**1. Open on Fleet Overview.**
"This is what you'd see logging in on a Monday morning — every machine's risk level in one view." Point out the healthy/warning/critical breakdown and the highest-priority asset called out at the top. This is the answer to "what should I worry about today," not something a plant manager has to piece together from five different spreadsheets.

**2. Click into the machine currently flagged Critical** (the seeded turbine).
Walk through, in order:
- The failure probability and risk level
- The sensor history chart — "this is 90 days of real sensor readings, and you can see the trend building"
- The explanation section — "it's not a black box; here are the specific readings driving this score" (this is usually the moment that lands with a maintenance-minded person, more than the risk number itself)
- The downtime cost estimate and maintenance ROI — this is the number a plant manager or VP can take to their own leadership

**3. Go to Alerts.**
Show the active alert tied to that machine. Acknowledge it, then create a maintenance task directly from it. "The alert isn't just a notification — it turns into a tracked work order in one click."

**4. Go to Maintenance.**
Show the work order from step 3 sitting in Open status. Walk it through Start → Complete. "This is the same lifecycle your team already uses, just tied back to what triggered it."

**5. Go to Executive Dashboard.**
"This is the view for whoever isn't in the weeds day to day — fleet-wide risk and cost exposure, not sensor charts."

**6. If they're evaluating onboarding their own equipment, show Onboarding.**
Add a throwaway machine live, upload a small CSV of sample readings, and watch a health score appear within the same session. "This is genuinely how fast it is to bring your own equipment in — there's no IT project here."

**7. Mention the email alert, even if not demoing it live.**
"When that alert was created, an email went out automatically to whoever needs to know — nobody has to be staring at this screen for it to work." (See **Current Limitations** — don't promise this reaches the prospect's own inbox live on the call unless email delivery has been separately configured for them.)

---

## Key Talking Points

- **"You find out before it breaks, not after."** The entire pitch is the gap between a warning and a failure — lead with that, not with the technology.
- **"It's not a black box."** Every risk score comes with the specific factors driving it. This matters more to a maintenance audience than the model itself does.
- **"No IT project to get started."** Historical data comes in as a spreadsheet upload; there's no sensor integration required to begin evaluating it.
- **"One alert, one work order, one place to track it."** The workflow from detection to resolution lives in one system, not a notification in one tool and a work order in another.
- **"This is a live system, not a mockup."** Everything shown is running against a real deployed backend and a real database — worth saying explicitly, since a lot of what prospects see from startups at this stage is a slide deck.

---

## Typical Customer Questions

**"Do you integrate with our existing sensors/PLC/historian?"**
Not yet, directly. Today, historical data comes in via CSV upload — if you can export sensor readings to a spreadsheet, you can get them in. Direct/live integration is on the roadmap but not built.

**"Is anyone else in our industry using this?"**
Be straightforward: this is a pilot-stage product without a live paying customer yet. Frame it as an opportunity to shape the product as an early partner, not a weakness to talk around.

**"What does it cost?"**
Pricing isn't finalized yet — this is genuinely still to be worked out, especially for an early pilot. Don't invent a number on the call; take it as a follow-up.

**"What sensors/data do you need?"**
Five readings per machine: two temperature readings, rotational speed, torque, and tool wear — the common set exported by rotating equipment sensors. If their export doesn't line up exactly, say so honestly and follow up rather than promising compatibility on the spot.

**"How long does it take to get set up?"**
Onboarding a machine and its historical data takes minutes once you have a CSV export — that's the whole point of the guided onboarding flow. Getting from "interested" to "live pilot," including their own data, is realistically a matter of days, not weeks.

**"Is our data secure?"**
The platform is login-gated — nothing is visible without authentication. (Don't over-promise here beyond that; this is a single-tenant pilot deployment, not an audited enterprise security posture yet.)

**"Can it do [specific thing]?"**
The honest answer during a sales conversation, same as during discovery: *"tell me more about why you need that"* — not a same-call yes. Write it down, follow up.

---

## Current MVP Capabilities

What's real and demoable today:

- Fleet-wide risk dashboard across multiple machines
- ML-driven failure probability scoring with explainable, factor-level detail
- Automatic email alerting when risk crosses into critical
- Alert → work order workflow (create, start, complete)
- Downtime cost and maintenance ROI estimates
- CSV bulk upload of historical sensor data, with a downloadable template
- Guided onboarding flow for a new machine and its historical data
- Executive-level fleet summary view

---

## Current Limitations

Know these before the call so nothing catches you off guard live:

- **Single customer per deployment** — this is not yet a self-serve, multi-company product. A new customer today means a new login provisioned by hand.
- **No live sensor integration** — CSV upload only; no real-time IoT or historian connection yet.
- **Email alerts currently can only deliver to one configured inbox** (not yet set up to reach an arbitrary prospect's own email without additional setup on the email provider side) — don't promise live email delivery to *their* inbox on a first call unless this has been arranged beforehand.
- **No pricing model finalized** — don't quote a number.
- **No existing customer reference or case study** — this is a first-pilot conversation, not a proof point from someone else.
- **Single-tier access** — no role-based permissions or per-user restrictions within an account yet.
