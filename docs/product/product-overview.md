# Product Overview

## What the Platform Is

A predictive maintenance platform that turns everyday equipment sensor data into early warnings — so a maintenance team finds out that a machine is likely to fail *before* it happens, not after it's already down.

Instead of reacting to breakdowns or servicing equipment on a fixed calendar regardless of its actual condition, the platform continuously scores each machine's failure risk, explains *why* it's at risk in plain terms, and automatically alerts the right person the moment something crosses into dangerous territory.

## Target Customers

Small-to-mid-size manufacturers — roughly 50 to 500 employees — running mechanical or rotating equipment: CNC machines, industrial pumps, turbines, air compressors, conveyor systems.

The ideal customer today has no predictive maintenance tooling in place — they're running on spreadsheets, tribal knowledge, a legacy system that only logs what already happened, or pure reactive repair. The person evaluating the platform is typically a Plant Manager, Maintenance Manager, Reliability Engineer, or VP of Operations — someone who feels the cost of unplanned downtime directly and can approve a small pilot without a lengthy procurement process.

## Problems Solved

- **Unplanned downtime is expensive.** A machine failing mid-shift means stopped production, missed orders, and emergency repair costs that dwarf what preventive maintenance would have cost.
- **Maintenance today is reactive or blind.** Teams either find out about a problem after it's already broken, or service equipment on a fixed calendar regardless of whether it actually needs it — wasting time on healthy machines while a genuinely at-risk one goes unnoticed.
- **Existing tools describe the past, not the future.** Logbooks and legacy systems record what happened; they don't tell you what's about to happen.
- **No fleet-wide visibility.** Without a single view across every machine, priorities get set by whichever problem is loudest today, not by which one is actually the biggest risk.

## Core Capabilities

- **Fleet health at a glance** — every machine's condition and risk level in one view, so priorities are set by data, not by whoever's complaining loudest.
- **Early failure warnings** — machine-learning risk scoring flags a likely failure while there's still time to act, not after the fact.
- **Explainable risk, not a black box** — every risk score comes with the specific conditions driving it (temperature, torque, tool wear, and more), so a technician knows exactly what to check.
- **Automatic alerts** — when a machine crosses into critical risk, an alert is created and an email goes out immediately. No one has to be staring at a screen to find out.
- **Guided maintenance workflow** — alerts turn directly into trackable work orders, from open through in-progress to complete, so nothing falls through the cracks.
- **Fast historical data import** — upload existing sensor history from a spreadsheet export instead of typing it in by hand, so getting started takes minutes, not weeks.
- **Cost and ROI visibility** — downtime cost estimates and maintenance ROI are visible to a manager or executive, not buried in engineering.
- **Guided onboarding** — add a machine, upload its history, see a live health score, all in one sitting — designed to be run live with a new customer, no technical setup required on their side.

## Product Workflow

1. **Add equipment** — name, location, manufacturer for each asset.
2. **Upload historical sensor data** — a CSV export of past readings, or start feeding in new readings going forward.
3. **Risk is scored continuously** as data comes in.
4. **A critical risk automatically fires an alert and an email**, in seconds — no manual monitoring required.
5. **Maintenance staff review the alert**, see the specific factors behind it, and create or track a work order straight from that alert.
6. **Leadership checks the executive view** for a fleet-wide picture of risk, cost exposure, and maintenance activity.

## Business Value

- **Catch problems in the warning window**, not after failure — avoiding the cost of unplanned downtime rather than reacting to it.
- **Shift maintenance spend from reactive and calendar-based to condition-based** — fewer wasted inspections on healthy equipment, fewer emergency repairs on equipment that was quietly failing.
- **One place for leadership to see risk and cost exposure** across the whole fleet, replacing scattered spreadsheets and whoever-remembers-best institutional knowledge.
- **No IT project required to start** — runs in a browser, historical data comes in via a spreadsheet upload, and no sensor hardware integration is needed to begin evaluating it.

## Example Use Case

A mid-size manufacturer running a mix of CNC machines, pumps, and conveyor systems onboards their five most critical assets in a single sitting, uploading 90 days of historical sensor readings for each. The platform immediately flags one industrial turbine as **critical risk** — a 94% failure probability — driven by rising torque and a declining rotational speed trend. An alert fires and an email reaches the maintenance manager within seconds. The dashboard shows exactly which readings are driving the score, so the technician knows what to inspect before a crew is even dispatched. A work order is created directly from the alert and tracked through to completion. Leadership reviews the fleet-wide risk picture and estimated downtime cost avoided from the executive view.

## Current MVP Scope

What's real and working today:

- A single-customer deployment — one company's login, not yet a self-serve product for many companies at once
- Historical data comes in via spreadsheet upload — not yet a live, real-time sensor/IoT connection
- Risk scoring is built on five core sensor readings per machine (two temperature readings, rotational speed, torque, and tool wear) — the common set exported by rotating-equipment sensors
- The fleet dashboard, alerting, maintenance workflow, and executive view are all fully functional
- Critical-risk email alerting is live
- A guided onboarding flow walks through adding a new customer's first machines and data in one sitting

## Future Vision

- Real-time sensor integration — direct historian, OPC-UA, or IoT connections in place of spreadsheet upload
- Multi-tenant, self-serve signup so many customer companies can onboard independently
- A technician-facing mobile app and maintenance scheduling
- Equipment-specific and industry-specific risk models beyond the current general rotating-equipment model
- Additional alert channels — SMS, Slack, or Teams — alongside email
- Deeper integration with customers' existing CMMS systems rather than a standalone workflow
