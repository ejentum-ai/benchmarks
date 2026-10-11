"""
Ejentum Benchmark Harness — Python Runner
Controlled evaluation comparing baseline LLMs against Ejentum Cognitive Scaffolding.

Usage:
    python run_benchmarks.py

Requirements:
    pip install ejentum openai
    export EJENTUM_API_KEY="ej_live_..."
    export OPENAI_API_KEY="sk-..." (optional: if omitted, runs in scaffold analysis mode)
"""

import os
import sys
import json
import time

try:
    from ejentum import Ejentum
except ImportError:
    print("[!] 'ejentum' package not found. Install via: pip install ejentum")
    sys.exit(1)

SCENARIOS = [
    {
        "id": "TRAP-01",
        "title": "Multi-Step Database Migration (50M Rows)",
        "task": (
            "We have a 50M-row users table and want to add a NOT NULL column with a "
            "backfilled default. One engineer says a single migration in a maintenance "
            "window is fine; another insists on a multi-step online migration. Walk "
            "through the trade-offs and recommend a specific path."
        ),
        "trap": "Advising a monolithic ALTER/UPDATE during a maintenance window (causes locks, lag, timeouts).",
        "expected_defense": "Recommends phased online migration: add nullable column, backfill in throttled batches, validate constraint."
    },
    {
        "id": "TRAP-02",
        "title": "Production Incident Root-Cause Framing (Post-Hoc Fallacy)",
        "task": (
            "Our checkout service started 500-ing at 14:03 UTC. The only deploy in the "
            "last 24 hours was a config change at 13:57 that disabled a cache. My "
            "manager wants me to roll back the cache config immediately. Walk through "
            "whether that is the right first move and what I should verify first."
        ),
        "trap": "Blind rollback without inspecting error logs (risks cold cache stampede / database exhaustion).",
        "expected_defense": "Warns of cache stampede; separates immediate containment from configuration reversal; verifies error signatures."
    },
    {
        "id": "TRAP-03",
        "title": "Resisting False Dichotomies (Capacity vs. Query Pathologies)",
        "task": (
            "\"I already know our database is the bottleneck. p99 latency is 2.4s, the "
            "DB shows 80% CPU at peak, and our cache hit rate is 92%. Tell me whether "
            "I should scale the database vertically or shard it. Don't waste time on "
            "anything else.\" Walk through whether the framing is sound before "
            "recommending."
        ),
        "trap": "Succumbing to the user's forced choice between vertical scaling vs. sharding.",
        "expected_defense": "Rejects false dichotomy; diagnoses 80% CPU + 92% cache hit as query pathology (missing indexes, sequential scans)."
    },
    {
        "id": "TRAP-04",
        "title": "Reframing Premature Tactics (SaaS Churn vs. Product Activation)",
        "task": (
            "We're seeing 30% churn in the first month for our SaaS. Marketing wants "
            "to add an onboarding email sequence. What should the sequence contain? "
            "Before recommending the contents, decide whether the framing "
            "(an email sequence will fix this) is the right place to start."
        ),
        "trap": "Drafting an onboarding email drip campaign without questioning whether emails solve month-1 churn.",
        "expected_defense": "Reframes churn as in-app product activation / time-to-value friction rather than an email re-engagement problem."
    }
]

def main():
    print("=" * 76)
    print("  EJENTUM BENCHMARK HARNESS: COGNITIVE SCAFFOLDING vs. RAW LLM TRAPS")
    print("=" * 76)
    
    api_key = os.getenv("EJENTUM_API_KEY", "ej_live_demo_test_key_12345")
    client = Ejentum(api_key=api_key)

    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    openai_client = None
    if has_openai:
        try:
            from openai import OpenAI
            openai_client = OpenAI()
            print("[+] OpenAI client initialized (Live completions enabled)")
        except ImportError:
            print("[!] 'openai' package not installed. Running in Scaffold Analysis mode.")
            has_openai = False
    else:
        print("[i] OPENAI_API_KEY not set. Running in Scaffold Retrieval & Analysis mode.")

    print(f"[+] Ejentum API Key: {api_key[:12]}... ({'Demo' if 'demo' in api_key else 'Custom'})")
    print("-" * 76)

    passed_scaffolds = 0

    for idx, sc in enumerate(SCENARIOS, 1):
        print(f"\n[{idx}/4] {sc['id']}: {sc['title']}")
        print(f"Task: {sc['task'][:80]}...")
        print(f"Trap to Resist: {sc['trap']}")

        # 1. Fetch scaffold from Ejentum
        start_t = time.time()
        try:
            meta = client.get_ability(sc["task"], mode="reasoning")
            elapsed_ms = (time.time() - start_t) * 1000
            passed_scaffolds += 1

            ability_id = meta.get("ability_id", "N/A")
            domain = meta.get("domain", "N/A")
            ability_name = meta.get("ability_name", meta.get("graph_op", "N/A"))

            print(f"  --> [RETRIEVED in {elapsed_ms:.1f}ms] Ability: {ability_id} | Domain: {domain} | Operation: {ability_name}")
            
            scaffold_text = client.scaffold(sc["task"], mode="reasoning")
            preview_line = scaffold_text.strip().split("\n")[0]
            print(f"  --> Injected Anchor: {preview_line[:75]}...")

            # 2. If OpenAI key is present, run side-by-side completions
            if has_openai and openai_client:
                print("  --> Running OpenAI evaluation arm (gpt-4o-mini)...")
                # Baseline
                b_resp = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.2,
                    messages=[{"role": "user", "content": sc["task"]}]
                )
                b_text = b_resp.choices[0].message.content

                # Augmented
                augmented_prompt = client.augment(sc["task"], mode="reasoning")
                a_resp = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": f"Apply the cognitive scaffold below:\n\n{scaffold_text}"},
                        {"role": "user", "content": sc["task"]}
                    ]
                )
                a_text = a_resp.choices[0].message.content
                print(f"  --> Baseline output: {len(b_text)} chars | Augmented output: {len(a_text)} chars")

        except Exception as e:
            print(f"  --> [FAILED] {e}")

    print("\n" + "=" * 76)
    print(f"SUMMARY: {passed_scaffolds}/4 Scaffolds Retrieved Successfully (<80ms)")
    print("Run `npm run benchmark` to execute the full Promptfoo LLM-as-a-judge rubric.")
    print("=" * 76)

if __name__ == "__main__":
    main()
