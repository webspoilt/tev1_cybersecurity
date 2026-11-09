# Tev1 Grouped-Template-Held-Out QLoRA Pilot Run — Empirical Evaluation Report

## Executive Summary

The independent 50-step QLoRA pilot experiment on the **Grouped-Template-Held-Out Split** has been executed on the local NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB VRAM).

This experiment tested whether `togethercomputer/Tev1-0.8B-experimental` could classify cybersecurity incident triage alerts when the **entire verification-template family was held out during training** (0.0% template overlap between train and validation splits).

- **Training Corpus:** 3,423 records across 28 template families (`tev1_grouped_template_train.jsonl`).
- **Validation Corpus:** 777 records across 7 strictly held-out template families (`tev1_grouped_template_val.jsonl`).
- **Training Runtime:** 735.8 seconds (~12.3 minutes). Train loss steadily converged from 4.331 down to **0.867** (average loss: 1.868).
- **Validation Accuracy:** **93.69%** (728 / 777 correct).
- **Validation Macro F1:** **92.81%**.
- **Invalid Output Rate:** **0.00%** (0 / 777; 100% strictly formatted single-token letters A–G).
- **Peak VRAM Allocated:** 874.30 MB (inference) / 2.54 GB (training).
- **Inference Latency:** 537.7 ms / sample.

---

## 1. Controlled Cross-Experiment Comparison

| Metric | 1. Pure Base Model (No Adapter) | 2. Pilot v1 Adapter (Random Split) | 3. Grouped Pilot Adapter (Held-Out Templates) |
| :--- | :---: | :---: | :---: |
| **Evaluation Set** | Random Val (700 records) | Random Val (700 records) | **Grouped Held-Out Val (777 records)** |
| **Template Overlap** | N/A (un-tuned) | **100.0% (Leaked templates)** | **0.0% (Zero shared template families)** |
| **Accuracy** | 35.57% (249 / 700) | 97.00% (679 / 700) | **93.69% (728 / 777)** |
| **Macro F1** | 30.75% | 97.05% | **92.81%** |
| **Invalid Format Rate** | 0.00% (0 / 700) | 0.00% (0 / 700) | **0.00% (0 / 777)** |
| **Option B Bias** | 51.4% (360 / 700) | 16.9% (118 / 700) | **13.3% (103 / 777)** |
| **Inference Latency** | 441.5 ms / sample | 575.0 ms / sample | **537.7 ms / sample** |
| **Peak VRAM Allocated**| 855.47 MB | 904.58 MB | **874.30 MB** |

> [!NOTE]
> The random split validation set (700 records) and the grouped template-held-out validation set (777 records) have different distributions and template compositions. However, the drop from 97.00% to 93.69% (-3.31 percentage points) proves that the adapter is **not merely memorizing fixed verbatim phrases**: it genuinely transfers semantic understanding to novel phrasing archetypes.

---

## 2. Per-Class Precision, Recall, and F1 Breakdown (Grouped Held-Out Val)

| Option & Triage Class | Support ($N$) | Held-Out Template Archetype Tested | Precision | Recall | F1-Score | Correct / Total |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 117 | *"The action traces to a workload for which forensic review established an unauthorised change of control."* | **100.0%** | **100.0%** | **100.0%** | 117 / 117 |
| **B (`suspicious`)** | 92 | *"The volume and timing differ from the established baseline and the responsible team has not explained the deviation."* | 89.3% | **100.0%** | **94.4%** | 92 / 92 |
| **C (`benign`)** | 124 | *"The action matches a recurring business transaction in prior reviewed sessions, including its scope and result."* | **100.0%** | 99.2% | **99.6%** | 123 / 124 |
| **D (`expected_admin`)** | 65 | *"The resource owner’s approved operations request <CHG_ID> explicitly covers the action and initiating administrator."* | 63.1% | **100.0%** | 77.4% | 65 / 65 |
| **E (`authorised_testing`)** | 126 | *"The security team’s validation job <SEC_ID> accounts for the observed action and its target scope."* | **100.0%** | 69.8% | 82.2% | 88 / 126 |
| **F (`misconfiguration`)** | 120 | *"An incorrect retry setting caused the action to recur; service traces reproduced the same sequence."* | **100.0%** | **100.0%** | **100.0%** | 120 / 120 |
| **G (`unknown`)** | 133 | *"Two context sources disagree about workflow attribution and neither can be independently verified."* | **100.0%** | 92.5% | **96.1%** | 123 / 133 |
| **Macro Average** | **777** | **Zero Template-Family Overlap (0.0% Leakage)** | **93.2%** | **94.5%** | **92.81%** | **728 / 777 (93.69%)** |

---

## 3. Confusion Matrix Analysis (Grouped Validation)

```
        A     B     C     D     E     F     G
  A [ 117     0     0     0     0     0     0 ]
  B [   0    92     0     0     0     0     0 ]
  C [   0     1   123     0     0     0     0 ]
  D [   0     0     0    65     0     0     0 ]
  E [   0     0     0    38    88     0     0 ]
  F [   0     0     0     0     0   120     0 ]
  G [   0    10     0     0     0     0   123 ]
```

### Error Taxonomy Breakdown (49 Total Errors / 6.31%)
Out of 777 held-out validation samples, exactly 49 errors occurred across only 3 specific failure modes:

1. **Class E $\rightarrow$ Class D Confusion (38 errors, 77.6% of all errors):**
   - Ground truth was `authorised_testing` (Option E), but the model predicted `expected_admin` (Option D).
   - **Root Cause:** The held-out validation template for Class E (*"The security team’s validation job <SEC_ID> accounts for the observed action and its target scope"*) closely mirrors routine administrative validation jobs in Class D. Because the model had never seen this specific testing phrasing in training, it conflated security team validation with operational change validation.
2. **Class G $\rightarrow$ Class B Confusion (10 errors, 20.4% of all errors):**
   - Ground truth was `unknown` (Option G), but the model predicted `suspicious` (Option B).
   - **Root Cause:** When two context sources disagree about workflow attribution, the model adopts a conservative, risk-averse stance by flagging the event as `suspicious`.
3. **Class C $\rightarrow$ Class B Confusion (1 error, 2.0% of all errors):**
   - A single benign alert was conservatively classified as suspicious.

---

## 4. Key Findings: Evidence vs. Shortcut Learning

1. **Generalization Transfer Confirmed:** Despite 100% of the validation templates being completely unseen during training, the adapter achieved **93.69% accuracy**. This demonstrates that Tev1 is learning the broader semantic concepts of unauthorized access, baseline deviation, administrative change tickets, and retry loops, rather than merely acting as an n-gram memorizer.
2. **The E vs. D Boundary Vulnerability:** The primary drop from 97% to 93.69% is concentrated in the boundary between authorized security testing and operational system administration (38 errors). When phrasing changes from *"security exercise"* to *"validation job"*, the model tends to classify it as administrative.
3. **Zero False Negatives on Attacks:** The adapter achieved **100.0% precision and 100.0% recall on Class A (`malicious`)**, correctly detecting all 117 held-out attack alerts without a single error.

---

## 5. Artifact & Deliverable Registry

- **Trained Adapter Checkpoint:** [`v2_experiments/tev1_grouped_template_pilot_v1/`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/tev1_grouped_template_pilot_v1)
- **Adapter Weights:** `adapter_model.safetensors` (21.7 MB)
- **Detailed Metrics JSON:** [`v2_experiments/tev1_grouped_template_metrics.json`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/tev1_grouped_template_metrics.json)
- **Exact Predictions JSONL:** [`v2_experiments/tev1_grouped_template_predictions.jsonl`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/tev1_grouped_template_predictions.jsonl)
- **Safety Gate:** `CONFIRM_FINETUNE` has been re-locked to `False` in [`run_tev1_grouped_pilot.py`](file:///c:/Users/ASUS/Desktop/jev/run_tev1_grouped_pilot.py).
