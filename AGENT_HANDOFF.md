# JEV / Tev1: Master Agent Handoff & Project State Specification

> [!IMPORTANT]
> **CRITICAL MANDATE FOR SUCCESSOR AGENTS:**
> When another Antigravity agent opens this repository on a different computer, it **must** read this file (`AGENT_HANDOFF.md`) completely before running commands, editing scripts, initializing Git repositories, or modifying model weights. This file is the authoritative, permanent single source of truth across all developmental stages, physical machines, and conversational boundaries.

---

## Part 1 — Complete Project Identity & Architectural Mission

### 1.1 Project Overview
- **Project Identifier:** JEV / Tev1 Cybersecurity Fine-Tuning Research (Internal Codename: `jev`)
- **Core Research Question:** Can a sub-1B parameter hybrid recurrent-attention neural model (`togethercomputer/Tev1-0.8B-experimental`) be fine-tuned via parameter-efficient low-rank adaptation (QLoRA) to perform reliable enterprise Security Operations Center (SOC) incident triage, and does performance on synthetic triage benchmarks transfer to authentic enterprise detection telemetry?
- **Current Operational Status:**
  - **Empirical Experiments:** 100% COMPLETE. Frozen.
  - **Model Adapters:** Preserved and locked in `v2_experiments/`.
  - **Fine-Tuning Safety Locks:** HARD-LOCKED (`CONFIRM_FINETUNE = False` in `run_tev1_pilot.py` and `run_tev1_grouped_pilot.py`). Successor agents must never enable or execute training without explicit user direction.
  - **Git Status:** Git repository is **not initialized** (`.git` does not exist). No commits, pushes, or remotes exist.
  - **Release State:** Fully staged, audited, and manifested for a public GitHub source release under MIT License for original JEV code.

### 1.2 Strict Project Boundary & Bounty Hunter Separation
- **Separation Statement:** The JEV / Tev1 project is strictly and exclusively an academic/empirical machine learning research project on sub-1B alert triage and synthetic-to-real transferability.
- **The Bounty Hunter Project:** An entirely separate, future prospective security application project hosted on another machine. It incorporates agentic multi-turn threat hunting, live environment orchestration, and interactive attack investigation.
- **Cross-Contamination Warning:** The next agent must **never** conflate JEV/Tev1 with Bounty Hunter, must not import Bounty Hunter files into this repository, and must keep all JEV publication manuscripts, code, and documentation strictly focused on Tev1 triage evaluation.

---

## Part 2 — Complete Chronological History (All 27 Phases)

The project progressed through 27 distinct developmental, experimental, and audit phases:

1. **Initial Conception & Model Exploration:** Explored low-footprint edge LLMs capable of running on consumer GPU hardware for SOC alert assessment. Investigated candidate architectures including Qwen, Llama, and recurrent delta-rule hybrid models.
2. **First Base Model Selection (Trendyol Discard):** Evaluated `Trendyol/Trendyol-LLaMa-3-8B-v2.0` and alternative Turkish-English/multilingual variants; discarded due to excessive VRAM demands (>16 GB) incompatible with local consumer hardware (4 GB RTX 3050).
3. **Pivoting to Tev1-0.8B:** Selected `togethercomputer/Tev1-0.8B-experimental` (545.92M parameters). Identified its unique architectural advantages: hybrid linear-attention recurrent delta-rule layers interleaved with standard feed-forward networks, enabling sub-quadratic sequence processing and low inference footprint.
4. **Local Hardware Constraints & Environment Pinning:** Benchmarked memory limits on an NVIDIA GeForce RTX 3050 Laptop GPU (4.00 GB Dedicated VRAM). Pinned Python 3.11.9, PyTorch 2.6.0+cu124, Hugging Face Transformers 5.22.2, PEFT 0.21.2, and BitsAndBytes 0.45.0 in virtual environment `.venv_local_eval`.
5. **OpenSec-Triage Dataset Onboarding:** Sourced `tegridydev/opensec-triage` (CC BY 4.0, 4,200 records), an alert triage benchmark structuring synthetic SOC incidents across a 7-class taxonomy:
   - `A`: `malicious` (True positive attack)
   - `B`: `suspicious` (Requires escalation/investigation)
   - `C`: `benign` (Benign background traffic/software)
   - `D`: `expected_admin` (Legitimate sysadmin maintenance)
   - `E`: `authorised_testing` (Authorized red team / pentest)
   - `F`: `misconfiguration` (Benign flaw / retry loop)
   - `G`: `unknown` (Contradictory / unresolvable sources)
6. **Prompt Formatting & Instruction Calibration:** Formatted OpenSec-Triage records into structured ChatML prompts pairing alert telemetry, business context, and verification clauses with the 7-class choice menu.
7. **Gate 1 Pre-Flight Verification:** Executed zero-shot baseline pre-flight checks on a stratified 700-record test slice of OpenSec-Triage (`tev1_base_val_predictions.jsonl`).
8. **Gate 1 Empirical Baseline Run:** Baseline results established: Accuracy: 35.57%, Macro-F1: 30.75%, Invalid output rate: 0.00%. The base model suffered from massive class collapse into Class B (`suspicious`, 360/700 predictions) and completely failed on Class D (`expected_admin`, F1: 0.00%).
9. **QLoRA Architecture Formulation:** Configured 4-bit NormalFloat (NF4) quantization with double quantization and bfloat16 computation. Applied LoRA rank $r=16$, $\alpha=32$ across all 12 linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `in_proj_qkv`, `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj`) over 24 layers (186 linear modules). Trainable parameters: exactly 5,411,328 (0.99% overhead).
10. **Phase 1 Pilot Training Run (Random Split):** Executed a 50-step pilot QLoRA training run (`v2_experiments/tev1_qlora_pilot_v1`) on 3,500 randomly split OpenSec-Triage records.
11. **Phase 1 Pilot Evaluation (Random Split):** Evaluated adapter on the 700 validation records: Accuracy skyrocketed to 97.00% (679/700), Macro-F1: 97.05%.
12. **Base vs. Adapter Comparative Analysis:** Verified that adapter improved accuracy by +61.43 percentage points over base across all 7 classes.
13. **Verification-Clause Leakage Discovery:** Systematic string auditing revealed that 100% of OpenSec-Triage validation records possessed trailing sentences (e.g., *"The engagement record and target owner independently verify prior permission..."*) that acted as near-deterministic cheat codes.
14. **Clause Ablation Experiment:** Stripped the trailing verification clause from all 700 validation records. Accuracy collapsed catastrophically from 97.00% to 14.71% (Macro-F1 fell from 97.05% to 5.02%). 669/700 (95.6%) collapsed into predicting Class B (`suspicious`), proving the model had memorized clause templates rather than reasoning over raw telemetry.
15. **Template-Family Discovery & Stratification Audit:** Analyzed the 4,200 OpenSec-Triage records and discovered that the entire benchmark was generated from exactly 35 distinct template families (5 per class). Random 80/20 splitting leaked identical template phrasing between train and test.
16. **Grouped Template-Family Holdout Split:** Engineered a strict grouped split holding out 1 entire template family per class (28 train families, 7 held-out val families) with 0.0% template overlap:
    - Train: 3,423 records (SHA-256: `0d3362f0b2a30021c6e349038832ab94ea955049b1d90b2ca59a5d63722b94f5`)
    - Val: 777 records (SHA-256: `fa9d49da881df0f6462111bc6f259981ac781ac33e3f96b519fd9a1bd35bcd64`)
    - Note: Natural template frequencies yielded an imbalanced validation distribution (A: 117, B: 92, C: 124, D: 65, E: 126, F: 120, G: 133).
17. **Gate 2 Pre-Flight Grouped Verification:** Pre-flight checks confirmed zero vocabulary contamination and exact loss tracking configuration.
18. **Phase 2 Pilot Training Run (Grouped Split):** Trained frozen adapter `v2_experiments/tev1_grouped_template_pilot_v1` on 3,423 grouped records for 50 steps.
19. **Phase 2 Grouped Pilot Evaluation:** Evaluated on 777 held-out records: Accuracy reached 93.69% (728/777), Macro-F1 reached 92.81%. Perfect 1.00 precision/recall on Class A (`malicious`).
20. **Grouped Error Analysis & Conflation Audit:** Analyzed all 49 validation errors. Identified 38 cases where Class E (`authorised_testing`) was misclassified as Class D (`expected_admin`) due to shared operational authorization phrasing in the validation templates.
21. **Independent Cybersecurity Dataset Search:** Audited candidate public SOC datasets for cross-domain transfer: Splunk BOTS (v1, v2, v3), CIC-IDS2017, and LANL Unified Host and Network Dataset.
22. **LANL Unified Discard:** Discarded LANL Unified due to absence of ground-truth incident triage labels (raw authentication and process events without alert semantics).
23. **SecAlertBench Discovery & Data-Use Review:** Identified SecAlertBench (enterprise SOC alerts labeled Attack / Non-Attack). Confirmed open research repository status but quarantined raw records due to lack of explicit redistribution license.
24. **SecAlertBench Binary Evaluation Protocol:** Formulated a rigorous 200-alert balanced evaluation (100 Attack, 100 Non-Attack) tested across two conditions:
    - **Condition A (Full Metadata):** Alert rule name, kill chain phase, and evidence.
    - **Condition B (Evidence Only):** Stripped rule names and attack classifications to test raw telemetry interpretation.
25. **Windows Defender AV Quarantine Fix:** Resolved OS Errno 22 caused by Defender quarantining webshell exploit payloads by sampling records directly in-memory during inference without intermediate disk writes.
26. **Statistical Reliability Audit:** Recomputed metrics across 800 predictions using Wilson score intervals and 2,000 paired bootstrap resamples. Revealed that while the adapter drastically cut false alarms in Condition A (FPR dropped from 75% to 26%), it suffered severe false negatives in Condition B (Recall collapsed to 4%).
27. **Packaging, Documentation & Handoff Preparation:** Built comprehensive research papers, publication readiness checklists, release manifests, and cross-machine handoff specifications.

---

## Part 3 — Exact Model Architecture & Parameter Truth

### 3.1 Model Base Specifications
- **Hugging Face Model ID:** `togethercomputer/Tev1-0.8B-experimental`
- **Total Base Parameter Count:** 545,920,000 (~545.92M parameters)
- **Base Architecture:** Hybrid Linear-Attention Recurrent Delta-Rule (Interleaved linear attention recurrence and standard transformer feed-forward blocks across 24 layers).
- **Quantization:** 4-bit NormalFloat (`bitsandbytes` NF4) with double quantization and `bfloat16` compute dtype.

### 3.2 Fine-Tuning PEFT / LoRA Hyperparameters
- **Adapter Type:** QLoRA
- **LoRA Rank ($r$):** 16
- **LoRA Alpha ($\alpha$):** 32
- **LoRA Dropout:** 0.05
- **Bias:** `none`
- **Target Modules (12 projections across 24 layers, 186 linear modules):**
  - Attention/Linear-Recurrence: `in_proj_qkv`, `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj`, `q_proj`, `k_proj`, `v_proj`, `o_proj`
  - Feed-Forward MLP: `gate_proj`, `up_proj`, `down_proj`
- **Total Trainable LoRA Parameters:** **5,411,328**
- **Parameter Overhead:** 0.9912% of base model (0.6304% of total 858.4M PEFT module representation).
- *(Note on historical typo: Early planning drafts estimated ~10.85M parameters assuming standard 2-matrix MLP expansions without linear recurrence folding. The verified exact runtime count from PEFT is 5,411,328).*

### 3.3 Training Hyperparameters
- **Training Steps:** 50 steps
- **Batch Size:** 2 per device (with gradient accumulation steps = 4; effective batch size = 8)
- **Optimizer:** `paged_adamw_8bit`
- **Learning Rate:** $2.0 \times 10^{-4}$ with linear decay
- **Warmup Steps:** 5
- **Max Sequence Length:** 1,024 tokens
- **Inference Generation:** Temperature 0.0 (greedy decoding), `max_new_tokens = 2`, `enable_thinking = False`.

---

## Part 4 — Master Empirical Results Table

All metrics below have been recomputed directly from raw prediction JSONL files and cross-verified via `v2_experiments/tev1_final_statistical_analysis.json`.

### 4.1 In-Domain OpenSec-Triage Benchmark Results

| Experiment / Evaluation Split | Evaluation Records | Accuracy | Macro F1 | Invalid Output Rate | Key Failure Mode / Dominant Behavior |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Gate 1 Base Model Zero-Shot** | 700 (Stratified) | 35.57% | 30.75% | 0.00% | Severe bias towards Class B (`suspicious`); 0.00% F1 on Class D (`expected_admin`). |
| **Random Split Pilot Adapter** | 700 (Stratified) | 97.00% | 97.05% | 0.00% | 100% memorization of trailing verification sentence clauses. |
| **Verification Clause Ablation** | 700 (Ablated) | 14.71% | 5.02% | 0.00% | 669/700 (95.6%) collapsed into Class B; proves inability to reason on raw telemetry. |
| **Grouped Template-Held-Out Pilot** | 777 (Grouped Val) | 93.69% | 92.81% | 0.00% | 38/126 Class E (`authorised_testing`) misclassified as Class D (`expected_admin`). |

### 4.2 Grouped Template-Held-Out Per-Class Breakdown (777 Records)

| Class Label | Semantic Category | Support | Precision | Recall | F1-Score | Confusion / Errors |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **A** | `malicious` | 117 | 1.0000 | 1.0000 | 1.0000 | 0 errors (117/117 correct) |
| **B** | `suspicious` | 92 | 0.8932 | 1.0000 | 0.9436 | 11 false alarms (from C and G) |
| **C** | `benign` | 124 | 1.0000 | 0.9919 | 0.9960 | 1 error (predicted B) |
| **D** | `expected_admin` | 65 | 0.6311 | 1.0000 | 0.7738 | 38 false positives from Class E |
| **E** | `authorised_testing` | 126 | 1.0000 | 0.6984 | 0.8224 | 38 misclassified as Class D |
| **F** | `misconfiguration` | 120 | 1.0000 | 1.0000 | 1.0000 | 0 errors (120/120 correct) |
| **G** | `unknown` | 133 | 1.0000 | 0.9248 | 0.9609 | 10 misclassified as Class B |
| **Total / Macro** | — | **777** | **0.9320** | **0.9450** | **0.9281** | **Total errors: 49 (93.69% Acc)** |

### 4.3 Independent Enterprise Evaluation (SecAlertBench — 200 Alerts)

Evaluated on 100 Attack and 100 Non-Attack real-world enterprise alerts under Condition A (Full Metadata) and Condition B (Evidence Only).

| Condition & Model | Accuracy [95% CI] | Attack Recall (TPR) [95% Wilson] | False Positive Rate (FPR) [95% Wilson] | Balanced Acc [95% CI] | Macro F1 [95% CI] | Matthews Corr (MCC) | Avg Latency (ms) | Peak VRAM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cond A: Base Model** | 45.0% [38.0%, 52.0%] | 65.0% [55.3%, 73.6%] | 75.0% [65.7%, 82.5%] | 45.0% [38.0%, 52.0%] | 42.7% [35.6%, 49.8%] | -0.1091 | 371.3 ms | 992.8 MB |
| **Cond A: Grouped Adapter** | **61.5%** [54.5%, 68.0%] | 49.0% [39.4%, 58.7%] | **26.0%** [18.4%, 35.4%] | **61.5%** [54.5%, 68.0%] | **60.9%** [53.7%, 67.5%] | **+0.2375** | 554.9 ms | 1315.5 MB |
| **Paired $\Delta$ (Adapter - Base)** | **+16.5 pp** [+9.0%, +24.0%] | **-16.0 pp** [-24.0%, -8.0%] | **-49.0 pp** [-59.0%, -40.0%] | **+16.5 pp** [+10.4%, +22.7%] | **+18.2 pp** [+11.2%, +25.3%] | — | — | — |
| **Cond B: Base Model** | 51.0% [44.0%, 58.0%] | 2.0% [0.6%, 7.0%] | 0.0% [0.0%, 3.7%] | 51.0% [47.5%, 54.5%] | 35.5% [29.7%, 41.3%] | +0.1005 | 1822.0 ms | 984.0 MB |
| **Cond B: Grouped Adapter** | 52.0% [45.0%, 59.0%] | 4.0% [1.6%, 9.8%] | 0.0% [0.0%, 3.7%] | 52.0% [48.0%, 56.0%] | 37.6% [31.5%, 43.6%] | +0.1429 | 607.3 ms | 1306.2 MB |
| **Paired $\Delta$ (Adapter - Base)** | **+1.0 pp** [0.0%, +2.5%] | **+2.0 pp** [0.0%, +5.0%] | **0.0 pp** [0.0%, 0.0%] | **+1.0 pp** [0.0%, +2.6%] | **+2.1 pp** [0.0%, +5.4%] | — | — | — |

### 4.4 Core Empirical Findings & Scientific Conclusions
1. **High In-Domain Accuracy is Not Real-World Generalization:** Achieving 93.69% accuracy on OpenSec-Triage grouped templates does not indicate autonomous SOC triage capability.
2. **Metadata Dependency:** The model relies heavily on high-level security abstractions (alert titles, rule names, MITRE techniques). When stripped of metadata (Condition B), Attack Recall collapses to 4.0% (96 false negatives out of 100 attacks).
3. **Conservative Posture Trade-Off:** In Condition A, QLoRA fine-tuning successfully suppressed spurious false positives by 49 percentage points (75% $\to$ 26%), but at the cost of 16 percentage points in missed detections (65% $\to$ 49% recall).
4. **Sub-1B Deployment Role:** Sub-1B models are suited for Tier-1 alert enrichment, false-alarm reduction, and structured routing alongside rule metadata, but cannot act as autonomous Tier-2 triage analysts on raw payload logs.

---

## Part 5 — Master File Inventory & Artifact Map

Below is the definitive catalog of all 53 project files categorized by functional tier:

### 5.1 Root Architecture & Release Documentation
- `README.md`: Public GitHub front page and project overview.
- `AGENT_HANDOFF.md`: This comprehensive master handoff specification (Root).
- `AGENT_HANDOFF_VALIDATION.md`: Integrity and numerical validation report.
- `LICENSE`: MIT License governing original JEV-authored code.
- `CITATION.cff`: Citation metadata for referencing the JEV / Tev1 research.
- `requirements.txt`: Exact pinned Python dependencies.
- `.gitignore`: Quarantine rules protecting raw datasets, virtualenvs, and weights.
- `GITHUB_PUBLIC_FILE_MANIFEST.json`: Whitelist catalog of release files.
- `GITHUB_RELEASE_SHA256.json`: Exact SHA-256 checksums of all release assets.
- `GITHUB_RELEASE_AUDIT.md`: Final release gating and history audit.
- `TEV1_PUBLIC_RELEASE_MANIFEST.json`: Canonical manifest for release verification.
- `TEV1_PUBLICATION_RELEASE_CHECKLIST.md`: Formal publication gating checklist.
- `TEV1_FINAL_RESEARCH_ABSTRACT.md`: Formal research abstract and findings summary.
- `tev1_grouped_template_manifest.json`: Manifest of grouped template holdout split.

### 5.2 Research Reports & Narrative Documentation
- `docs/RESEARCH_PAPER.md`: Full academic research paper formatted for arXiv/NeurIPS.
- `docs/PROJECT_JOURNEY.md`: Complete chronological narrative of all 27 phases.
- `docs/EXPERIMENT_INDEX.md`: Comprehensive index of all experimental benchmarks.
- `docs/PUBLICATION_READINESS.md`: Publication verification and sign-off review.
- `docs/DOCUMENTATION_COMPLETION_REPORT.md`: Audit of documentation completeness.
- `docs/NEXT_AGENT_QUICKSTART.md`: Concise 1-page orientation guide for successor agents.
- `TEV1_GATE1_BASELINE_REPORT.md`: Baseline evaluation results on 700 records.
- `TEV1_PILOT_RESULTS.md`: Random-split QLoRA pilot results.
- `TEV1_BASE_VS_ADAPTER_REPORT.md`: Direct comparison between base model and pilot.
- `TEV1_GENERALIZATION_AUDIT.md`: Verification clause leakage analysis.
- `TEV1_CLAUSE_ABLATION_REPORT.md`: Empirical results of stripping verification clauses.
- `TEV1_GROUPED_TEMPLATE_AUDIT.md`: Discovery of the 35 template families.
- `TEV1_GROUPED_TEMPLATE_PILOT_REPORT.md`: Empirical results of grouped template pilot.
- `TEV1_GROUPED_ERROR_ANALYSIS.md`: Exhaustive investigation of the 38 E $\to$ D errors.
- `TEV1_INDEPENDENT_EVALUATION_PLAN.md`: Strategic plan for enterprise transfer evaluation.
- `TEV1_SECALERTBENCH_EVALUATION.md`: Final empirical report on SecAlertBench evaluation.

### 5.3 Active Python Execution Scripts
- `run_tev1_pilot.py`: QLoRA random-split training harness (LOCKED).
- `run_tev1_grouped_pilot.py`: QLoRA grouped-split training harness (LOCKED).
- `run_tev1_base_val.py`: Zero-shot baseline evaluation script.
- `run_tev1_clause_ablation.py`: Clause ablation evaluation script.
- `run_secalertbench_eval.py`: Independent SecAlertBench binary evaluation script.
- `prepare_secalertbench_sample.py`: Deterministic alert sampling harness.
- `analyze_secalertbench_predictions.py`: Statistical bootstrap & CI calculation script.
- `verify_grouped_preflight.py`: Pre-flight data integrity validation script.
- `generate_grouped_template_split.py`: Split generation engine for template holdouts.
- `extract_pilot_errors.py`: Error record extraction script.
- `audit_grouped_errors.py`: Deep-dive script analyzing E $\to$ D confusion.
- `test_env.py`: Environment and GPU sanity check script.

### 5.4 Saved Experimental JSON & Prediction Data (`v2_experiments/`)
- `tev1_base_val_metrics.json` & `tev1_base_val_predictions.jsonl`: Gate 1 baseline data.
- `tev1_qlora_pilot_val_metrics.json` & `tev1_qlora_pilot_val_predictions.jsonl`: Random pilot data.
- `tev1_base_vs_adapter_comparison.json` & `tev1_base_vs_adapter_predictions.jsonl`: Comparison data.
- `tev1_clause_ablation_results.json` & `tev1_clause_ablation_predictions.jsonl`: Ablation data.
- `tev1_generalization_audit.json`: Clause audit metadata.
- `pilot_errors_extracted.json`: Extracted pilot error records.
- `tev1_grouped_template_metrics.json` & `tev1_grouped_template_predictions.jsonl`: Grouped pilot data.
- `tev1_grouped_error_analysis.json`: Grouped error classification records.
- `tev1_metric_integrity_audit.json`: Mathematical verification of all metrics.
- `independent_dataset_audit.json`: Audits of BOTS, CIC-IDS2017, LANL, and SecAlertBench.
- `secalertbench_binary_comparison.json`: SecAlertBench comparative results.
- `secalertbench_predictions.jsonl`: All 800 raw model predictions on SecAlertBench.
- `tev1_final_statistical_analysis.json`: Paired bootstrap distributions and Wilson intervals.

### 5.5 Preserved Adapter Directories (FROZEN)
- `v2_experiments/tev1_qlora_pilot_v1/`: Preserved weights, adapter config, and tokenizer.
- `v2_experiments/tev1_grouped_template_pilot_v1/`: Preserved weights, adapter config, and tokenizer.

---

## Part 6 — Licensing, Data Use & Redistribution Boundaries

> [!WARNING]
> Strict legal and intellectual property boundaries govern this project. Violating these rules breaches academic and open-source terms.

1. **JEV Original Source Code:** Licensed under the MIT License (`LICENSE`). All evaluation scripts, data pipelines, analysis harnesses, and documentation authored in this project are permissible for public GitHub distribution.
2. **Fine-Tuned Model Weights (`BLOCKED BY LICENCE`):**
   - The upstream base model `togethercomputer/Tev1-0.8B-experimental` is an experimental release by Together AI with unspecified derivative redistribution terms.
   - **Mandate:** Neither adapter weights nor merged models may be committed to Git or pushed to GitHub until explicit upstream redistribution rights are established. They remain quarantined in `.gitignore`.
3. **OpenSec-Triage Dataset:** Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). Attribution to `tegridydev/opensec-triage` is maintained across all documentation.
4. **SecAlertBench Dataset Quarantining:**
   - Raw records in `eval_independent/` originate from an open research repository without an explicit OSI license.
   - Raw payloads contain realistic attack strings (e.g., webshell scripts that trigger antivirus alarms).
   - **Mandate:** Raw SecAlertBench files must never be committed to Git or published. They are strictly quarantined in `.gitignore`.
5. **Credentials and Machine-Specific Paths:**
   - Secret audits confirm 0 API keys, tokens, or credentials exist.
   - All code uses portable relative paths; machine-specific prefixes (`C:\Users\ASUS\...`) must remain quarantined to local runtime artifacts.

---

## Part 7 — GitHub Transfer & Successor Machine Setup

### 7.1 Development Machine Transfer Sequence (Pushing to GitHub)
When the user instructs you to push this project to GitHub:
1. Verify `.gitignore` is intact and active.
2. Initialize Git: `git init -b main`
3. Add only whitelisted files: `git add .` (verifying against `GITHUB_PUBLIC_FILE_MANIFEST.json`).
4. Commit: `git commit -m "feat: complete JEV / Tev1 research release and agent handoff"`
5. Connect remote: `git remote add origin <USER_GITHUB_URL>`
6. Push: `git push -u origin main`

### 7.2 Successor Machine Setup Sequence (Cloning on Second PC)
When a new Antigravity agent opens this cloned repository on another computer:
1. **Read Mandate:** The agent must immediately read `AGENT_HANDOFF.md` and `docs/NEXT_AGENT_QUICKSTART.md`.
2. **Python Environment Creation:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
3. **Hardware Sanity Check:** Run `python test_env.py` to confirm PyTorch, CUDA, and GPU availability.
4. **Verify Checksums:** Run a checksum verification against `GITHUB_RELEASE_SHA256.json`.
5. **No Training Policy:** Acknowledge that `CONFIRM_FINETUNE = False` is locked and no fine-tuning is required.

---

## Part 8 — Proposed Future Research: Dual-Teacher Distillation

> [!NOTE]
> This section describes an unexecuted architectural proposal for future research. No code has been executed, no models downloaded, and no compute allocated for this phase.

### 8.1 Theoretical Motivation
Empirical evaluation demonstrated that while sub-1B models excel at low-latency classification with metadata, they lack the deep semantic representation required to interpret obfuscated exploit evidence (Condition B). Conversely, frontier 70B+ LLMs possess deep reasoning but are too slow and resource-intensive for inline Tier-1 SOC triage.

### 8.2 Proposed Architecture
A multi-task dual-teacher knowledge distillation framework:
1. **Teacher 1 (Log Parsing & Technical Reasoning):** Qwen2.5-Coder-32B-Instruct or DeepSeek-R1-Distill-Qwen-14B, providing rich representations of raw telemetry, syntax trees, and command execution traces.
2. **Teacher 2 (Security Policy & Contextual Grounding):** Laya (or equivalent specialized cybersecurity LLM), providing grounded threat intelligence, MITRE ATT&CK mappings, and enterprise policy interpretation.
3. **Student Model:** Tev1-0.8B (hybrid linear-attention delta-rule).
4. **Distillation Objective:**
   $$\mathcal{L} = \alpha \mathcal{L}_{\text{task}} + \beta \mathcal{L}_{\text{KL}}(\mathbf{z}_{\text{student}}, \mathbf{z}_{\text{telemetry}}) + \gamma \mathcal{L}_{\text{KL}}(\mathbf{z}_{\text{student}}, \mathbf{z}_{\text{policy}})$$
   Where the student learns to jointly model raw evidence and security policy without requiring trailing cheat-code clauses.

---

## Part 9 — Verification & Checksum Manifest

- **Release Date:** November 2026
- **Total Release Files:** 53
- **Primary Contacts & Authorship:** JEV / Tev1 Research Team
- **Master Checksums:** Sourced in `GITHUB_RELEASE_SHA256.json`
