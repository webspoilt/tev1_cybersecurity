# Tev1 Dataset Governance, Licensing, and Audit Register

## 1. Governance Principles & Strict Policies

From project inception, data governance was guided by four mandatory integrity policies:

1. **Zero Test Contamination:** Canonical cybersecurity evaluation benchmarks—specifically **CAIS WMDP-Cyber** and **CyberMetric-10000**—were quarantined strictly for held-out evaluation. Under no circumstances were benchmark records merged into candidate training pools.
2. **Zero Label or Evidence Fabrication:** No synthetic prompts, fake EDR telemetry, or fabricated labels were generated. Every candidate example derives from verifiable, pre-existing open-source security corpora.
3. **Rigorous Pre-Training Semantic Audits:** Datasets were not accepted merely based on Hugging Face metadata or claimed licenses. Every candidate underwent stratified semantic inspection to verify task suitability.
4. **License & Provenance Verification:** License claims were audited against primary upstream repositories to prevent copyright infringement or downstream license incompatibility.

---

## 2. Complete Candidate Audit Register

### Candidate 1: Trendyol Cybersecurity Instruction Dataset
- **Upstream Repository:** `Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset`
- **Claimed License:** Apache 2.0
- **Size:** 53,202 samples (~195 MB JSONL)
- **Investigation Date:** November 9, 2026
- **Audit Methodology:** 300-sample stratified audit across 5 random seeds (`TRENDYOL_FINAL_AUDIT.md`).
- **Semantic Findings:**
  - Mean assistant response length: **276 words** (~1,800 characters).
  - Content: 100% conceptual tutorials, essays, and theoretical cybersecurity explanations (e.g., explaining SQL injection syntax or SIEM log pipelines).
  - Tactical Suitability: **0 discrete incident triage tasks; 0 multiple-choice decisions**.
- **Governance Determination:** **REJECTED.** Training on this dataset would have degraded Tev1's short decision interface into conversational verbosity.

---

### Candidate 2: Los Alamos National Laboratory (LANL) Cyber1 Dataset
- **Upstream Repository:** Los Alamos National Laboratory Cybersecurity Research Data (`https://csr.lanl.gov/data/cyber1/`)
- **Claimed License:** Open Academic Research Use (Public Domain / US Gov Work)
- **Size:** 1.64 Billion authentication/event lines (~12 GB compressed)
- **Investigation Date:** November 9, 2026
- **Audit Methodology:** Sampled 50,000 authentication rows and red-team ground-truth records (`LANL_CYBER1_INSPECTION_REPORT.md`).
- **Semantic Findings:**
  - Structure: Strictly tabular CSV event tuples (`time,source_user,dest_user,source_comp,dest_comp,auth_type,logon_type,auth_orient,status`).
  - Lacks natural language text, EDR behavioral logs, or textual investigation notes.
- **Governance Determination:** **REJECTED for LLM Instruction Tuning.** Converting raw tabular CSV strings into synthetic LLM prompts without naturalistic context was rejected as unrepresentative of language-based triage.

---

### Candidate 3: OpenSec-Triage Dataset
- **Upstream Repository:** `tegridydev/opensec-triage`
- **Claimed License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Size:** 50,000 alerts (Train: 40k, Validation: 5k, Test: 5k)
- **Investigation Date:** November 9, 2026
- **Audit Methodology:** Stratified inspection, class balance verification, and trailing clause analysis (`OPENSEC_TRIAGE_FINAL_AUDIT.md`, `TEV1_GENERALIZATION_AUDIT.md`).
- **Semantic Findings:**
  - Structure: Synthetic EDR alert telemetry, business context, and follow-up verification findings mapped to a 7-class triage disposition (`malicious`, `suspicious`, `benign`, `expected_admin`, `authorised_testing`, `misconfiguration`, `unknown`).
  - High Class Balance: Exactly 14.28% per class across all 7 categories.
  - Critical Limitation Discovered: Trailing verification clauses derive from a closed pool of only ~14–15 fixed templates per class, causing structural template leakage when randomly split.
- **Governance Determination:** **APPROVED FOR PILOT STUDY with documented generalization limitations.**

---

## 3. Quarantined Evaluation Benchmarks

The following datasets are permanently marked as **Evaluation-Only Quarantined Assets**:

| Dataset Name | Sub-Split | Sample Count | Primary Purpose | Quarantine Status |
| :--- | :--- | :---: | :--- | :--- |
| **CAIS WMDP-Cyber** | Dual-use cyber knowledge | 199 | Pre-training baseline evaluation | **STRICTLY QUARANTINED (Zero Training)** |
| **CyberMetric-10000** | General cybersecurity MCQs | 922 | Pre-training baseline evaluation | **STRICTLY QUARANTINED (Zero Training)** |
| **OpenSec-Triage Test** | `opensec_raw_test.jsonl` | 5,000 | Held-out evaluation split | **STRICTLY QUARANTINED (Untouched)** |

---

## 4. Derivative Licensing Analysis

- **Base Model License:** `togethercomputer/Tev1-0.8B-experimental` is distributed under Together AI's open-weights research release terms.
- **Training Corpus License:** `tegridydev/opensec-triage` is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0), permitting modification and redistribution with attribution.
- **Derivative Adapter Policy:** Prior to any public release or commercial distribution of the adapter weights (`v2_experiments/tev1_qlora_pilot_v1`), legal counsel or maintainers must ensure license compatibility between Together AI's base terms and CC BY 4.0 attribution requirements.
