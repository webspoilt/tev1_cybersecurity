# OpenSec-Triage Dataset Verification & Tev1 QLoRA Training Audit

**Target Model:** `togethercomputer/Tev1-0.8B-experimental`  
**Dataset Under Audit:** `tegridydev/opensec-triage` (Release 0.5.0)  
**Execution Platform:** Local NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB VRAM)  
**Audit Date:** November 9, 2026  
**Final Verdict:** **APPROVED CANDIDATE FOR TEV1 QLORA PILOT**  

---

## 1. Phase 1 — Dataset Verification & Provenance

### 1.1 Source & Licensing Terms
- **Repository:** [`https://huggingface.co/datasets/tegridydev/opensec-triage`](https://huggingface.co/datasets/tegridydev/opensec-triage)
- **License:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**
  - *Model Training:* **PERMITTED**
  - *Commercial & Non-Commercial Use:* **PERMITTED**
  - *Redistribution of Derived Works:* **PERMITTED**
  - *Attribution Obligation:* Standard credit to TegridyDev.
- **Composition & Data Nature:** Authored synthetic English security alert scenarios built across 10,000 counterfactual groups. Each group pairs an observable security event (DNS update, Kubernetes Secret read, OAuth consent grant) with specific verification evidence.
- **Ground-Truth Labeling Mechanism:** Ground truth is strictly established by deterministic evidence rules:
  - `malicious`: Requires correlated unauthorized compromise evidence (threat intel, lateral movement).
  - `suspicious`: Unexplained deviation without confirmed compromise.
  - `benign`: Routine business baseline match.
  - `expected_admin`: Valid change ticket covering the exact time, asset, and operator.
  - `authorised_testing`: Active security assessment approval covering scope.
  - `misconfiguration`: Reproduced configuration fault explaining the event.
  - `unknown`: Missing or conflicting evidence.

### 1.2 Quantitative Audit & Split Verification
- **Total Rows:** Exactly **50,000 records**
  - **Train:** 40,000 records
  - **Validation:** 5,000 records
  - **Test:** 5,000 records
- **Class Distribution in Train Split:** Perfectly balanced across all 7 classes:
  - `suspicious`: 5,719 (14.30%)
  - `misconfiguration`: 5,718 (14.29%)
  - `authorised_testing`: 5,716 (14.29%)
  - `benign`: 5,716 (14.29%)
  - `malicious`: 5,711 (14.28%)
  - `expected_admin`: 5,710 (14.27%)
  - `unknown`: 5,710 (14.27%)
- **Data Quality:**
  - Duplicate texts in train split: **0** (100% unique)
  - Train-to-Validation text overlap / leakage: **0** (Family profiles and groups are disjoint across splits)
  - Missing fields: **0**

---

## 2. Phase 2 — Tev1 Decision Compatibility Audit

### 2.1 300-Sample Stratified Inspection
300 records sampled uniformly across the dataset were evaluated:
- **Observable Security Action:** **300 / 300 (100.0%)** contain specific telemetry actions.
- **Business / Environmental Context:** **300 / 300 (100.0%)** contain department, environment, and shift timing context.
- **Verification Evidence Clause:** **287 / 300 (95.67%)** provide explicit follow-up evidence (e.g. ticket validation, config replay, intruder link).
- **Word Length Distribution:** Average **70.7 words** (Min: 61 words, Max: 80 words). Ideal context length for compact LLM inference.

### 2.2 Decision Interface Mapping Recommendation
Tev1's baseline interface emits a single option letter (`A`, `B`, `C`, etc.).
- **Why Arbitrary 4-Class Merging is Rejected:** Merging 7 classes down to 4 (e.g. forcing `misconfiguration` into `benign` or `expected_admin` into `unknown`) would destroy critical operational SOC distinctions.
- **Recommended 7-Option Interface:** Tev1 supports full lettered multiple-choice options (`A` through `G`):
  - `A) malicious`
  - `B) suspicious`
  - `C) benign`
  - `D) expected_admin`
  - `E) authorised_testing`
  - `F) misconfiguration`
  - `G) unknown`
- This preserves 100% of the ground truth without label fabrication.

---

## 3. Phase 3 — Candidate Dataset Generation

A clean, non-contaminated candidate dataset has been generated in [`tev1_training_candidate/`](file:///C:/Users/ASUS/Desktop/jev/tev1_training_candidate):
- **Raw Source Preservation:** Raw files preserved unchanged in `data/OpenSec_Triage/`.
- **Candidate Train Split:** **3,500 records** (exactly 500 per class, balanced).
  - SHA-256: `1533e4aa812600e0ad951c708b1339d5a3456c5613564851550c48c5ecd31351`
- **Candidate Validation Split:** **700 records** (exactly 100 per class, balanced).
  - SHA-256: `c9762034bf4854c4333e7a52cbde980e9fe88f680bbb7c6ec06f27818dd57a3d`
- **Zero Contamination:** Zero WMDP-Cyber records. Zero CyberMetric records.
- **Manifest:** Formally recorded in [`tev1_training_candidate/manifest.json`](file:///C:/Users/ASUS/Desktop/jev/tev1_training_candidate/manifest.json).

---

## 4. Phase 4 — Local RTX 3050 QLoRA Smoke Test

A 5-step QLoRA smoke test was executed on your RTX 3050 GPU using the candidate dataset:
- **Model:** `togethercomputer/Tev1-0.8B-experimental` (4-bit NF4)
- **Trainable Targets:** All 12 LoRA linear projections (`r=8, alpha=16`)
- **Optimizer:** `paged_adamw_8bit` with gradient checkpointing
- **Smoke Test Results:**
  - Status: **PASSED (11.4s)**
  - Loss Trajectory: Decreased steadily from **4.430 $\to$ 4.377 $\to$ 4.336 $\to$ 4.310 $\to$ 4.293**
  - Peak VRAM Consumed: **2.48 GB / 4.00 GB**
  - VRAM Headroom: **1.52 GB free** (safe from CUDA OOM)
  - Smoke artifacts cleaned; baseline model and Gate 0 adapter remain untouched.

---

## 5. Phase 5 — Final Decision & Gate Status

### Final Verdict: **APPROVED CANDIDATE (GO)**
- **Reason:** The dataset satisfies all provenance, licensing (CC BY 4.0), label authenticity, balance, and hardware constraints. It trains genuine defensive triage decision-making without fabricating labels.
- **Safety Lock:** **`CONFIRM_FINETUNE = False` remains strictly active**. No full training run will execute without your explicit authorization.
