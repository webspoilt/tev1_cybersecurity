# Tev1 Grouped Template-Held-Out Generalization Audit

## Executive Summary

To determine whether Tev1 can interpret defensive cybersecurity verification evidence it has not encountered during training—rather than memorizing closed sets of recurring phrases—a structured grouped template-held-out experiment was designed across all 4,200 candidate records (3,500 original training + 700 original validation).

- **Objective:** Construct a rigorous, non-overlapping dataset split where entire verification-template families are held out from training, while preserving full telemetry, operational context, and ground-truth evidence.
- **Safety Status:** **`CONFIRM_FINETUNE = False`**. No training was started. Base model weights, baseline benchmark records (61.73%), and the existing 50-step pilot adapter (`v2_experiments/tev1_qlora_pilot_v1`) remain completely preserved and untouched.
- **Template Diversity Reality:** An exhaustive audit reveals that OpenSec-Triage contains **exactly 5 independent lead template families per class** (35 families total across all 7 classes).
- **Grouped Split Created:** A clean 4:1 template-family grouped split was constructed:
  - **Train:** 3,423 records across 28 template families (4 per class).
  - **Val:** 777 records across 7 held-out template families (1 per class).
  - **Group Overlap:** **0.0% (Verified 0 shared template families)**.
- **Final Verdict:** **`INSUFFICIENT TEMPLATE DIVERSITY FOR ADVANCED GENERALIZATION`**. While the 4:1 split is technically valid and ready for testing, having only 5 synthetic template archetypes per class is too brittle to support claims of generalized cybersecurity reasoning. We recommend replacing or supplementing this synthetic dataset with a diverse, naturally authored source.

---

## 1. Phase 1 — Template Grouping & Semantic Audit

Every record in OpenSec-Triage exhibits a rigid 7-sentence structure where sentences 5 and 6 provide the conclusive investigative disposition:
- **Sentence 5:** The primary investigative finding (lead clause).
- **Sentence 6:** The corroborating cross-check (trailing clause).

### Template Diversity per Class

| Class Letter | Triage Category | Total Records Analyzed | Distinct Raw Clauses | Normalized Skeletons | Independent Lead Template Families |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **A** | `malicious` | 600 | 15 | 15 | **5** |
| **B** | `suspicious` | 600 | 14 | 14 | **5** |
| **C** | `benign` | 600 | 14 | 14 | **5** |
| **D** | `expected_admin` | 600 | 600 | 14 | **5** |
| **E** | `authorised_testing` | 600 | 600 | 14 | **5** |
| **F** | `misconfiguration` | 600 | 14 | 14 | **5** |
| **G** | `unknown` | 600 | 15 | 15 | **5** |
| **Total** | — | **4,200** | **1,257** | **100** | **35** |

*(Note on Classes D & E: Although raw text appeared unique due to randomized change IDs `CHG-xxxx` and exercise IDs `SEC-xxxx`, normalizing the identifiers reveals that they also derive from exactly 14 syntactic skeleton templates mapped to 5 core semantic families).*

### Evidence Content vs. Stylistic Boilerplate

The audit proves that the template families **do not contain decorative filler**—they contain the **definitive ground-truth discriminators**:
- **Class A Template Families:** Describe stolen tokens, code under attacker control, credential reuse, account takeover, or unauthorized workload modification.
- **Class D Template Families:** Describe approved operations requests, reviewed maintenance runbooks, change management tickets (`CHG-xxxx`), or authorized recovery procedures.
- **Class G Template Families:** Describe expired authorization records, telemetry gaps, unresolvable attribution, or conflicting context sources.

---

## 2. Phase 2 — Grouped Split Construction & Overlap Verification

Rather than randomly partitioning alerts (which caused the 100% template leakage in the original split), records were partitioned strictly by **semantic template family**.

### Split Methodology (4:1 Template Holdout)
- For each of the 7 classes, **4 template families** are allocated to Training, and **1 complete template family** is strictly held out for Validation.
- Ground-truth evidence is preserved in full; no clauses were ablated or removed.
- Source attribution (CC BY 4.0, `tegridydev/opensec-triage`) is preserved in every record.

### Class Distribution: Original Random Split vs. New Grouped Split

| Class Letter & Name | Original Random Train | Original Random Val | New Grouped Train (4 Families) | New Grouped Val (1 Held-Out Family) |
| :--- | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 500 (14.3%) | 100 (14.3%) | 483 (14.1%) | 117 (15.1%) |
| **B (`suspicious`)** | 500 (14.3%) | 100 (14.3%) | 508 (14.8%) | 92 (11.8%) |
| **C (`benign`)** | 500 (14.3%) | 100 (14.3%) | 476 (13.9%) | 124 (16.0%) |
| **D (`expected_admin`)** | 500 (14.3%) | 100 (14.3%) | 535 (15.6%) | 65 (8.4%) |
| **E (`authorised_testing`)** | 500 (14.3%) | 100 (14.3%) | 474 (13.8%) | 126 (16.2%) |
| **F (`misconfiguration`)** | 500 (14.3%) | 100 (14.3%) | 480 (14.0%) | 120 (15.4%) |
| **G (`unknown`)** | 500 (14.3%) | 100 (14.3%) | 467 (13.6%) | 133 (17.1%) |
| **Total Record Count** | **3,500** | **700** | **3,423** | **777** |
| **Template Family Overlap** | **100.0%** (35 / 35) | **100.0%** (35 / 35) | **0.0% (0 / 35)** | **0.0% (0 / 35)** |

### Held-Out Validation Families by Class

1. **A (`malicious`):** *"The action traces to a workload for which forensic review established an unauthorised change of control."* (117 records)
2. **B (`suspicious`):** *"The volume and timing differ from the established baseline and the responsible team has not explained the deviation."* (92 records)
3. **C (`benign`):** *"The action matches a recurring business transaction in prior reviewed sessions, including its scope and result."* (124 records)
4. **D (`expected_admin`):** *"The resource owner’s approved operations request <CHG_ID> explicitly covers the action and initiating administrator."* (65 records)
5. **E (`authorised_testing`):** *"The security team’s validation job <SEC_ID> accounts for the observed action and its target scope."* (126 records)
6. **F (`misconfiguration`):** *"An incorrect retry setting caused the action to recur; service traces reproduced the same sequence."* (120 records)
7. **G (`unknown`):** *"Two context sources disagree about workflow attribution and neither can be independently verified."* (133 records)

---

## 3. Phase 3 — Deliverables & Integrity Manifest

The grouped candidate datasets and manifest have been created:

- **Grouped Train File:** [`tev1_grouped_template_train.jsonl`](file:///C:/Users/ASUS/Desktop/jev/tev1_grouped_template_train.jsonl)
  - Records: 3,423
  - SHA-256: `0d3362f0b2a30021c6e349038832ab94ea955049b1d90b2ca59a5d63722b94f5`
- **Grouped Val File:** [`tev1_grouped_template_val.jsonl`](file:///C:/Users/ASUS/Desktop/jev/tev1_grouped_template_val.jsonl)
  - Records: 777
  - SHA-256: `fa9d49da881df0f6462111bc6f259981ac781ac33e3f96b519fd9a1bd35bcd64`
- **Manifest:** [`tev1_grouped_template_manifest.json`](file:///C:/Users/ASUS/Desktop/jev/tev1_grouped_template_manifest.json)
  - Documents exact hashes, record counts, and zero template-family overlap.

---

## 4. Final Verdict & Strategic Recommendation

# **Final Verdict: INSUFFICIENT TEMPLATE DIVERSITY FOR ADVANCED GENERALIZATION**

### Evaluation Analysis
1. **Source Limitations:** The entire OpenSec-Triage dataset is driven by a synthetic combinatorial generator with only **5 core sentence archetypes per class**. Holding out 1 archetype for validation leaves only 4 archetypes for training.
2. **Experimental Feasibility:** The proposed 3,423-train / 777-val split is technically ready and offers a strict zero-leakage test of whether Tev1 can semantically generalize across template archetypes (e.g., generalizing from *"stolen token"* to *"unauthorised change of control"*).
3. **Core Recommendation:** 
   - **Step A:** If desired, run a single, low-cost 50-step experiment on `tev1_grouped_template_train.jsonl` to measure if Tev1 achieves non-trivial zero-shot transfer on the held-out templates (requires explicit user approval).
   - **Step B:** Do not rely on OpenSec-Triage as the sole benchmark of cybersecurity decision capability. Prepare an authentic, independently authored dataset (such as Splunk BOTS or CIC-IDS triage narratives) where lexical variety, natural human investigation notes, and noisy telemetry provide authentic evaluation rigor.
