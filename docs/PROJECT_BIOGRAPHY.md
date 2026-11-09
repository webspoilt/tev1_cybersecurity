# Tev1 Cybersecurity Fine-Tuning: Comprehensive Project Biography & Chronicle

## Project Overview

- **Target Model:** `togethercomputer/Tev1-0.8B-experimental` (Hybrid Linear-Attention / Delta-Rule architecture).
- **Core Objective:** Fine-tune a compact, sub-1B parameter hybrid recurrent model on defensive cybersecurity decision-making (incident triage, SOC alert classification, administrative authorization) under zero-budget local constraints.
- **Hardware Platform:** Local NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB Dedicated VRAM, WDDM driver 566.07, CUDA 12.7 / PyTorch 2.6.0+cu124 on Windows 11).
- **Project Boundary & Independence:** This project is strictly separate from the Bounty Hunter project (which operates on a separate machine). No code, data, adapters, or benchmarks are co-mingled.

---

## 1. Chronological Timeline & Milestones

### November 8, 2026: Foundation & Gate 1 Baseline
- **Gate 0 Environment Setup:** Python 3.11 virtual environment configured at `.venv_local_eval`. PyTorch 2.6.0+cu124 installed with CUDA acceleration.
- **Architecture Validation:** Verified that Tev1-0.8B requires 12 specific linear projection target modules across its recurrent and self-attention hybrid layers: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `in_proj_qkv`, `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj`.
- **Gate 1 Baseline Evaluation:** Evaluated un-tuned `togethercomputer/Tev1-0.8B-experimental` on 1,121 held-out canonical cybersecurity benchmark records (`val_split_v1.jsonl`, consisting of 199 WMDP-Cyber records and 922 CyberMetric-10000 records).
  - Overall Accuracy: **61.73%** (692 / 1,121).
  - Macro F1: **62.12%**.
  - Invalid Output Rate: **0.98%** (11 / 1,121).
  - Peak Dedicated VRAM: **1.22 GB**.
  - Average Latency: **234.7 ms / sample**.
  - Comparison: Outperformed Qwen3.5-0.8B-Base (58.97% Acc, 573.9 ms latency) by +2.76% accuracy and 2.4x inference speed.
- **Error Analysis & Bias Audit:**
  - Audited the 418 baseline errors (`TEV1_GATE1_ERROR_ANALYSIS.md`).
  - Implemented conservative post-processing prefix recovery (`TEV1_POSTPROCESSING_EXPERIMENT.md`), successfully recovering 8 of 11 malformed outputs without hallucinating labels.
  - Investigated answer-position bias (`TEV1_POSITION_BIAS_AUDIT.md`), discovering a 37.6% skew toward Option A in ground truth and a 42.4% prediction preference.

### November 9, 2026 (Morning): Candidate Dataset Discoveries & Audits
- **Strategic Policy Lock:** Quarantined WMDP-Cyber and CyberMetric-10000 strictly for held-out evaluation. Mandated zero label fabrication and authentic defensive data search.
- **Investigation 1 — Trendyol Cybersecurity Instruction Dataset (53,202 rows):**
  - Downloaded to `data/Trendyol`.
  - Conducted 300-record stratified audit (`TRENDYOL_FINAL_AUDIT.md`).
  - **Result: REJECTED.** 100% of rows were multi-paragraph conceptual essays (~276 words/response) without tactical decision choices, incident triage options, or structured alerts.
- **Investigation 2 — LANL Cyber1 Event Dataset (1.64B events):**
  - Sampled authentication logs and red-team ground truth (`LANL_CYBER1_INSPECTION_REPORT.md`).
  - **Result: REJECTED for direct instruction-tuning.** Anonymized tabular authentication strings without textual telemetry or tactical defensive decision options.
- **Investigation 3 — OpenSec-Triage (`tegridydev/opensec-triage`, 50,000 alerts):**
  - Audited upstream dataset under CC BY 4.0 (`OPENSEC_TRIAGE_FINAL_AUDIT.md`).
  - Verified balanced 7-class triage ground truth: `malicious`, `suspicious`, `benign`, `expected_admin`, `authorised_testing`, `misconfiguration`, `unknown`.
  - Staged balanced candidate corpus: 3,500 training records (500/class) and 700 validation records (100/class) with SHA-256 manifest locking.

### November 9, 2026 (Mid-Day): QLoRA Pilot Run & Controlled Comparison
- **Gate 2 Verification & Safety Safeguard:** Implemented `CONFIRM_FINETUNE` safety switch in `run_tev1_pilot.py`. Re-verified manifest hashes.
- **50-Step QLoRA Pilot Execution:**
  - Ran 50 optimizer steps (effective batch size 16, 800 training exposures) using `paged_adamw_8bit`, cosine schedule (max LR $2 \times 10^{-4}$), and 4-bit NF4 double quantization on RTX 3050 Laptop GPU.
  - Runtime: 1338.3s (~22.3 min). Train loss steadily converged from 4.332 to **0.8798**; validation loss reached **0.8757**.
  - Checkpoint saved to `v2_experiments/tev1_qlora_pilot_v1`.
- **Validation Evaluation:** Evaluated the pilot adapter across the 700 OpenSec-Triage validation records.
  - Accuracy: **97.00%** (679 / 700). Macro F1: **97.05%**. Invalid Rate: **0.00%**.
- **Controlled Base vs. Pilot Comparison (`TEV1_BASE_VS_ADAPTER_REPORT.md`):**
  - Evaluated pure base model (no adapter) under identical parameters.
  - Base Model Accuracy: **35.57%** (severe blind spots on `expected_admin` [0% recall] and `misconfiguration` [2% recall], with 51.4% bias toward Option B).
  - Pilot Adapter Delta: **+61.43 percentage points accuracy** and **+66.30 percentage points Macro F1**. Recovered 436 base model errors while regressing on only 6.

### November 9, 2026 (Afternoon): Rigorous Evaluation Integrity & Ablation Audits
- **Generalization & Integrity Audit (`TEV1_GENERALIZATION_AUDIT.md`):**
  - Conducted full pairwise lexical and structural audit across all 3,500 train and 700 val records.
  - Discovered that while exact duplicates were 0%, **100% of validation records shared identical trailing verification clauses** drawn from a closed pool of ~14–15 fixed templates per class in the upstream synthetic generator.
  - Corrected error taxonomy: 19 of 21 errors (90.5%) were conservative risk-averse shifts; 2 errors (9.5%) were non-conservative misclassifications.
  - Resolved latency measurement: True warm inference is **441.5 ms (Base)** vs. **575.0 ms (Pilot)**; initial 1,830 ms was an un-warmed JIT initialization artifact.
  - Verdict issued: **`POSSIBLE TEMPLATE LEAKAGE`**.
- **Verification Clause Ablation Test (`TEV1_CLAUSE_ABLATION_REPORT.md`):**
  - Removed trailing verification sentences (sentences 5–6), preserving all raw telemetry (sentences 0–4).
  - Accuracy collapsed from **97.00%** to **14.71%**, with the model predicting Option B (`suspicious`) on 95.6% of records.
  - Proved that the verification clauses contained 100% of the decisive investigative evidence, as raw telemetry was identical across conflicting classes for 149 scenarios.
- **Grouped Template-Held-Out Split (`TEV1_GROUPED_TEMPLATE_AUDIT.md`):**
  - Grouped all 4,200 records into 35 semantic template families (5 per class).
  - Constructed a strict 4:1 holdout split: 3,423 train records (4 families/class) and 777 val records (1 held-out family/class) with **0.0% template overlap**.
  - Final Verdict: OpenSec-Triage has insufficient template diversity (only 5 archetypes per class) to prove general reasoning. Recommended transitioning to naturalistic datasets (Splunk BOTS, CIC-IDS).

---

## 2. Technical Architecture & Hardware Configuration

### Model Details
- **Base Model:** `togethercomputer/Tev1-0.8B-experimental`
- **Total Parameters:** ~545.92 Million
- **Trainable LoRA Parameters:** 5,411,328 (0.99% of total across 186 linear projection adapter modules)
- **Quantization:** 4-bit NormalFloat4 (NF4) with Double Quantization via `bitsandbytes`
- **Compute Dtype:** `torch.float16`
- **LoRA Configuration:** $r=8$, $\alpha=16$, dropout=0.05, target modules: 12 linear projections.

### Hardware Footprint on Local RTX 3050 Laptop GPU (4 GB VRAM)
- **Base Model Static VRAM:** ~855 MB dedicated.
- **Pilot Adapter Forward Pass:** ~904 MB dedicated.
- **Training Peak VRAM:** ~2.48 GB dedicated VRAM (with OS shared memory absorption during backward pass; no CUDA OOM).
- **Inference Latency:** 441.5 ms/call (Base), 575.0 ms/call (Adapter) under reference PyTorch fallback for delta-rule layers.
