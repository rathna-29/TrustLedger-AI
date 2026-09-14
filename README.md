# TrustLedger-AI

**The Trust Ledger for Financial AI Agents**

A risk-aware autonomy layer that sits between a financial AI agent and the
moment it spends money. Every agent decision is scored across **15 risk stages**
(identity, behaviour drift, semantic manipulation, man-in-the-middle wallet
risk, liquidity, velocity, chain-of-commitment, chain-of-custody, ledger
integrity, baseline stability) and passed through the **Decision Governor**
(BLOCK / EXECUTE / ESCALATE) before any action is committed.

> **Disclaimer:** this is a hackathon prototype. Every transaction is
> simulated against local synthetic data. Nothing touches a real bank account,
> wallet, or blockchain.

---

## Highlights

- **15-stage decision pipeline** with auditor-grade per-stage traces
- **Decision Governor** with BLOCK / EXECUTE / ESCALATE and human-in-the-loop
  review queue
- **Tamper-evident local ledger** - chained hashes, chain-integrity
  verification, anyone-can-verify
- **ML augmentation**: behavioural anomaly scoring + semantic manipulation
  detection (scikit-learn based, deterministic by default)
- **Deterministic by default** - same scenario always yields the same verdict
  (seed fixed, RNG seeded), so demos and tests never flake
- **Write-audited decisions** - only EXECUTE / CONSTRAIN closed-loop actions
  count toward risk-model baseline updates
- **One-click scenarios** - the dashboard fires pre-built demo scenarios so you
  never need to click through 15 stages by hand

## Architecture at a glance

```
                 +--------------- dashboard / templates (Bootstrap 5)
                 |                      |
 Agent POST      |                      |
 /agent/intent --+----> routes/ ------>  modules/ (m01..m15, pipeline)
                 |                      |
                 +----> ml/  behaviour_model, manipulation_llm
                 |                      |
                 +----> security/  crypto, ledger, jwt
                 |                      |
                 +----> database/  sqlite schema + seed
```

The full write-up lives in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quick start (dev)

```bash
# 1. virtualenv + deps
python3 -m venv venv
./venv/bin/pip install -r requirements/base.txt

# 2. seed the demo database (prints agent tokens you'll use in the demo)
./venv/bin/python database/seed_data.py

# 3. run
./venv/bin/python app.py
# -> http://localhost:5000/dashboard
```

> pytest is available under `requirements/dev.txt`; CI runs tests + a boot
> smoke check on every push (see `.github/workflows/ci.yml`).

## Demo checklist (30-second run)

1. Open `http://localhost:5000/dashboard`
2. Click a **scenario chip** (e.g. "Suspicious large transfer")
3. The pipeline board animates the 15 stages live
4. A decision lands in **Review queue** or **Blocked** - click it to see the
   per-stage audit trail
5. Check the **Ledger integrity** panel: tamper with a row and the chain
   verification immediately reports `NOT_INTACT`

## Project layout

```
app.py                     Thin WSGI entrypoint (factory-delegated)
application/               app factory (create_app) - testable under any WSGI server
config/                    env-driven settings
database/                  sqlite schema + seed + db access
ml/                        behaviour model + manipulation-LLM wrappers
modules/                   the 15 decision stages + shared pipeline
routes/                    agent / dashboard / review blueprints
security/                  crypto, ledger, JWT
static/  templates/        frontend (dashboard.html, charts, CSS)
scripts/                   run / seed / test / prepare-ci helpers
tests/                     smoke + unit tests (unittest; pytest-compatible)
docs/                      this repo's documentation
requirements/              base.txt (runtime) + dev.txt (tests/CI)
.github/workflows/ci.yml   CI: lint+test+boot smoke
```

## Docs

| Document | What it answers |
| --- | --- |
| [docs/BUGS.md](docs/BUGS.md) | Every known bug, its observable effect, and severity |
| [docs/FIXES.md](docs/FIXES.md) | Bug -> fix, and *why* the fix is correct |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline, modules, governor, data flow |
| [docs/API.md](docs/API.md) | HTTP endpoints + auth + example payloads |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Version history |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | How to contribute |
| [docs/SECURITY.md](docs/SECURITY.md) | Security model, threats, trust boundaries |
| [docs/ROADMAP.md](docs/ROADMAP.md) | What is next |

## License

[MIT](LICENSE)
