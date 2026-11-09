# Tev1 Fine-Tuning Project — Metric Integrity and Discrepancy Resolution Audit

**Project Directory:** `C:\Users\ASUS\Desktop\jev`  
**Execution Timestamp:** 2026-11-09  
**Status:** Complete & Fully Verified  

---

## Executive Summary

This audit recomputes, directly from the primary line-by-line prediction files (`*.jsonl`), all performance metrics across all four phases of evaluation in the Tev1 fine-tuning project:
1. **Unadapted Base Model** on OpenSec-Triage Validation Set (700 records)
2. **Pilot Adapter (Random Split / Leakage-Prone)** on Validation Set (700 records)
3. **Pilot Adapter Verification Clause Ablation Test** (700 records)
4. **Grouped-Template-Held-Out Pilot Adapter (Zero Template Overlap)** (777 records)

Every metric reported in this document is derived by direct execution against saved predictions. No metrics have been copied or carried forward without programmatic re-verification.

---

## 1. Master Recomputation & Verification Table

| Metric | Phase 1: Base Model (No LoRA) | Phase 2: Pilot Adapter (Random Split) | Phase 3: Pilot Adapter (Clause Ablation) | Phase 4: Grouped Pilot (0% Template Overlap) |
| :--- | :---: | :---: | :---: | :---: |
| **Prediction File** | `tev1_base_val_predictions.jsonl` | `tev1_qlora_pilot_val_predictions.jsonl` | `tev1_clause_ablation_predictions.jsonl` | `tev1_grouped_template_predictions.jsonl` |
| **Total Evaluation Samples** | 700 | 700 | 700 | **777** |
| **Correct Predictions** | 249 | 679 | 103 | **728** |
| **Incorrect Predictions** | 451 | 21 | 597 | **49** |
| **Invalid Format Count** | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | **0 (0.00%)** |
| **Accuracy** | **35.5714%** (35.57%) | **97.0000%** (97.00%) | **14.7143%** (14.71%) | **93.6937%** (**93.69%**) |
| **Macro Precision** | 45.5702% | 97.4169% | 7.3094% | **93.2039%** |
| **Macro Recall** | 35.5714% | 97.0000% | 14.7143% | **94.5023%** |
| **Macro F1 Score** | **30.7500%** | **97.0488%** | **5.0163%** | **92.8103%** (**92.81%**) |
| **Weighted F1 Score** | 30.7500% | 97.0488% | 5.0163% | **93.8271%** |

---

## 2. Recomputed Per-Class Metrics and Support

### Phase 1: Unadapted Base Model (`togethercomputer/Tev1-0.8B-experimental`)
*Dataset: `tev1_training_candidate/tev1_triage_candidate_val.jsonl` (700 samples, balanced 100/class)*

| Class Letter & Name | Support | Correct | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 100 | 32 | 54.24% | 32.00% | 40.25% |
| **B (`suspicious`)** | 100 | 72 | 20.00% | 72.00% | 31.30% |
| **C (`benign`)** | 100 | 66 | 56.41% | 66.00% | 60.83% |
| **D (`expected_admin`)** | 100 | 0 | 0.00% | 0.00% | 0.00% |
| **E (`authorised_testing`)** | 100 | 17 | 36.17% | 17.00% | 23.13% |
| **F (`misconfiguration`)** | 100 | 2 | 100.00% | 2.00% | 3.92% |
| **G (`unknown`)** | 100 | 60 | 52.17% | 60.00% | 55.81% |
| **Macro Average** | **700** | **249** | **45.57%** | **35.57%** | **30.75%** |

### Phase 2: Pilot Adapter (`v2_experiments/tev1_qlora_pilot_v1`)
*Dataset: `tev1_training_candidate/tev1_triage_candidate_val.jsonl` (700 samples, balanced 100/class, 100% template overlap)*

| Class Letter & Name | Support | Correct | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 100 | 100 | 100.00% | 100.00% | 100.00% |
| **B (`suspicious`)** | 100 | 99 | 83.90% | 99.00% | 90.83% |
| **C (`benign`)** | 100 | 89 | 100.00% | 89.00% | 94.18% |
| **D (`expected_admin`)** | 100 | 100 | 99.01% | 100.00% | 99.50% |
| **E (`authorised_testing`)** | 100 | 99 | 100.00% | 99.00% | 99.50% |
| **F (`misconfiguration`)** | 100 | 100 | 99.01% | 100.00% | 99.50% |
| **G (`unknown`)** | 100 | 92 | 100.00% | 92.00% | 95.83% |
| **Macro Average** | **700** | **679** | **97.42%** | **97.00%** | **97.05%** |

### Phase 3: Verification Clause Ablation Test
*Dataset: Ablated validation records with decisive clauses removed (700 samples)*

| Class Letter & Name | Support | Correct | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 100 | 5 | 20.00% | 5.00% | 8.00% |
| **B (`suspicious`)** | 100 | 97 | 14.50% | 97.00% | 25.23% |
| **C (`benign`)** | 100 | 0 | 0.00% | 0.00% | 0.00% |
| **D (`expected_admin`)** | 100 | 0 | 0.00% | 0.00% | 0.00% |
| **E (`authorised_testing`)** | 100 | 0 | 0.00% | 0.00% | 0.00% |
| **F (`misconfiguration`)** | 100 | 1 | 16.67% | 1.00% | 1.89% |
| **G (`unknown`)** | 100 | 0 | 0.00% | 0.00% | 0.00% |
| **Macro Average** | **700** | **103** | **7.31%** | **14.71%** | **5.02%** |

### Phase 4: Grouped Pilot Adapter (`v2_experiments/tev1_grouped_template_pilot_v1`)
*Dataset: `tev1_grouped_template_val.jsonl` (777 samples, held-out template families, 0% template overlap)*

| Class Letter & Name | Support | Correct | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A (`malicious`)** | 117 | 117 | 100.00% | 100.00% | 100.00% |
| **B (`suspicious`)** | 92 | 92 | 89.32% | 100.00% | 94.36% |
| **C (`benign`)** | 124 | 123 | 100.00% | 99.19% | 99.60% |
| **D (`expected_admin`)** | 65 | 65 | 63.11% | 100.00% | 77.38% |
| **E (`authorised_testing`)** | 126 | 88 | 100.00% | 69.84% | 82.24% |
| **F (`misconfiguration`)** | 120 | 120 | 100.00% | 100.00% | 100.00% |
| **G (`unknown`)** | 133 | 123 | 100.00% | 92.48% | 96.09% |
| **Macro Average** | **777** | **728** | **93.20%** | **94.50%** | **92.81%** |

---

## 3. Recomputed Confusion Matrices

### Base Model (No LoRA) — Row: Ground Truth, Column: Prediction
```
        A     B     C     D     E     F     G
  A    32    68     0     0     0     0     0
  B     0    72    21     0     0     0     7
  C     2    22    66     0     3     0     7
  D    14    30    16     0    26     0    14
  E    10    50     2     0    17     0    21
  F     1    79    12     0     0     2     6
  G     0    39     0     0     1     0    60
```

### Pilot Adapter (Random Split) — Row: Ground Truth, Column: Prediction
```
        A     B     C     D     E     F     G
  A   100     0     0     0     0     0     0
  B     0    99     0     0     0     1     0
  C     0    11    89     0     0     0     0
  D     0     0     0   100     0     0     0
  E     0     0     0     1    99     0     0
  F     0     0     0     0     0   100     0
  G     0     8     0     0     0     0    92
```

### Pilot Adapter (Ablation Test) — Row: Ground Truth, Column: Prediction
```
        A     B     C     D     E     F     G
  A     5    95     0     0     0     0     0
  B     2    97     0     0     0     1     0
  C     5    94     0     0     0     1     0
  D     2    95     0     0     0     3     0
  E     2    98     0     0     0     0     0
  F     6    93     0     0     0     1     0
  G     3    97     0     0     0     0     0
```

### Grouped Pilot Adapter (0% Overlap) — Row: Ground Truth, Column: Prediction
```
        A     B     C     D     E     F     G
  A   117     0     0     0     0     0     0
  B     0    92     0     0     0     0     0
  C     0     1   123     0     0     0     0
  D     0     0     0    65     0     0     0
  E     0     0     0    38    88     0     0
  F     0     0     0     0     0   120     0
  G     0    10     0     0     0     0   123
```

---

## 4. Resolution of Cross-Document Discrepancies

During this comprehensive audit, several discrepancies across previously generated markdown reports and conversation logs were identified and resolved:

### Discrepancy 1: Ablation Test Macro F1 (5.02% vs. 10.97%)
- **Source of Discrepancy:** The conversation context summary noted `falling to 14.71% after removing decisive verification evidence` with a passing reference to `10.97% macro F1`, whereas the primary result file `TEV1_CLAUSE_ABLATION_REPORT.md` and `tev1_clause_ablation_results.json` recorded `5.02% macro F1`.
- **Recomputation Finding:** The exact macro F1 recomputed directly from `v2_experiments/tev1_clause_ablation_predictions.jsonl` is **5.0163%** (5.02%).
- **Resolution:** The true metric is 5.02%. In an ablated evaluation where 669 out of 700 predictions defaulted to Class B, five classes (C, D, E, G) had zero true positives and zero precision/recall, yielding $F_1 = 0.0$ across 5 classes. Averaging over all 7 classes produces $(0.08 + 0.2523 + 0 + 0 + 0 + 0.0189 + 0) / 7 = 0.05016$ (5.02%). Any citation of 10.97% was an informal draft estimate; 5.02% is the verified empirical fact.

### Discrepancy 2: Base Model Macro F1 (30.75% vs. 30.14%)
- **Source of Discrepancy:** Certain summary text referred to the base model macro F1 as ~30.14%.
- **Recomputation Finding:** Direct calculation on `v2_experiments/tev1_base_val_predictions.jsonl` produces:
  - Accuracy: **35.5714%** (249 / 700)
  - Macro F1: **30.7500%**
  - Class D had 0 correct predictions ($F_1 = 0.0$), Class F had 2 correct predictions ($F_1 = 3.92\%$).
- **Resolution:** 30.75% is the canonical unrounded macro F1 for the base model.

### Discrepancy 3: Grouped Validation Class Support (Unbalanced vs. Balanced)
- **Source of Discrepancy:** The initial OpenSec-Triage validation split was artificially constructed with exactly 100 samples per class (700 total). The grouped template-held-out validation split contains **777 samples** with varying per-class support:
  - A: 117, B: 92, C: 124, D: 65, E: 126, F: 120, G: 133
- **Resolution:** As verified by `tev1_grouped_template_manifest.json` and `tev1_grouped_template_val.jsonl`, when holding out whole template families rather than random records, the split reflects natural cluster sizes. The reported weighted average F1 is **93.83%** and unweighted macro average F1 is **92.81%**.

---

## 5. Trainable Parameter Audit (5.41M vs. 10.85M)

### Audit Findings
- **Claim in early drafts / model cards:** "Trainable Parameters: 10,854,400 (10.85M)".
- **Measured value during training:** Both `run_tev1_pilot.py` and `run_tev1_grouped_pilot.py` logged:
  `trainable params: 5,411,328 || all params: 545,920,000 || trainable%: 0.9912`
- **Safetensors Inspection:**
  - `v2_experiments/tev1_qlora_pilot_v1/adapter_model.safetensors`: Exactly **5,411,328** parameters across 372 tensors.
  - `v2_experiments/tev1_grouped_template_pilot_v1/adapter_model.safetensors`: Exactly **5,411,328** parameters across 372 tensors.
- **Architectural Reason:**
  The base model `togethercomputer/Tev1-0.8B-experimental` possesses a hybrid linear-attention (delta-rule) and feedforward architecture across 24 layers. When targeting the 12 linear projection names (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, `out_proj`), some modules only exist in attention layers while others only exist in linear-attention delta layers. The total number of adapted linear layers across the network is 186.
  With rank $r=8$, the total trainable weight parameters sum to:
  $$\sum (d_{\text{in}} \times 8 + 8 \times d_{\text{out}}) = 5,411,328$$
- **Origin of 10.85M:** The 10.85M figure originated from a pre-experimental theoretical estimation that assumed standard dense Transformer layers (where all 12 modules would appear uniformly across all 24 layers at full hidden dimension $d=2048$).
- **Conclusion:** Both the initial pilot adapter and the grouped-template pilot adapter used **100% identical, equivalent LoRA configurations**: $r=8$, $\alpha=16$, dropout=0.05, 4-bit NF4 quantization, and exactly 5,411,328 trainable parameters. Neither experiment was under- or over-parameterized relative to the other.

---

## 6. Audit Verdict

All metrics in `v2_experiments/tev1_metric_integrity_audit.json` have been reconciled with primary prediction records. The evaluation framework, metric integrity, and experimental comparability are formally confirmed.
