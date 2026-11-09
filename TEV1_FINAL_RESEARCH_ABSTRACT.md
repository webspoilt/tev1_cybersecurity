# Tev1 Final Research Abstract & Empirical Synthesis

**Title:** Parameter-Efficient Cybersecurity Instruction Tuning of Hybrid Linear-Attention Models: Empirical Generalization, Template Vulnerabilities, and Enterprise Alert Triage  
**Target Artifact:** `togethercomputer/Tev1-0.8B-experimental` with QLoRA ($r=8$, $\alpha=16$, 5.41M trainable parameters)  
**Authors:** Tev1 Autonomous Research Project  
**Date:** 2026-11-09  
**Status:** Complete Empirical Synthesis & Release Gate Verified  

---

## Abstract

Security Operations Centers (SOCs) face overwhelming alert fatigue, prompting growing interest in compact, sub-billion-parameter language models capable of on-premises, low-latency alert triage without cloud data leakage. In this work, we present an exhaustive empirical study of instruction-tuning `togethercomputer/Tev1-0.8B-experimental`—a 546M-parameter hybrid linear-attention (delta-rule) causal language model—for defensive cybersecurity decision-making. 

Operating under a strict zero-budget, local consumer GPU constraint (single NVIDIA RTX 3050 Laptop GPU with 4.0 GB VRAM), we fine-tuned Tev1 using 4-bit NormalFloat Quantized Low-Rank Adaptation (QLoRA) across 186 linear projection adapter modules. Initial training on a random split of the OpenSec-Triage dataset yielded a seemingly extraordinary validation accuracy of **97.00%** (versus **35.57%** for the unadapted base model). However, adversarial generalization audits revealed extensive train-validation template leakage: all validation samples shared identical trailing verification boilerplate drawn from a closed pool of 14–15 phrases per class. A complete verification clause ablation test collapsed accuracy to **14.71%** (Macro F1: **5.02%**), proving that the pilot adapter had memorized closed syntactic patterns rather than learning robust telemetry reasoning.

To establish genuine out-of-distribution transfer, we restructured the corpus into a **Grouped Template-Held-Out Split** ($N=4,200$), holding out entire template families per class (0.0% template overlap). A newly initialized 50-step QLoRA run converged to a loss of 0.867 and achieved **93.69% accuracy** (Macro F1: **92.81%**) on 777 held-out records, demonstrating that the model could interpret novel verification phrasing for malicious attacks (100% precision/recall), misconfigurations (100% precision/recall), and baseline anomalies.

Finally, to test real-world transfer, we conducted an independent evaluation against **SecAlertBench**, evaluating 200 real-world Tier-1 enterprise SOC alerts across two conditions:
1. **Condition A (Full SIEM Alert Metadata):** The grouped adapter significantly improved overall accuracy from **45.00% to 61.50%** (paired difference $\Delta = +16.50$ pp, 95% bootstrap CI: $[+9.00\%, +24.00\%]$) and cut the False Positive Rate from **75.00% to 26.00%** ($\Delta = -49.00$ pp, 95% CI: $[-59.00\%, -40.00\%]$). However, this false-alarm discipline came with a severe operational cost: Attack Recall dropped from **65.00% down to 49.00%** ($\Delta = -16.00$ pp, 95% CI: $[-24.00\%, -8.00\%]$), resulting in 51 false negatives out of 100 attacks.
2. **Condition B (Raw Telemetry Evidence Only):** When alert rule names and taxonomy tags were stripped, attack detection collapsed across both models (**2.00% for base, 4.00% for adapter**; 96 false negatives).

These findings demonstrate that while QLoRA adaptation successfully imparts false-alarm suppression and structured alert comprehension to compact hybrid models, **the adapter cannot parse raw exploit payloads in isolation and is not suitable for autonomous alert dismissal or threat blocking.** Tev1 is strictly an experimental decision-support filter requiring human-in-the-loop oversight.
