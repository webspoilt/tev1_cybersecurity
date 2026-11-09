# Tev1 Reproducibility Guide & Experimental Runbook

## Overview

This guide provides end-to-end instructions for reproducing the baseline evaluations, dataset audits, 4-bit QLoRA fine-tuning, controlled comparisons, and generalization audits conducted during the Tev1 fine-tuning research project.

All experiments were executed on an entry-level consumer laptop:
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB Dedicated GDDR6 VRAM, WDDM 3.1).
- **Driver:** NVIDIA Driver 566.07 (DirectX 12 / CUDA 12.7).
- **OS:** Microsoft Windows 11 Home (64-bit).

---

## 1. System Environment Setup

### Prerequisites
- Python 3.11.9 (64-bit) (Python 3.13 is strictly discouraged due to C++ wheel build issues).
- Git.
- 15 GB of free local disk space for model cache and virtual environments.

### Environment Installation
```bash
# Clone the project repository
git clone https://github.com/your-org/tev1-cybersecurity-qlora.git
cd tev1-cybersecurity-qlora

# Create isolated Python 3.11 virtual environment
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate

# Install exact pinned dependencies with CUDA 12.4 pre-built wheels
pip install torch==2.6.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124
pip install transformers==5.22.2 peft==0.14.0 bitsandbytes==0.45.2 accelerate==1.4.0 datasets==3.2.0 scikit-learn==1.6.1
```

### Environment Verification
Run the following inline verification to confirm CUDA acceleration:
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0), '| VRAM:', round(torch.cuda.get_device_properties(0).total_memory/1024**3, 2), 'GB')"
```
Expected output:
```
CUDA Available: True | Device: NVIDIA GeForce RTX 3050 Laptop GPU | VRAM: 4.0 GB
```

---

## 2. Dataset Reproduction & Hash Verification

The candidate training and validation datasets derive from `tegridydev/opensec-triage` under CC BY 4.0. To verify bit-for-bit file integrity against the project manifest:

```python
import hashlib, json

manifest = json.load(open("tev1_training_candidate/manifest.json"))
for split, meta in manifest["files"].items():
    h = hashlib.sha256(open(meta["path"], "rb").read()).hexdigest()
    assert h == meta["sha256"], f"Hash mismatch in {split}: expected {meta['sha256']}, got {h}"
    print(f"[PASS] {split} ({meta['path']}): {h}")
```

Expected Hashes:
- `tev1_triage_candidate_train.jsonl` (3,500 samples): `1533e4aa812600e0ad951c708b1339d5a3456c5613564851550c48c5ecd31351`
- `tev1_triage_candidate_val.jsonl` (700 samples): `c9762034bf4854c4333e7a52cbde980e9fe88f680bbb7c6ec06f27818dd57a3d`

---

## 3. Running Baseline Evaluation (Zero Adapter)

To evaluate the un-tuned base model `togethercomputer/Tev1-0.8B-experimental` on the 700 validation samples:

```bash
python run_base_val_eval.py
```
- Outputs metrics to: `v2_experiments/tev1_base_val_metrics.json`
- Outputs predictions to: `v2_experiments/tev1_base_val_predictions.jsonl`
- Expected Accuracy: **35.57%** (249 / 700 correct)
- Expected Macro F1: **30.75%**

---

## 4. Running the 50-Step QLoRA Pilot Training

The training runner contains a safety gate (`CONFIRM_FINETUNE`) to prevent accidental GPU execution:
1. Open `run_tev1_pilot.py`.
2. Locate line 28: `CONFIRM_FINETUNE = False`.
3. Set `CONFIRM_FINETUNE = True` (or run with authorized approval).
4. Launch the training runner:
```bash
python run_tev1_pilot.py
```
- **Runtime:** ~22.3 minutes on RTX 3050.
- **VRAM Consumption:** Peak ~2.48 GB allocated.
- **Output Checkpoint:** Saved to `v2_experiments/tev1_qlora_pilot_v1/`.

---

## 5. Evaluating the Pilot Adapter

To evaluate the trained pilot adapter across the 700 validation records:
```bash
python evaluate_pilot_val.py
```
- Outputs metrics to: `v2_experiments/tev1_qlora_pilot_val_metrics.json`
- Outputs predictions to: `v2_experiments/tev1_qlora_pilot_val_predictions.jsonl`
- Expected Accuracy: **97.00%** (679 / 700 correct)
- Expected Macro F1: **97.05%**
- Expected Format Error Rate: **0.00%**

---

## 6. Running Generalization Audits & Ablations

### Verification Clause Template Leakage Audit
To reproduce the pairwise overlap audit between all 3,500 train and 700 val records:
```bash
python audit_template_leakage.py
```
Expected output:
```
Loaded 3500 train and 700 val records.
Exact duplicates: 0
Validation records matching exact train skeleton: 0 / 700 (0.0%)
Validation records with Jaccard >= 0.80 to a train record: 31 / 700 (4.4%)
Average Max Jaccard: 0.7058
Val records sharing normalized verification clause with train: 700 / 700 (100.0%)
```

### Verification Clause Ablation Experiment
To reproduce the ablation experiment where trailing verification sentences are removed:
```bash
python run_clause_ablation_eval.py
```
Expected output:
```
Original Accuracy: 97.00% -> Ablated Accuracy: 14.71% (Delta: -82.29 pp)
Original Macro F1: 97.05% -> Ablated Macro F1: 5.02% (Delta: -92.03 pp)
Option B (suspicious) Frequency: 669 / 700 (95.57%)
```

### Grouped Template Split Generator
To generate the 4:1 zero-overlap template-held-out dataset:
```bash
python build_grouped_template_split.py
```
- Outputs: `tev1_grouped_template_train.jsonl` (3,423 records) and `tev1_grouped_template_val.jsonl` (777 records).
- Template Family Overlap: **0.0%**.
