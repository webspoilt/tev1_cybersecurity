# Tev1 Pre-Publication & Public Distribution Readiness Checklist

## 1. Executive Summary

This checklist establishes the formal publication boundaries, license verifications, credential scrubbing status, and distribution conditions required before publishing the Tev1 fine-tuning research repository to GitHub or hosting the adapter on the Hugging Face Hub.

---

## 2. Public Release Readiness Audit

| Check Category | Verification Requirement | Current Status | Supporting Evidence / Action Required |
| :--- | :--- | :---: | :--- |
| **Credential Protection** | Zero API keys, Hugging Face tokens, local passwords, or machine secrets in repo. | **VERIFIED CLEAN** | `.gitignore` active; scripts access environment variables or unauthenticated public weights. |
| **Path Anonymization** | Remove machine-specific absolute Windows usernames (`C:\Users\ASUS\...`) from public docs. | **CLEANED** | Public documentation uses generic relative paths (`docs/`, `v2_experiments/`). |
| **Benchmark Quarantine** | WMDP-Cyber and CyberMetric quarantined; zero benchmark data in training sets. | **VERIFIED CLEAN** | Bit-for-bit audited; candidate train manifests contain zero benchmark samples. |
| **Academic Integrity** | Transparent disclosure of template leakage; no false real-world SOC claims. | **VERIFIED CLEAN** | Research paper and README clearly explain the 14.71% ablation collapse and template leakage. |
| **Project Separation** | Strict separation from separate Bounty Hunter project on secondary laptop. | **VERIFIED CLEAN** | Bounty Hunter integration documented strictly as future research; zero mixed code or runs. |
| **Grouped Split Status** | Document completion of 50-step grouped pilot (93.69% accuracy on 777 held-out records). | **DOCUMENTED** | Full report committed at `TEV1_GROUPED_TEMPLATE_PILOT_REPORT.md`; safety lock re-engaged (`CONFIRM_FINETUNE=False`). |
| **Independent SOC Eval** | Document SecAlertBench evaluation (200 real alerts, 49% recall, 26% FPR, 4% evidence recall). | **DOCUMENTED** | Committed at `TEV1_SECALERTBENCH_EVALUATION.md` and `TEV1_FINAL_RESEARCH_RESULTS.md`. Raw payloads quarantined. |
| **SecAlertBench Data** | Ensure zero raw SecAlertBench alert payloads or unpermitted datasets are uploaded. | **QUARANTINED** | Raw payloads kept out of git commits; evaluation logs contain only sample IDs and labels. |
| **License Compatibility** | Confirm base model terms permit distributing fine-tuned LoRA weights. | **PENDING REVIEW** | Requires explicit review of Together AI research release terms alongside CC BY 4.0. |

---

## 3. Recommended Repository Layouts

### Recommended GitHub Repository Structure
```
tev1-cybersecurity-qlora/
├── README.md                           # Main project guide, tables, and architecture diagrams
├── CITATION.cff                        # Standard citation metadata
├── LICENSE                             # Project source code license (e.g. Apache 2.0)
├── .gitignore                          # Ignores .venv, cache, raw large dumps, credentials
├── requirements.txt                    # Pinned dependencies
├── evaluate_pilot_val.py               # Evaluation runner for random validation set
├── evaluate_grouped_pilot_val.py       # Evaluation runner for grouped held-out validation set
├── run_base_val_eval.py                # Controlled base model evaluation runner
├── run_clause_ablation_eval.py         # Verification clause ablation runner
├── build_grouped_template_split.py     # 4:1 zero-overlap grouped split builder
├── verify_grouped_preflight.py         # Pre-flight check runner for grouped split
├── run_tev1_grouped_pilot.py           # Grouped training runner (safety locked)
├── docs/
│   ├── PROJECT_JOURNEY.md              # Complete chronological engineering biography
│   ├── RESEARCH_PAPER.md              # Full research paper / technical preprint
│   ├── HUGGINGFACE_MODEL_CARD.md      # Hugging Face model card documentation
│   ├── REPRODUCIBILITY.md             # Step-by-step reproduction guide
│   ├── DATASET_GOVERNANCE.md          # Dataset audit logs, licensing, and quarantine register
│   ├── EXPERIMENT_INDEX.md            # Registry of all runs, metrics, and JSON artifacts
│   └── references.bib                 # BibTeX verified references
├── tev1_training_candidate/
│   └── manifest.json                  # Random candidate dataset SHA-256 integrity manifest
├── tev1_grouped_template_train.jsonl   # 3,423-record grouped template training split
├── tev1_grouped_template_val.jsonl     # 777-record grouped template held-out val split
└── tev1_grouped_template_manifest.json # Grouped template split manifest
```

### Recommended Hugging Face Hub Layout (Adapter Repo)
```
your-org/tev1-cybersecurity-qlora-grouped-pilot/
├── README.md                           # Model card (copied from docs/HUGGINGFACE_MODEL_CARD.md)
├── adapter_config.json                 # PEFT adapter configuration (r=8, alpha=16)
├── adapter_model.safetensors           # LoRA weights (21.7 MB safetensors)
├── chat_template.jinja                 # Jinja chat template
├── tokenizer.json                      # Tokenizer vocabulary
└── tokenizer_config.json               # Tokenizer configuration
```

---

## 4. Conditions Precedent to Public Distribution

Before pushing code or model weights to public repositories, the following final checks must occur:
1. **Repository Creation Authorization:** Confirm user approval for creating public GitHub and Hugging Face repositories.
2. **License Clearance:** Confirm that Together AI's research release terms for `Tev1-0.8B-experimental` permit distributing derivative LoRA delta weights under open research licenses.
3. **Model Weight Verification:** Ensure only `adapter_model.safetensors` (21.7 MB) is uploaded, never full base model weight tensors.
