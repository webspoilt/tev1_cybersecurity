# Successor Agent Quick-Start Orientation

> [!IMPORTANT]
> **READ `AGENT_HANDOFF.md` FIRST!**
> This quick-start guide is a high-level executive summary. Before running commands, modifying scripts, or making decisions, you **must** read the complete [AGENT_HANDOFF.md](../AGENT_HANDOFF.md) in the repository root.

---

## 1. Project At A Glance
- **Project Name:** JEV / Tev1 Cybersecurity Fine-Tuning Research (`jev`)
- **Core Investigation:** Fine-tuning sub-1B hybrid recurrent-attention model `togethercomputer/Tev1-0.8B-experimental` (545.92M parameters, 5,411,328 QLoRA parameters) for SOC alert triage.
- **Current State:** 100% of empirical research experiments are **complete and frozen**.
- **Fine-Tuning Lock:** `CONFIRM_FINETUNE = False` is hard-locked in `run_tev1_pilot.py` and `run_tev1_grouped_pilot.py`. Do **not** unlock or retrain.
- **Git Status:** Git repository is **not initialized** (`.git` does not exist). No commits, pushes, or remotes exist.
- **Bounty Hunter Boundary:** The Bounty Hunter project is completely separate (hosted on another PC). Do **not** mix or import Bounty Hunter code here.

---

## 2. Definitive Experimental Benchmark Results

### 2.1 In-Domain OpenSec-Triage Benchmark
- **Gate 1 Baseline (700 records):** 35.57% Acc, 30.75% Macro-F1 (Severe collapse to Class B `suspicious`; 0.00% F1 on Class D `expected_admin`).
- **Random Split Pilot (700 records):** 97.00% Acc, 97.05% Macro-F1.
- **Verification Clause Ablation (700 records):** 14.71% Acc, 5.02% Macro-F1 (669/700 collapsed to Class B; revealed trailing cheat-code leakage).
- **Grouped Template Holdout Pilot (777 records, 0.0% template overlap):** 93.69% Acc, 92.81% Macro-F1 (Perfect 1.00 precision/recall on Class A `malicious`; 38 cases of Class E `authorised_testing` conflated with Class D `expected_admin`).

### 2.2 Independent Enterprise Evaluation (SecAlertBench — 200 Real Alerts)
- **Condition A (Full Metadata: Alert rule + MITRE + evidence):**
  - *Base Model:* 45.0% Acc, 65.0% Attack Recall (TPR), 75.0% False Positive Rate (FPR), MCC -0.1091.
  - *Grouped Adapter:* 61.5% Acc, 49.0% Attack Recall (TPR), 26.0% False Positive Rate (FPR), MCC +0.2375.
  - *Paired Difference:* Accuracy +16.5 pp [9.0%, 24.0%], Recall -16.0 pp [-24.0%, -8.0%], FPR -49.0 pp [-59.0%, -40.0%].
- **Condition B (Evidence Only: Stripped rule names & exploit labels):**
  - *Base Model:* 51.0% Acc, 2.0% Recall (TPR), 0.0% FPR.
  - *Grouped Adapter:* 52.0% Acc, 4.0% Recall (TPR), 0.0% FPR (96 false negatives out of 100 attacks).
  - *Scientific Takeaway:* The model cannot reason on raw payload syntax alone; it requires alert metadata abstractions.

---

## 3. Strict Compliance & Licensing Boundaries
1. **Source Code:** MIT License (`LICENSE`) for original JEV code.
2. **Adapter Weights:** `BLOCKED BY LICENCE` pending Together AI upstream clarity. Never commit or push weights to GitHub. Quarantined in `.gitignore`.
3. **SecAlertBench Raw Data:** Quarantined in `.gitignore`. Contains raw webshell payloads that trigger antivirus alarms (Windows Defender). Never push raw payloads.
4. **Credentials:** 0 credentials exist. Maintain zero API keys, tokens, or private keys.

---

## 4. Setup on This Machine (Or Cloned Machine)
1. **Activate / Create Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
2. **Sanity Check:**
   ```bash
   python test_env.py
   ```
3. **Verify SHA-256 Hashes:**
   Check against `GITHUB_RELEASE_SHA256.json`.

---

## 5. Next Recommended Agent Tasks
- If pushing to GitHub: Initialize Git (`git init -b main`), add whitelisted files, commit, and push.
- If preparing manuscript for conference submission: Review `docs/RESEARCH_PAPER.md` and `docs/PUBLICATION_READINESS.md`.
- For any other task: Consult `AGENT_HANDOFF.md`.
