# Tev1 Experiment Index & Artifact Registry

This document serves as the master registry of all experimental runs, evaluation benchmarks, JSON metric files, prediction logs, and model checkpoints generated during the Tev1 fine-tuning research project.

---

## 1. Master Experiment Table

| Experiment ID | Task / Phase | Model Configuration | Dataset / Evaluation Target | Key Metrics | Status | Supporting Artifact |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **EXP-001** | Gate 1 Baseline | Tev1-0.8B (Pure Base, 4-bit) | `val_split_v1.jsonl` (1,121 MCQs: WMDP + CyberMetric) | Acc: **61.73%**, F1: **62.12%**, Latency: **234.7 ms** | **PASSED** | `local_eval_results/tev1_baseline_val_metrics_v1.json` |
| **EXP-002** | Output Post-Processing | Regex Answer Normalizer | 11 Invalid Outputs from EXP-001 | 8 recovered (4 correct, 4 incorrect) | **COMPLETED** | `local_eval_results/error_analysis/tev1_postprocessing_metrics.json` |
| **EXP-003** | Position Bias Audit | Tev1-0.8B (Pure Base, 4-bit) | `val_split_v1.jsonl` (1,121 MCQs) | 42.4% Option A skew (matches 37.6% GT skew) | **COMPLETED** | `local_eval_results/error_analysis/TEV1_POSITION_BIAS_AUDIT.md` |
| **EXP-004** | QLoRA Smoke Test | Tev1-0.8B + LoRA (5 steps) | `data/OpenSec_Triage` sample (100 rows) | Loss: 4.88 $\rightarrow$ 3.12, Peak VRAM: 2.14 GB | **PASSED** | `run_candidate_smoke_test.py` |
| **EXP-005** | 50-Step Pilot Training | Tev1-0.8B + LoRA (12 target modules) | `tev1_triage_candidate_train.jsonl` (3,500 samples) | Train Loss: **0.8798**, Eval Loss: **0.8757**, Runtime: **1338s** | **PASSED** | `v2_experiments/tev1_qlora_pilot_v1/checkpoint-50/` |
| **EXP-006** | Pilot Adapter Validation | Tev1-0.8B + Pilot Adapter | `tev1_triage_candidate_val.jsonl` (700 samples) | Acc: **97.00%**, F1: **97.05%**, Invalid: **0.00%** | **PASSED** | `v2_experiments/tev1_qlora_pilot_val_metrics.json` |
| **EXP-007** | Controlled Base Comparison | Tev1-0.8B (Pure Base, Zero Adapter) | `tev1_triage_candidate_val.jsonl` (700 samples) | Acc: **35.57%**, F1: **30.75%**, Delta: **+61.43 pp** | **COMPLETED** | `v2_experiments/tev1_base_val_metrics.json` |
| **EXP-008** | Template Leakage Audit | Pairwise Structural Comparison | 3,500 Train vs. 700 Val Samples | Exact Dups: 0%, Clause Overlap: **100.0%** | **AUDITED** | `v2_experiments/tev1_generalization_audit.json` |
| **EXP-009** | Clause Ablation Experiment | Tev1-0.8B + Pilot Adapter | `tev1_triage_candidate_val_ablated.jsonl` (700 samples) | Acc: **14.71%**, F1: **5.02%**, Option B skew: **95.6%** | **COMPLETED** | `v2_experiments/tev1_clause_ablation_results.json` |
| **EXP-010** | Grouped Split Generation | Dataset Holdout Architecture | All 4,200 OpenSec Candidate Records | 3,423 Train / 777 Val, **0.0% Template Overlap** | **COMPLETED** | `tev1_grouped_template_manifest.json` |
| **EXP-011** | Grouped Pre-Flight Check | Dry-Run & Integrity Validator | `verify_grouped_preflight.py` & `verify_dry_run.py` | 7/7 Dataset checks passed, 4/4 Model checks passed | **PASSED** | `verify_grouped_preflight.py` |
| **EXP-012** | Grouped Pilot Training | Tev1-0.8B + Fresh LoRA (50 steps) | `tev1_grouped_template_train.jsonl` (3,423 samples) | Runtime: **735.8s**, Train Loss: **0.867**, Peak VRAM: **2.54 GB** | **PASSED** | `v2_experiments/tev1_grouped_template_pilot_v1/` |
| **EXP-013** | Grouped Pilot Validation | Tev1-0.8B + Grouped Adapter | `tev1_grouped_template_val.jsonl` (777 samples) | Acc: **93.69%**, F1: **92.81%**, Invalid: **0.00%**, Latency: **537.7 ms** | **PASSED** | `v2_experiments/tev1_grouped_template_metrics.json` |
| **EXP-014** | SecAlertBench Independent Eval | Base Model vs Grouped Adapter | `eval_independent/secalertbench_*.json` (200 samples) | Cond A Acc: **45.0% vs 61.5%**; FPR: **75.0% vs 26.0%**; Cond B TPR: **2.0% vs 4.0%** | **PASSED** | `v2_experiments/secalertbench_binary_comparison.json` |

---

## 2. Checkpoint & Artifact Registry

### Trained Model Checkpoints
1. **Initial Pilot Adapter (Random Split):**
   - **Directory:** `v2_experiments/tev1_qlora_pilot_v1/`
   - **Adapter Weights:** `adapter_model.safetensors` (21,700,560 bytes / ~21.7 MB)
   - **Target Modules:** 12 linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, etc.)
2. **Grouped Template Adapter (Held-Out Templates, 0% Overlap):**
   - **Directory:** `v2_experiments/tev1_grouped_template_pilot_v1/`
   - **Adapter Weights:** `adapter_model.safetensors` (21,700,560 bytes / ~21.7 MB)
   - **Configuration:** $r=8$, $\alpha=16$, 12 linear target modules.

### Primary Prediction Logs
- **Baseline MCQ Predictions:** `local_eval_results/tev1_gate1_predictions_exact.jsonl`
- **Pilot v1 Predictions (Random Val):** `v2_experiments/tev1_qlora_pilot_val_predictions.jsonl`
- **Base Model Predictions (Zero Adapter):** `v2_experiments/tev1_base_val_predictions.jsonl`
- **Head-to-Head Comparison Pair Log:** `v2_experiments/tev1_base_vs_adapter_predictions.jsonl`
- **Clause Ablation Predictions:** `v2_experiments/tev1_clause_ablation_predictions.jsonl`
- **Grouped Template Predictions (777 samples):** `v2_experiments/tev1_grouped_template_predictions.jsonl`

### Dataset Manifests
- **Random Candidate Corpus Manifest:** `tev1_training_candidate/manifest.json`
  - Train (3,500 samples): `1533e4aa812600e0ad951c708b1339d5a3456c5613564851550c48c5ecd31351`
  - Val (700 samples): `c9762034bf4854c4333e7a52cbde980e9fe88f680bbb7c6ec06f27818dd57a3d`
- **Grouped Template Split Manifest:** `tev1_grouped_template_manifest.json`
  - Train (3,423 samples): `0d3362f0b2a30021c6e349038832ab94ea955049b1d90b2ca59a5d63722b94f5`
    - Class counts: A: 483, B: 508, C: 476, D: 535, E: 474, F: 480, G: 467
  - Val (777 samples): `fa9d49da881df0f6462111bc6f259981ac781ac33e3f96b519fd9a1bd35bcd64`
    - Class counts: A: 117, B: 92, C: 124, D: 65, E: 126, F: 120, G: 133
  - Template Overlap: **0.0% (Zero shared template families)**.
