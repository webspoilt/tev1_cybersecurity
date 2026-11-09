# Tev1 Generalization and Evaluation Integrity Audit Report

## Executive Summary

Following the completion of the 50-step QLoRA pilot of `togethercomputer/Tev1-0.8B-experimental` and the controlled comparison reporting 97.00% adapter accuracy versus 35.57% base model accuracy, a rigorous four-part evaluation integrity and generalization audit was conducted across all 3,500 training records and 700 validation records.

- **Primary Verdict:** **`POSSIBLE TEMPLATE LEAKAGE`**
- **Safety Status:** `CONFIRM_FINETUNE` remains locked to `False`. Base weights, pilot adapters, and benchmark evaluations (`val_split_v1.jsonl`, 61.73% baseline) remain untouched and segregated.
- **Root Integrity Finding:** While exact duplicate records are **0 / 700 (0.0%)**, and surface near-duplicates ($Jaccard \ge 0.80$) are limited to **31 / 700 (4.4%)**, **100.0% (700 / 700) of validation records share verbatim normalized verification/evidence clauses with the training set**. The upstream OpenSec-Triage dataset relies on a synthetic template grammar where ~14–15 fixed verification phrases per class act as near-deterministic indicators.
- **Metric Verification:** All reported totals, confusion matrices, and the 21 pilot errors were verified bit-for-bit from the raw prediction logs. However, the claim that *"100% of errors are conservative"* is disproven: **19 of 21 (90.5%)** are conservative risk-averse shifts, but **2 errors (9.5%)** represent non-conservative misclassifications.
- **Latency Resolution:** The measured latency difference (1,830.6 ms vs. 393.5 ms) was caused by an un-warmed initial evaluation batch taking 920.5s for the first 100 samples (~9.2s/sample) during JIT setup. Controlled warm benchmarking reveals the true inference latency is **441.5 ms/sample (Base)** vs. **575.0 ms/sample (Pilot Adapter)** (~133.5 ms LoRA overhead).

---

## 1. Train-Validation Template Leakage & Overlap Audit

A full pairwise lexical, structural, and semantic skeleton comparison was executed between all 3,500 training records and all 700 validation records.

### Quantitative Overlap Summary

| Metric | Measured Value | Percentage of Val Set | Evaluation Implication |
| :--- | :---: | :---: | :--- |
| **Exact State Duplicates** | **0 / 700** | **0.0%** | Zero exact memorization of complete records. |
| **Exact Full Skeleton Matches** | **0 / 700** | **0.0%** | Telemetry parameters (assets, IPs, tools) vary across splits. |
| **Near-Duplicates ($Jaccard \ge 0.90$)** | **0 / 700** | **0.0%** | No near-identical entire alert scenarios. |
| **Near-Duplicates ($Jaccard \ge 0.80$)** | **31 / 700** | **4.4%** | Small fraction of scenarios share high overall token similarity. |
| **Mean Max-Token Jaccard** | **0.7058** | — | High background vocabulary sharing typical of domain text. |
| **Shared Normalized Verification Clauses** | **700 / 700** | **100.0%** | **CRITICAL LEAKAGE:** Every validation record shares a trailing verification clause with the training corpus. |

### The Leakage Mechanism: Fixed Synthetic Evidence Grammars

An audit of the sentence structures reveals that OpenSec-Triage alerts are composed of two parts:
1. **Front Scenario Body:** Parameterized asset hostnames (e.g., `SALES-ASSET-666e447c...`), principals, environments, and activity summaries.
2. **Trailing Verification Clause:** A 1-to-2 sentence conclusion describing corroborating evidence (e.g., *"Application traces map the action to a documented product feature..."*).

Crucially, in the upstream dataset, the trailing verification clauses are drawn from a closed pool of only **~14 to 15 unique phrases per class**:
- **Class A (`malicious`):** Only 15 unique verification clauses across 500 training examples.
- **Class B (`suspicious`):** Only 14 unique verification clauses across 500 training examples.
- **Class C (`benign`):** Only 14 unique verification clauses across 500 training examples.
- **Class F (`misconfiguration`):** Only 14 unique verification clauses across 500 training examples.
- **Class G (`unknown`):** Only 15 unique verification clauses across 500 training examples.
- *(Classes D and E inject randomized change IDs `CHG-xxxx` and exercise IDs `SEC-xxxx`, but retain identical syntactic templates).*

Because all 700 validation samples reuse these identical 14–15 trailing evidence templates, the 50-step QLoRA adapter learned to attend strongly to these closing grammatical cues rather than synthesizing complex raw telemetry.

---

## 2. Metric Integrity & Error Claim Re-Audit

All performance metrics were independently recomputed directly from [`tev1_base_val_predictions.jsonl`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/tev1_base_val_predictions.jsonl) and [`tev1_qlora_pilot_val_predictions.jsonl`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/tev1_qlora_pilot_val_predictions.jsonl).

### Recomputation Verification
- **Base Accuracy:** Recomputed at **35.5714%** (249 / 700). Matches reported 35.57%.
- **Pilot Accuracy:** Recomputed at **97.0000%** (679 / 700). Matches reported 97.00%.
- **Base Macro F1:** Recomputed at **30.7482%**. Matches reported 30.75%.
- **Pilot Macro F1:** Recomputed at **97.0488%**. Matches reported 97.05%.
- **Error Count:** Exactly **21 errors** confirmed out of 700 samples.

### Verification of the "Conservative Error" Claim
The prior report claimed that *"100% of errors are conservative, risk-averse shifts"*. A record-by-record re-audit disproves this claim:

1. **Genuinely Conservative (19 / 21 = 90.5%):**
   - **11 errors ($C \rightarrow B$):** `benign` classified as `suspicious`. (Defensive false alarm; risk-averse).
   - **8 errors ($G \rightarrow B$):** `unknown` classified as `suspicious`. (Uncorroborated telemetry flagged as suspicious; risk-averse).
2. **Non-Conservative Errors (2 / 21 = 9.5%):**
   - **Record ID 176 ($B \rightarrow F$):** Ground truth was `suspicious` (policy audit changed to collect fewer event categories during recovery), but the model predicted `misconfiguration` (Option F). Downgrading an unverified, potentially malicious policy suppression action to an operational misconfiguration is **non-conservative**.
   - **Record ID 493 ($E \rightarrow D$):** Ground truth was `authorised_testing` (security exercise), but the model predicted `expected_admin` (Option D). Conflating an adversarial assessment with routine system administration is an **administrative misattribution**, not a conservative triage action.

**Conclusion:** The claim must be updated: **90.5% of pilot errors are conservative, while 9.5% are non-conservative misclassifications.**

---

## 3. Latency Fairness & Measurement Resolution

The controlled comparison reported an evaluation latency of **393.5 ms/sample for Base** versus **1,830.6 ms/sample for the Pilot Adapter**. Both scripts used identical decoding parameters (`max_new_tokens=4`, `do_sample=False`, temperature=0.0).

### Root Cause Analysis of Latency Difference

An inspection of the timestamp checkpoints in the pilot evaluation log ([`task-2024.log`](file:///C:/Users/ASUS/.gemini/antigravity/brain/7078de16-ec97-4875-92e7-fdb49a17f247/.system_generated/tasks/task-2024.log)) revealed a massive warm-up skew:
- **First 100 samples (Samples 1–100):** Took **920.5 seconds** (~9,205 ms/sample).
- **Subsequent 600 samples (Samples 101–700):** Completed in **360.9 seconds** (**601.5 ms/sample**).

The 920.5-second initial delay occurred because `evaluate_pilot_val.py` ran without a GPU warm-up call, triggering PyTorch kernel initialization, Windows WDDM paging allocation, and PEFT weight-hook registration on the first batch under high memory pressure.

### Controlled Warm Single-Call Latency Benchmark

To establish fair latency under identical warm conditions, a 5-step warm forward benchmark was executed:
- **Pure Base Model:** **441.5 ms / call**
- **Pilot Adapter (Base + LoRA):** **575.0 ms / call**
- **True LoRA Latency Overhead:** **+133.5 ms / call** (a ~30% overhead for computing 12 linear LoRA adapter branches, not the inflated 365% artifact previously observed).

---

## 4. Independent Generalization Assessment

### What the 97.00% Validation Result Establishes
1. **Instruction & Decision Interface Discipline:** Tev1-0.8B successfully learned to adhere strictly to the decision interface, generating 100% valid single-character choices (A–G) enclosed in `<state>` tags without hallucinating explanations or conversational preambles.
2. **LoRA Parameter Plasticity:** Confirms that the 12 targeted projection modules (`q_proj`, `v_proj`, `linear_attn`, etc.) can be effectively trained under 4-bit QLoRA on an RTX 3050 without numerical instability or NaN divergence.
3. **Template Syntactic Association:** Confirms that Tev1 can reliably associate multi-sentence structured security evidence with discrete categorical outcomes.

### What the 97.00% Validation Result Does NOT Establish
1. **Does NOT prove generalization to naturalistic SOC telemetry:** Because the verification clauses in OpenSec-Triage are synthetically constrained to ~14 templates per class, the model may simply be functioning as an n-gram keyphrase matcher for those specific sentences.
2. **Does NOT prove robustness against varied real-world phrasing:** If an analyst writes *"User stated they forgot their password"* instead of the canonical *"The action matches a recurring business transaction in prior reviewed sessions"*, the model's accuracy may drop significantly.

### Recommended Independent Evaluation Dataset

To test true generalization without risking benchmark contamination or template leakage, we recommend testing against:
- **Splunk Boss of the SOC (BOTS v1–v3) / Certified SOC Incident Scenarios:**
  - Real-world enterprise network, Windows event, and endpoint logs collected during authentic red-team engagements and benign enterprise operations.
  - Human-adjudicated ground truth with naturalistic variance in alert telemetry, notes, and investigation steps.
  - Openly available under defensive research licensing without commercial restrictions.

---

## 5. Final Audit Verdict

# **Verdict: POSSIBLE TEMPLATE LEAKAGE**

### Audit Rationale
Although the model exhibits genuine learning and zero complete-record memorization (0 exact duplicates), the presence of identical, low-cardinality verification templates across 100% of the validation set means that the 97.00% accuracy score cannot be interpreted as uncompromised generalization to arbitrary cybersecurity telemetry. 

The pilot adapter should be preserved as a successful proof of technical feasibility and format compliance, but claims of real-world operational triage mastery must be held until evaluated against an independent, naturalistic SOC dataset.
