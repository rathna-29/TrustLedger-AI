# Bug Tracker - TrustLedger-AI

Every known or fixed bug, its observable effect, and how to reproduce or see it.
Severity: CRIT = causes wrong money-moving decision or undetectable ledger
tampering; HIGH = breaks a core invariant (determinism, transparency);
MED = degrades UX/observability; LOW = cosmetic.

| ID | Severity | Module / File | Symptom (what you SEE) | Trigger / how to observe |
|----|----------|--------------|------------------------|--------------------------|
| BUG-01 | CRIT | m13-ledger (old `verify_chain`) | Ing `verify_chain` only recomputed the final entry hash; editing ANY middle row still passed audit. A malicious operator could rewrite an approved amount in the middle of the chain without any alert. | Edit a row that is not the tail of `audit_log`, run chain verification, see PASS. |
| BUG-02 | CRIT | `database/schema.sql` audit_log | No `prev_hash`/linkage column in the original schema; the ledger was a flat list, not a chain, so tamper detection had no anchor to recompute against. | Schema dump shows no hash-link column. |
| BUG-03 | HIGH | pipeline early-reject path | When identity failed, the pipeline returned a decision **without** running the manipulation / policy / limits stages, so "BLOCKED because unknown agent" produced an incomplete 15-stage trace; auditing a rejection showed a hole. | Submit intent with an unknown/forgery Bearer token, inspect the trace. |
| BUG-04 | HIGH | `m14_baseline_update` | Baseline (behaviour mean/std) was updated on **every** processed intent, including blocked and escalated ones, so repeated blocked attempts caused the risk model itself to drift and made repeat runs non-deterministic. | Run the same blocked scenario twice: risk_score/hash differ. |
| BUG-05 | HIGH | `m09_risk_engine` | `risk_score` used `random.uniform` so identical input could yield different scores run-to-run; a demo could flip EXECUTE->BLOCK on refresh. | Run same payload twice, compare risk_score. |
| BUG-06 | MED | `modules/a15_monitoring` (monitor queue) | Decision labels in stage trace used inconsistent keys across stages (e.g. some used `label`, others `stage`), so the dashboard failed to render the 15-stage board correctly. | Inspect `pipeline_stages` key shapes stage to stage. |
| BUG-07 | MED | dashboard routes + templates | `/dashboard` route (and `/api/overview`) worked only when run as monolithic `app.py`; after switching to a factory, Flask looked for templates under `application/templates/`, returning 500 `TemplateNotFound: dashboard.html`. | Boot via `create_app()` and GET `/dashboard`. |
| BUG-08 | LOW | startup | `app.py` refused to boot (and CI seeding looped) unless `app.db` already existed, with misleading "run seed" message that could not be acted on interactively. | Clone fresh, run `python app.py` without DB. |

Closed: BUG-01..BUG-08 fixed - see [FIXES.md](FIXES.md).
