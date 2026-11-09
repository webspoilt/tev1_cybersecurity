# Tev1 Verification Clause Ablation Report

## Executive Summary

An evaluation-only ablation experiment was executed on the 50-step QLoRA pilot adapter (`v2_experiments/tev1_qlora_pilot_v1`) to determine whether model performance is genuinely reasoning over cybersecurity telemetry or solely dependent on repeated trailing verification clauses identified in the generalization audit.

- **Ablation Methodology:** Evaluated on all 700 held-out validation records from `tev1_triage_candidate_val.jsonl`. For each record, the repeated trailing verification clauses (sentences 5 and 6) were removed, leaving only the authentic telemetry, hostnames, timestamps, user identities, and environmental context (sentences 0 to 4).
- **Core Result:** Accuracy collapsed from **97.00%** (Original) to **14.71%** (Ablated), representing an absolute regression of **-82.29 percentage points**. Macro F1 collapsed from **97.05%** to **5.02%** (**-92.03 percentage points**).
- **Behavioral Shift:** Stripped of the synthetic verification boilerplate, the adapter collapsed into predicting Option B (`suspicious`) for **669 out of 700 records (95.57%)**.
- **Evidence vs. Boilerplate Finding:** In the upstream OpenSec-Triage dataset, the trailing verification clause was not merely decorative boilerplate—it contained **100% of the decisive investigative evidence** separating malicious, benign, administrative, and testing actions.

---

## 1. Macro Results: Original vs. Ablated Performance

Both evaluations used identical model weights, 4-bit NF4 quantization, greedy decoding (`do_sample=False`, `max_new_tokens=4`), and ChatML system prompts on an NVIDIA GeForce RTX 3050 Laptop GPU:

| Metric | Original Val (With Verification Clauses) | Ablated Val (Telemetry Only) | Absolute Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **97.00%** (679 / 700) | **14.71%** (103 / 700) | **-82.29 pp** |
| **Macro F1** | **97.05%** | **5.02%** | **-92.03 pp** |
| **Invalid Output Rate** | 0.00% (0 / 700) | 0.00% (0 / 700) | 0.00 pp |
| **Evaluation Latency** | 601.5 ms / sample (warm) | 593.1 ms / sample (warm) | -8.4 ms |
| **Option B (`suspicious`) Frequency** | 118 / 700 (16.86%) | **669 / 700 (95.57%)** | **+78.71 pp** |

---

## 2. Per-Class Performance Breakdown

Each class evaluated exactly 100 validation records ($N=700$ total):

| Class Letter & Name | Original Recall | Ablated Recall | $\Delta$ Recall | Original Precision | Ablated Precision | $\Delta$ Precision | Original F1 | Ablated F1 | $\Delta$ F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 100.0% | 5.0% | **-95.0 pp** | 100.0% | 20.0% | **-80.0 pp** | 100.0% | 8.0% | **-92.0 pp** |
| **B (`suspicious`)** | 99.0% | 97.0% | **-2.0 pp** | 83.9% | 14.5% | **-69.4 pp** | 90.8% | 25.2% | **-65.6 pp** |
| **C (`benign`)** | 89.0% | 0.0% | **-89.0 pp** | 100.0% | 0.0% | **-100.0 pp** | 94.2% | 0.0% | **-94.2 pp** |
| **D (`expected_admin`)** | 100.0% | 0.0% | **-100.0 pp** | 99.0% | 0.0% | **-99.0 pp** | 99.5% | 0.0% | **-99.5 pp** |
| **E (`authorised_testing`)** | 99.0% | 0.0% | **-99.0 pp** | 100.0% | 0.0% | **-100.0 pp** | 99.5% | 0.0% | **-99.5 pp** |
| **F (`misconfiguration`)** | 100.0% | 1.0% | **-99.0 pp** | 99.0% | 16.7% | **-82.3 pp** | 99.5% | 1.9% | **-97.6 pp** |
| **G (`unknown`)** | 92.0% | 0.0% | **-92.0 pp** | 100.0% | 0.0% | **-100.0 pp** | 95.8% | 0.0% | **-95.8 pp** |

---

## 3. Confusion Matrix Analysis

### Original Pilot Confusion Matrix (With Verification Clauses)
```
        A     B     C     D     E     F     G
  A [ 100     0     0     0     0     0     0 ]
  B [   0    99     0     0     0     1     0 ]
  C [   0    11    89     0     0     0     0 ]
  D [   0     0     0   100     0     0     0 ]
  E [   0     0     0     1    99     0     0 ]
  F [   0     0     0     0     0   100     0 ]
  G [   0     8     0     0     0     0    92 ]
```

### Ablated Pilot Confusion Matrix (Telemetry Only, Clauses Removed)
```
        A     B     C     D     E     F     G
  A [   5    95     0     0     0     0     0 ]
  B [   2    97     0     0     0     1     0 ]
  C [   5    94     0     0     0     1     0 ]
  D [   2    95     0     0     0     3     0 ]
  E [   2    98     0     0     0     0     0 ]
  F [   6    93     0     0     0     1     0 ]
  G [   3    97     0     0     0     0     0 ]
```
*Diagnosis:* When the verification clauses are ablated, the model completely loses discriminative capacity across classes C, D, E, and G ($0\%$ recall across all four classes). It defaults almost uniformly to Option B (`suspicious`) on 669 out of 700 samples.

---

## 4. Substantive Evidence Loss Audit

A crucial question is whether removing the trailing clauses removed mere stylistic boilerplate or the actual ground-truth evidence:

- **Total records where clause removal removed substantive evidence:** **700 / 700 (100.0%)**
- **Quantification of Telemetry Ambiguity:** In the ablated dataset, **149 telemetry descriptions (sentences 0–4) are completely identical across multiple conflicting target classes**.
  - *Example:* `Dns server audit on SALES-ASSET-4fa85195b0666958 recorded that a client requested a DNS zone transfer. The event references principal-e2162f60002fb61c. Business context: customer relationship management. Environment: Centrally managed services...`
  - In Record ID 12, this exact telemetry was classified as **`malicious`** because sentence 5 added: *"Process correlation links the action to code that incident responders independently verified was under attacker control."*
  - In Record ID 614, this exact same telemetry was classified as **`unknown`** because sentence 5 added: *"The workflow and authorisation records for this time window expired before review."*
  - In enterprise networks, a DNS zone transfer or a temporary service creation is intrinsically dual-use; without investigative corroboration, ground truth cannot be determined by human analysts or models alike.

---

## 5. Distinguishing Evidence from Inference

### Empirical Evidence
1. **Measured Fact:** The pilot adapter's accuracy on the validation split drops from 97.00% to 14.71% when sentences 5 and 6 are removed.
2. **Measured Fact:** 100% of validation records share trailing verification clause templates with the 3,500 training samples.
3. **Measured Fact:** The 14.71% ablated accuracy is essentially baseline chance agreement for a model that defaults to Option B (since Option B makes up 100 of the 700 ground truth samples, predicting Option B 669 times yields $97 / 100 = 97$ true positives for class B, which accounts for $97 / 103 = 94.2\%$ of all correct ablated predictions).

### Grounded Inference
1. **The adapter's high 97.00% performance is strictly dependent on the trailing verification clauses.** The adapter did not learn an invariant mental model of cybersecurity alert telemetry; rather, it learned to parse and map the closed pool of ~14 verification clause templates directly to classes A–G.
2. **OpenSec-Triage is a synthetic two-stage dataset.** The front half (telemetry) is intentionally non-deterministic and insufficient for triage on its own; the back half (investigative clause) acts as an explicit text label generator.
3. **The adapter defaults to a defensive prior under uncertainty.** When stripped of the decisive verification sentence, the adapter defaults to predicting `suspicious` (Option B) 95.6% of the time, behaving as a risk-averse default classifier.

---

## 6. Deliverables & Safety Preservations

- **Ablation Results JSON:** [`v2_experiments/tev1_clause_ablation_results.json`](file:///C:/Users/ASUS/Desktop/jev/v2_experiments/tev1_clause_ablation_results.json)
- **Ablation Predictions JSONL:** [`v2_experiments/tev1_clause_ablation_predictions.jsonl`](file:///C:/Users/ASUS/Desktop/jev/v2_experiments/tev1_clause_ablation_predictions.jsonl)
- **Ablated Dataset:** [`tev1_training_candidate/tev1_triage_candidate_val_ablated.jsonl`](file:///C:/Users/ASUS/Desktop/jev/tev1_training_candidate/tev1_triage_candidate_val_ablated.jsonl)
- **Safety Lock:** `CONFIRM_FINETUNE` remains locked to `False`. The pilot adapter and all original benchmark evaluations remain segregated and preserved.
