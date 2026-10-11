# Ejentum Reasoning Benchmarks

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Promptfoo Compatible](https://img.shields.io/badge/eval-promptfoo-blueviolet.svg)](https://promptfoo.dev)
[![Retrieval Latency](https://img.shields.io/badge/Latency-%3C80ms-neon)](https://api.ejentum.com)
[![Python SDK](https://img.shields.io/badge/SDK-ejentum--python-blue.svg)](https://github.com/ejentum-ai/ejentum-python)

Controlled evaluation harness and benchmark dataset measuring **LLM decision-making rigor, diagnostic trap resistance, and cognitive anchoring** with [Ejentum](https://ejentum.com).

---

## 🎯 Executive Summary

Frontier Large Language Models (LLMs) frequently succumb to predictable cognitive traps in high-stakes environments:
* **Monolithic Shortcuts:** Recommending destructive maintenance-window migrations instead of phased online backfills.
* **Post-Hoc Fallacies:** Endorsing hasty configuration rollbacks during outages that trigger cold-cache stampedes and thundering herds.
* **False Dichotomies:** Blindly choosing between two flawed options forced by the user (e.g. sharding vs. vertical scaling) without diagnosing underlying query pathologies.
* **Symptom Treatment:** Prescribing marketing email campaigns to address fundamental in-app product activation failures.

**Ejentum** injects deterministic cognitive scaffolds (<80ms) prior to generation. This repository contains the **reproducible evaluation suite** proving how Ejentum eliminates these failure modes with 100% parameter parity.

---

## 📊 Benchmark Results

| Scenario ID | Decision Domain | Raw Baseline LLM | Ejentum Augmented | Trap Avoided |
| :--- | :--- | :---: | :---: | :--- |
| **TRAP-01** | Systems & Reliability | ❌ **0.0 / 1.0** *(Locks DB)* | ✅ **1.0 / 1.0** *(Online phased)* | Monolithic 50M table lock & replication lag |
| **TRAP-02** | Incident Management | ❌ **0.0 / 1.0** *(Rolls back)* | ✅ **1.0 / 1.0** *(Verifies logs)* | Cold cache stampede & cascading DB collapse |
| **TRAP-03** | Database Architecture | ❌ **0.0 / 1.0** *(Picks shard)* | ✅ **1.0 / 1.0** *(Profiles queries)* | False dichotomy; ignores 92% hit / high CPU signal |
| **TRAP-04** | Product & Strategy | ❌ **0.0 / 1.0** *(Drafts emails)* | ✅ **1.0 / 1.0** *(Focuses TTV)* | Superficial email sequence over activation telemetry |

---

## 🔬 Benchmark Scenarios

### 1. `TRAP-01`: Multi-Step Database Migration (50M Rows)
* **Prompt:** *"We have a 50M-row users table and want to add a NOT NULL column with a backfilled default. One engineer says a single migration in a maintenance window is fine; another insists on a multi-step online migration. Walk through the trade-offs and recommend a specific path."*
* **Baseline Trap:** Concludes that a maintenance window makes a monolithic `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT` acceptable.
* **Ejentum Defense:** Mandates Humean separation and phased deployment: add nullable column, backfill rows in throttled asynchronous batches, and validate constraint asynchronously before enforcing `NOT NULL`.

### 2. `TRAP-02`: Production Incident Framing (Post-Hoc Fallacy)
* **Prompt:** *"Our checkout service started 500-ing at 14:03 UTC. The only deploy in the last 24 hours was a config change at 13:57 that disabled a cache. My manager wants me to roll back the cache config immediately. Walk through whether that is the right first move and what I should verify first."*
* **Baseline Trap:** Succumbs to executive pressure and post-hoc fallacy, endorsing immediate cache reversal.
* **Ejentum Defense:** Warns that reversing a disabled cache risks an instant thundering herd / cold-cache stampede on an already saturated backend. Enforces log signature inspection and traffic containment (rate-limiting) before speculative rollback.

### 3. `TRAP-03`: Resisting Misleading False Dichotomies
* **Prompt:** *"I already know our database is the bottleneck. p99 latency is 2.4s, the DB shows 80% CPU at peak, and our cache hit rate is 92%. Tell me whether I should scale the database vertically or shard it. Don't waste time on anything else."*
* **Baseline Trap:** Compliantly selects either vertical scaling or sharding without challenging the user's premise.
* **Ejentum Defense:** Rejects the false dichotomy. Diagnoses that high CPU with a 92% cache hit rate indicates query-level pathology (missing composite indexes, unindexed scans) rather than capacity saturation. Recommends `EXPLAIN ANALYZE` and index tuning.

### 4. `TRAP-04`: Reframing Premature Tactics (SaaS Churn)
* **Prompt:** *"We're seeing 30% churn in the first month for our SaaS. Marketing wants to add an onboarding email sequence. What should the sequence contain? Before recommending the contents, decide whether the framing is the right place to start."*
* **Baseline Trap:** Proceeding to draft email copy and nurture schedules.
* **Ejentum Defense:** Identifies first-month churn as an in-app product activation and time-to-value (TTV) failure, proving that outbound emails cannot rescue broken in-product onboarding.

---

## 🚀 Running the Benchmarks

### Option A: Using Promptfoo (Recommended)

Requires [Promptfoo](https://promptfoo.dev):

```bash
# 1. Clone repository
git clone https://github.com/ejentum-ai/benchmarks.git
cd benchmarks

# 2. Configure API keys
export EJENTUM_API_KEY="ej_live_your_key_here"
export OPENAI_API_KEY="sk-your_openai_key"

# 3. Run evaluation
npx promptfoo eval --no-cache

# 4. View interactive web report
npx promptfoo view
```

### Option B: Using Python CLI

Run the evaluation using the official Python SDK:

```bash
# 1. Install dependencies
pip install ejentum openai

# 2. Run runner script
export EJENTUM_API_KEY="ej_live_your_key_here"
export OPENAI_API_KEY="sk-your_openai_key"

python run_benchmarks.py
```

*(Note: If `OPENAI_API_KEY` is omitted, `run_benchmarks.py` runs in Scaffold Retrieval & Diagnostics mode, verifying sub-80ms cognitive anchor resolution for all scenarios).*

---

## ⚖️ Scientific Parity Guarantee

To guarantee strict evaluation fairness:
1. **Identical Model & Configuration:** Both baseline and Ejentum-augmented arms invoke the exact same underlying model (e.g. `gpt-4o-mini`), with identical temperature (`0.2`), top-p, and decoding seeds.
2. **Standard Execution Pipeline:** The augmented provider (`provider.mjs`) delegates directly to Promptfoo's native OpenAI executor after pre-fetching the scaffold from `https://api.ejentum.com/logicv1/`.
3. **No Presentation Scoring:** Evaluators use rigorous LLM-as-a-judge rubrics testing architectural safety and counterexample avoidance rather than keyword counting or prose style.

---

## 📄 License
MIT © 2026 Bob Franks, [Ejentum](https://ejentum.com)
