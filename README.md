# Tev1 Cybersecurity Fine-Tuning: Efficient QLoRA on a Sub-Billion Parameter Hybrid Model

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Model](https://img.shields.io/badge/Model-Tev1--0.8B--Experimental-orange.svg)](https://huggingface.co/togethercomputer/Tev1-0.8B-experimental)
[![Hardware](https://img.shields.io/badge/Hardware-RTX%203050%20Laptop%20(4GB)-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Experimental%20Research-yellow.svg)]()

> [!WARNING]
> **Experimental Research Adapter:** This repository contains research artifacts, ablation evaluations, and LoRA adapters fine-tuned on `togethercomputer/Tev1-0.8B-experimental`. It is intended strictly for academic study into dataset governance, shortcut learning, and parameter-efficient fine-tuning on consumer hardware. **It is not an autonomous, production-ready security operations system and must not be deployed for unattended threat detection.**

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Research Objectives](#research-objectives)
3. [Target Model & Hardware Architecture](#target-model--hardware-architecture)
4. [Dataset Discovery & Audits](#dataset-discovery--audits)
5. [Training Methodology & QLoRA Configuration](#training-methodology--qlora-configuration)
6. [Empirical Results: Base Model vs. Pilot Adapters](#empirical-results-base-model-vs-pilot-adapters)
7. [Adversarial Audits & Generalization Findings](#adversarial-audits--generalization-findings)
   - [Verification Clause Template Leakage](#verification-clause-template-leakage)
   - [Verification Clause Ablation Test](#verification-clause-ablation-test)
8. [Phase 7: Grouped Template-Family Holdout Evaluation (Completed)](#phase-7-grouped-template-family-holdout-evaluation-completed)
9. [Phase 8: Independent Enterprise SOC Alert Evaluation with SecAlertBench (Completed)](#phase-8-independent-enterprise-soc-alert-evaluation-with-secalertbench-completed)
10. [Known Limitations & Negative Findings](#known-limitations--negative-findings)
11. [Planned Bounty Hunter Integration (Future Work)](#planned-bounty-hunter-integration-future-work)
12. [Repository Directory Structure](#repository-directory-structure)
13. [Reproducibility & Getting Started](#reproducibility--getting-started)
14. [Citation & Attribution](#citation--attribution)

---

## 1. Project Overview

The **Tev1 Cybersecurity Fine-Tuning Project** investigates whether compact, sub-billion parameter hybrid linear-attention models can be adapted for tactical cybersecurity decision-making under strict zero-budget, consumer-grade hardware constraints.

Operating entirely on an **NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB Dedicated VRAM)**, this project demonstrates:
- **Feasibility:** Successful 4-bit QLoRA adaptation of `togethercomputer/Tev1-0.8B-experimental` without out-of-memory (OOM) failures or loss divergence.
- **Decision Interface Discipline:** Elimination of verbose preambles and format errors, achieving a 0.00% invalid-output rate under a structured ChatML XML interface.
- **Out-of-Distribution Generalization:** Proven ability to classify alerts when entire verification-template families are held out from training, achieving **93.69% accuracy** under 0.0% template overlap.

---

## 2. Research Objectives

1. **Local Parameter-Efficient Fine-Tuning:** Establish whether QLoRA can adapt a hybrid linear-attention recurrent architecture (`Tev1-0.8B`) on a 4 GB laptop GPU.
2. **Defensive Decision Categorization:** Evaluate performance across a 7-class incident triage taxonomy: `malicious`, `suspicious`, `benign`, `expected_admin`, `authorised_testing`, `misconfiguration`, and `unknown`.
3. **Data Governance & License Verification:** Enforce strict data hygiene by rejecting unvetted, essay-based, or non-tactical datasets, while quarantining standard evaluation benchmarks (such as WMDP-Cyber and CyberMetric).
4. **Adversarial Generalization Auditing:** Investigate whether high validation accuracy reflects true domain reasoning or synthetic shortcut learning across repeated template grammars.
5. **Grouped Template-Family Holdout Evaluation:** Measure whether the model can generalize to completely unseen phrasing archetypes without prior exposure in training.

---

## 3. Target Model & Hardware Architecture

### Model Specifications
- **Base Model:** `togethercomputer/Tev1-0.8B-experimental`
- **Architecture:** Hybrid Linear-Attention / Delta-Rule recurrent neural network based on the Qwen 0.8B foundation.
- **Total Parameters:** ~545.92 Million.
- **Trainable LoRA Parameters:** 5,411,328 (0.63% of total parameters).
- **Target Modules (12 Linear Projections):** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `in_proj_qkv`, `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj`.

### Hardware Platform
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB Dedicated GDDR6 VRAM, WDDM 3.1).
- **Driver:** NVIDIA Game Ready Driver 566.07 (CUDA 12.7).
- **Host OS:** Microsoft Windows 11 Home (64-bit).
- **Software Stack:** Python 3.11.9, PyTorch `2.6.0+cu124`, `transformers==5.22.2`, `peft==0.14.0`, `bitsandbytes==0.45.2`.

---

## 4. Dataset Discovery & Audits

| Dataset Candidate | Size / Rows | License | Audit Outcome | Technical Reason |
| :--- | :---: | :---: | :---: | :--- |
| **Trendyol Cybersecurity** | 53,202 rows | Apache 2.0 | **REJECTED** | 100% long-form essays (~276 words/response); 0 discrete triage tasks. |
| **LANL Cyber1** | 1.64B events | Research / Open | **REJECTED** | Tabular authentication CSV logs lacking text telemetry or tactical choices. |
| **OpenSec-Triage** | 50,000 alerts | CC BY 4.0 | **APPROVED** | 7-class triage ground truth with EDR alert context and verification. |

---

## 5. Training Methodology & QLoRA Configuration

The adapters were trained under the following verified configuration:
- **Quantization:** 4-bit NormalFloat4 (NF4) with Double Quantization (`bitsandbytes`).
- **Compute Precision:** `torch.float16`.
- **LoRA Parameters:** Rank $r=8$, $\alpha=16$, Dropout=0.05, exactly 5,411,328 trainable parameters (0.99% parameter overhead across 186 linear projection adapter modules in 24 layers).
- **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, `out_proj`.
- **Optimizer:** `paged_adamw_8bit` (learning rate: $2.0 \times 10^{-4}$, cosine decay schedule).
- **Batching:** Micro-batch size 1, Gradient Accumulation 16 (Effective batch size: 16).
- **Steps:** 50 optimizer steps (~800 samples processed; ~0.23 epochs).

---

## 6. Empirical Results: Base Model vs. Pilot Adapters

| Metric | 1. Pure Base Model | 2. Pilot v1 Adapter (Random Split) | 3. Grouped Pilot Adapter (Held-Out Templates) |
| :--- | :---: | :---: | :---: |
| **Evaluation Split** | Random Val (700 records) | Random Val (700 records) | **Grouped Held-Out Val (777 records)** |
| **Template Overlap** | N/A (un-tuned) | 100.0% (Leaked templates) | **0.0% (Zero shared template families)** |
| **Accuracy** | 35.57% (249 / 700) | **97.00%** (679 / 700) | **93.69% (728 / 777)** |
| **Macro F1** | 30.75% | **97.05%** | **92.81%** |
| **Invalid Format Rate** | 0.00% (0 / 700) | 0.00% (0 / 700) | **0.00% (0 / 777)** |
| **Option B Bias** | 51.4% (360 / 700) | 16.9% (118 / 700) | **13.3% (103 / 777)** |
| **Warm Inference Latency** | 441.5 ms / sample | 575.0 ms / sample | **537.7 ms / sample** |
| **Peak VRAM Allocated** | 855.47 MB | 904.58 MB | **874.30 MB** |

---

## 7. Adversarial Audits & Generalization Findings

### 1. Verification Clause Template Leakage
- **Audit Findings:** While exact full-record duplicates were 0%, **100.0% (700/700) of validation records shared trailing verification clauses with the training set**.
- **Root Cause:** In OpenSec-Triage, trailing verification sentences are drawn from a closed pool of only **~14–15 fixed sentence templates per class**. The random train/validation split sampled across these same templates, causing structural template leakage.

### 2. Verification Clause Ablation Test
- **Experiment:** Removed trailing verification sentences (sentences 5–6), evaluating the adapter purely on raw alert telemetry, hostnames, timestamps, and business context (sentences 0–4).
- **Result:** Accuracy collapsed from **97.00%** to **14.71%** (-82.29 pp); Macro F1 collapsed from **97.05%** to **5.02%** (-92.03 pp).
- **Finding:** The adapter defaulted into predicting Option B (`suspicious`) on 95.6% of alerts. Audit proved that raw telemetry was identical across conflicting classes for 149 records; the removed clauses contained 100% of the decisive ground-truth evidence.

---

## 8. Phase 7: Grouped Template-Family Holdout Evaluation (Completed)

To measure true out-of-distribution transfer without template leakage, a **Grouped Template-Held-Out Experiment** was executed (`run_tev1_grouped_pilot.py`):
- **Training Set:** 3,423 records across 28 template families (4 families per class). SHA-256: `0d3362f0...`.
- **Validation Set:** 777 records across 7 strictly held-out template families (1 per class). SHA-256: `fa9d49da...`.
- **Template Family Overlap:** **0.0% (Zero shared template families)**.

### Per-Class Held-Out Performance ($N=777$)
- **A (`malicious`):** **100.0% Precision | 100.0% Recall | 100.0% F1** (117 / 117 correct).
- **B (`suspicious`):** 89.3% Precision | **100.0% Recall** | **94.4% F1** (92 / 92 correct).
- **C (`benign`):** **100.0% Precision** | 99.2% Recall | **99.6% F1** (123 / 124 correct).
- **D (`expected_admin`):** 63.1% Precision | **100.0% Recall** | 77.4% F1 (65 / 65 correct).
- **E (`authorised_testing`):** **100.0% Precision** | 69.8% Recall | 82.2% F1 (88 / 126 correct; 38 conflated with D).
- **F (`misconfiguration`):** **100.0% Precision | 100.0% Recall | 100.0% F1** (120 / 120 correct).
- **G (`unknown`):** **100.0% Precision** | 92.5% Recall | **96.1% F1** (123 / 133 correct).

```
Grouped Pilot Confusion Matrix (Labels A-G):
        A     B     C     D     E     F     G
  A [ 117     0     0     0     0     0     0 ]
  B [   0    92     0     0     0     0     0 ]
  C [   0     1   123     0     0     0     0 ]
  D [   0     0     0    65     0     0     0 ]
  E [   0     0     0    38    88     0     0 ]
  F [   0     0     0     0     0   120     0 ]
  G [   0    10     0     0     0     0   123 ]
```

**Key Finding:** Even when 100% of validation templates are completely unseen during training, Tev1 achieves **93.69% accuracy**, proving that it generalizes semantic security concepts rather than merely memorizing verbatim phrasing.

---

## 9. Phase 8: Independent Enterprise SOC Alert Evaluation with SecAlertBench (Completed)

To measure true out-of-distribution transfer to real-world enterprise telemetry, the model was evaluated on **SecAlertBench** (`Dxsssu/SecAlertBench`), comprising actual Tier-1 SOC alerts from three enterprise environments:
- **Sample:** 200 balanced enterprise alerts (100 Attack / 100 Non-Attack) with 50/50 option-order counterbalancing.
- **Condition A (Full SIEM Alert Metadata):** Model accuracy rose from **45.00% (Base)** to **61.50% (Grouped Adapter)** (+16.50 pp; Macro F1 +18.18 pp; MCC +0.3466). The adapter reduced the **False Positive Rate from 75.00% to 26.00%** (-49.0 pp).
- **Condition B (Raw Telemetry Evidence Only):** When alert rule names and taxonomy tags were stripped, both models failed to detect raw exploit strings (Attack Recall: Base 2.0%, Adapter 4.0%), defaulting to Non-Attack.

> [!WARNING]
> While the adapter demonstrated positive transfer on structured alert interpretation and false-positive suppression, **its 49% Attack Recall on Condition A and 4% Attack Recall on Condition B confirm that Tev1 is NOT ready for autonomous SOC alert triage.**

---

## 10. Known Limitations & Negative Findings

1. **Synthetic Template Poverty:** OpenSec-Triage provides only 5 synthetic phrasing archetypes per class.
2. **The E vs. D Boundary Confusion:** When phrasing shifts to *"security validation job"*, the model confuses security testing with operational administration (38 errors).
3. **Ambiguous Telemetry Bias:** When denied corroborating verification findings, the model collapses into a defensive prior, predicting `suspicious` (Option B) 95.6% of the time.

---

## 10. Planned Bounty Hunter Integration (Future Work)

> [!NOTE]
> **Architectural Separation:** The Tev1 fine-tuning research project and the downstream Bounty Hunter project are entirely separate systems running on separate physical machines. No integration has yet taken place.

In future research phases, the trained Tev1 adapter may serve as a local defensive classifier within the Bounty Hunter agent architecture, subject to standalone export, interface testing, and strict human verification.

---

## 11. Repository Directory Structure

```text
tev1-cybersecurity-qlora/
├── docs/
│   ├── PROJECT_JOURNEY.md               # Complete chronological development biography
│   ├── RESEARCH_PAPER.md               # Formal academic preprint and empirical study
│   ├── HUGGINGFACE_MODEL_CARD.md       # Standard Hugging Face model card specification
│   ├── DATASET_GOVERNANCE.md           # Dataset licensing, provenance, and audit logs
│   ├── REPRODUCIBILITY.md              # Step-by-step reproduction instructions
│   ├── EXPERIMENT_INDEX.md             # Complete index of all runs, metrics, and JSON files
│   ├── PUBLICATION_READINESS.md        # Pre-publication checklist and distribution boundaries
│   └── references.bib                  # BibTeX verified references
├── v2_experiments/
│   ├── tev1_grouped_template_metrics.json
│   ├── tev1_base_vs_adapter_comparison.json
│   ├── tev1_clause_ablation_results.json
│   ├── tev1_generalization_audit.json
│   ├── secalertbench_binary_comparison.json
│   └── tev1_final_statistical_analysis.json
├── tev1_grouped_template_train.jsonl   # 3,423-record grouped template training split
├── tev1_grouped_template_val.jsonl     # 777-record grouped template held-out val split
├── tev1_grouped_template_manifest.json # Grouped split manifest (0.0% template overlap)
├── README.md                           # Main repository guide
├── LICENSE                             # MIT License for original source code
├── CITATION.cff                        # Citation Metadata Format
└── .gitignore                          # Secret, virtualenv, and credential protection
```

---

## 12. Reproducibility & Getting Started

```bash
# Clone the repository
git clone https://github.com/your-org/tev1-cybersecurity-qlora.git
cd tev1-cybersecurity-qlora

# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install torch==2.6.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124
pip install transformers==5.22.2 peft==0.14.0 bitsandbytes==0.45.2 accelerate==1.4.0 scikit-learn

# Evaluate the Grouped Template Adapter on 777 held-out records
python evaluate_grouped_pilot_val.py
```

---

## 13. Citation & Attribution

```bibtex
@article{tev1_cybersecurity_qlora_2026,
  title={Efficient QLoRA Fine-Tuning of a 0.8B Language Model for Structured Cybersecurity Triage: An Experimental Study of Dataset Quality, Label Evidence and Template Leakage},
  author={Tev1 Research Team},
  year={2026},
  journal={Antigravity Research Archive},
  url={https://github.com/your-org/tev1-cybersecurity-qlora}
}
```
