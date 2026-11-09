# Tev1 Independent SecAlertBench Evaluation Report: Real-World Enterprise Alert Triage

**Project Directory:** `C:\Users\ASUS\Desktop\jev`  
**Execution Timestamp:** 2026-11-09  
**Evaluation Task:** Task ID `task-2743` (Exit Code 0, Fully Completed)  
**Safety Status:** `CONFIRM_FINETUNE = False` (All training harnesses locked; adapters frozen)  

---

## Executive Summary

To assess whether the `togethercomputer/Tev1-0.8B-experimental` model and its fine-tuned grouped LoRA adapter generalize to real-world cybersecurity telemetry outside the synthetic OpenSec-Triage dataset, an independent evaluation was executed against **SecAlertBench** (`Dxsssu/SecAlertBench`).

SecAlertBench contains real-world Tier-1 Security Operations Center (SOC) alert records collected from three large enterprise environments. Unlike OpenSec-Triage, SecAlertBench provides genuine alert telemetry (rule names, HTTP methods, URIs, raw request bodies/parameters, response status codes, and IP/port tuples) labeled natively by security analysts as `Attack` (true positive threats) versus `Non-Attack` (benign traffic / false alarms).

### Headline Empirical Findings

| Evaluation Setup | Model Under Test | Overall Accuracy | Attack Recall (TPR) | False Positive Rate (FPR) | Non-Attack Recall (TNR) | Attack Precision | Macro F1 | Matthews Corr (MCC) | Latency (ms/sample) | Peak VRAM |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Condition A: Full Metadata** | **Unadapted Base Model** | 45.00% | 65.00% | 75.00% | 25.00% | 46.43% | 42.71% | -0.1091 | 371.3 ms | 992.8 MB |
| **Condition A: Full Metadata** | **Grouped LoRA Adapter** | **61.50%** | **49.00%** | **26.00%** | **74.00%** | **65.33%** | **60.89%** | **+0.2375** | 554.9 ms | 1315.5 MB |
| *Absolute Difference ($\Delta$)* | *Adapter vs. Base* | *+16.50 pp* | *-16.00 pp* | *-49.00 pp* | *+49.00 pp* | *+18.90 pp* | *+18.18 pp* | *+0.3466* | *+183.6 ms* | *+322.7 MB* |
| **Condition B: Evidence Only** | **Unadapted Base Model** | 51.00% | 2.00% | 0.00% | 100.00% | 100.00% | 35.52% | +0.1005 | 1822.0 ms | 984.0 MB |
| **Condition B: Evidence Only** | **Grouped LoRA Adapter** | **52.00%** | **4.00%** | **0.00%** | **100.00%** | **100.00%** | **37.63%** | **+0.1429** | 607.3 ms | 1306.2 MB |
| *Absolute Difference ($\Delta$)* | *Adapter vs. Base* | *+1.00 pp* | *+2.00 pp* | *0.00 pp* | *0.00 pp* | *0.00 pp* | *+2.11 pp* | *+0.0424* | *-1214.7 ms* | *+322.2 MB* |

> [!IMPORTANT]
> **Operational Interpretation Warning:** All metrics reported above are measured on an artificially balanced evaluation sample ($N=200$, 100 Attack / 100 Non-Attack). In a production enterprise SOC, true attacks typically constitute less than 1% to 5% of daily alert volume (massive class imbalance). These results reflect **balanced-sample discriminator capacity**, not live operational triage volume.

---

## 1. Experimental Integrity Verification (12 / 12 Checks Passed)

1. **Exact Sample Counts:** Exactly 200 distinct records were evaluated (100 Attack records and 100 Non-Attack records, verified by unique sample IDs `ATTACK_000` through `ATTACK_099` and `NON_ATTACK_000` through `NON_ATTACK_099`).
2. **Deterministic Sampling:** Samples were drawn deterministically from the upstream datasets using fixed seed 42.
3. **No Code / Payload Execution:** Neither the evaluation script nor the language model executed any shell commands, scripts, or network connections from the alert payloads. All payloads were processed strictly as read-only text data.
4. **Adapter Isolation:** The Base Model evaluation loaded zero PEFT adapters (verified via `assert not hasattr(base_model, "peft_config")`). The Grouped Adapter run loaded the frozen weights from `v2_experiments/tev1_grouped_template_pilot_v1`.
5. **Separation of Conditions:** Condition A (full analyst-visible alert metadata) and Condition B (raw network evidence only) were evaluated in separate, unpolluted inference passes.
6. **Zero Label Leakage:** The ground-truth `Label` field (`Attack` / `Non-Attack`) was completely excluded from all input prompts in both conditions.
7. **Condition B Strict Neutralization:** In Condition B, all taxonomy fields (`attack_type`, `kill_chain_all`, and `rule_name`) were stripped. Prompts contained only raw protocol, IP/port tuples, HTTP method, URI, query parameters, request bodies, and HTTP status codes.
8. **Position Bias Elimination:** To neutralize token order bias, option mappings were split 50/50:
   - 100 records evaluated with `A: Attack`, `B: Non-Attack`
   - 100 records evaluated with `A: Non-Attack`, `B: Attack`
   Scoring logic decoded predicted letters (`A`/`B`) back to semantic labels (`Attack`/`Non-Attack`) according to each record's specific mapping.
9. **Zero Invalid Outputs:** 0 / 800 predictions produced formatting or invalid output errors (0.00% invalid rate).
10. **Warm-Up Execution:** A 1-sample warmup was executed before timing each model and condition.
11. **VRAM Footprint:** Maximum GPU memory allocated stayed under 1.32 GB across all runs on the local NVIDIA RTX 3050 Laptop GPU.
12. **Safety State Preserved:** `CONFIRM_FINETUNE = False` remained untouched. Neither adapter was modified or fine-tuned.

---

## 2. Condition A Deep Dive: Full Alert Metadata

In Condition A, models were provided with the standard SIEM alert summary: rule name, attack category, kill chain phase, source/destination IPs, HTTP method, URI, request parameters, request body, and HTTP response code.

### Confusion Matrices ($N=200$)

#### Base Model (Condition A)
```
                  Predicted Attack    Predicted Non-Attack
Actual Attack           65                    35
Actual Non-Attack       75                    25
```
- **False Positive Rate:** **75.00%** (75 of 100 benign alerts flagged as attacks).
- **Matthews Correlation Coefficient:** **-0.1091** (slightly worse than random chance due to strong false-alarm bias).

#### Grouped LoRA Adapter (Condition A)
```
                  Predicted Attack    Predicted Non-Attack
Actual Attack           49                    51
Actual Non-Attack       26                    74
```
- **False Positive Rate:** **26.00%** (A **49.0 percentage point reduction** in false positives compared to the base model).
- **Matthews Correlation Coefficient:** **+0.2375** (demonstrates genuine positive discrimination).

### Key Insight for Condition A
The base model acts as an alarmist sensor, predicting `Attack` on 140 of the 200 records (70% of alerts) because rule names like *"Apache Log4j2"* or *"SQL Injection"* bias it toward panic. In contrast, the grouped LoRA adapter learned significant false-positive discipline: it correctly identified 74% of the benign/non-attack alerts, improving overall accuracy from **45.00% to 61.50%** and Macro F1 from **42.71% to 60.89%**.

---

## 3. Condition B Deep Dive: Evidence-Focused Sensitivity Test

In Condition B, all taxonomy labels, rule names, and kill-chain descriptors were stripped. The models received only the raw HTTP method, URI, query parameters, request body, and HTTP response code.

### Confusion Matrices ($N=200$)

#### Base Model (Condition B)
```
                  Predicted Attack    Predicted Non-Attack
Actual Attack            2                    98
Actual Non-Attack        0                   100
```

#### Grouped LoRA Adapter (Condition B)
```
                  Predicted Attack    Predicted Non-Attack
Actual Attack            4                    96
Actual Non-Attack        0                   100
```

### Key Insight for Condition B: The Raw Telemetry Blind Spot
When rule names and attack categories are removed, **both models completely collapse into predicting `Non-Attack` on virtually every sample** (Base model predicted Non-Attack on 198/200; Adapter predicted Non-Attack on 196/200).
- The 51.0% and 52.0% accuracies are an artifact of predicting the majority class on a balanced 100/100 dataset.
- True attack detection rate dropped to **2.0% (Base)** and **4.0% (Adapter)**.
- **Root Cause:** Neither the base model nor the 50-step adapter has learned a deep token-level parser for raw URL-encoded exploit syntax (e.g. `${jndi:rmi://...}`, `' OR 1=1--`, `../../../../etc/passwd`). Because they were trained on synthetic English prose in OpenSec-Triage rather than raw URI strings, they treat unstructured query strings as benign noise in the absence of an alert rule name.

---

## 4. Per-Attack-Category Performance Breakdown

Examining performance across the most prevalent attack types in SecAlertBench reveals where the adapter succeeded and where it failed:

| Attack Category | Total Alerts | Attack Subset | Base Model Acc (Cond A) | Adapter Acc (Cond A) | Qualitative Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **SQL Injection (`SQL注入`)** | 62 | 2 | 4.8% (3 / 62) | **64.5% (40 / 62)** | The base model flagged almost every SQL alert as an attack (even when benign parameters caused a false alarm). The adapter correctly filtered out benign SQL queries, achieving 64.5% accuracy. |
| **Remote Code Execution (`代码执行`)** | 30 | 26 | **90.0% (27 / 30)** | 70.0% (21 / 30) | High base detection driven by alarming rule names (e.g. Log4j, Spring4Shell). Adapter detected 19/26 true attacks. |
| **Directory Traversal (`目录遍历`)** | 24 | 19 | 70.8% (17 / 24) | **79.2% (19 / 24)** | Adapter improved traversal classification from 70.8% to 79.2%, correctly recognizing traversal paths while suppressing benign 404 scans. |
| **Sensitive File Leakage (`敏感信息泄漏`)** | 18 | 15 | 22.2% (4 / 18) | 22.2% (4 / 18) | Both models struggled heavily with file disclosure alerts, frequently confusing benign configuration probes with true exploits. |
| **Default Misconfiguration (`默认配置不当`)** | 17 | 15 | 64.7% (11 / 17) | 47.1% (8 / 17) | Misconfigurations without clear exploit payloads proved challenging for the adapter. |
| **Weak Credentials (`弱口令`)** | 12 | 6 | 58.3% (7 / 12) | 50.0% (6 / 12) | Both models performed near chance level on credential brute-force telemetry. |

---

## 5. Answers to the Core Evaluation Questions

### Does the grouped adapter demonstrate useful transfer to this independent alert-triage task?

**Yes, but with strict and well-defined operational boundaries:**

1. **Demonstrated Positive Transfer:**
   - On full enterprise alert metadata (Condition A), the grouped adapter **significantly outperformed the base model** (+16.50 pp accuracy, +18.18 pp Macro F1, +0.3466 MCC).
   - Most importantly, the adapter drastically reduced the **False Positive Rate from 75.00% down to 26.00%**. In a Tier-1 SOC where alert fatigue is the number one operational failure point, cutting false alarms by nearly 50 percentage points while maintaining positive correlation represents a genuine capability improvement.
2. **Definitive Limitations:**
   - **Zero Transfer on Raw Unstructured Payloads (Condition B):** The adapter cannot triage raw, unparsed web telemetry without alert metadata. When stripped of rule names and categories, its attack recall collapsed to 4.0%.
   - **Synthetic-to-Natural Gap:** Training on 3,423 synthetic OpenSec-Triage records taught the model *reasoning over structured security relationships*, but did *not* teach it to be a raw regex exploit analyzer.
   - **Production Readiness:** The model is not ready for autonomous triage in a production environment. However, it demonstrates solid utility as an **assisted alert-ranking or false-positive suppression filter** when integrated alongside an upstream signature-based detection engine (like Suricata or ModSecurity).

---

## 6. Generated Project Artifacts

1. [`TEV1_SECALERTBENCH_EVALUATION.md`](file:///c:/Users/ASUS/Desktop/jev/TEV1_SECALERTBENCH_EVALUATION.md): This complete empirical evaluation report.
2. [`v2_experiments/secalertbench_binary_comparison.json`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/secalertbench_binary_comparison.json): Master metrics file containing exact accuracy, precision, recall, confusion matrices, MCC, latency, and VRAM across all 4 experimental conditions.
3. [`v2_experiments/secalertbench_predictions.jsonl`](file:///c:/Users/ASUS/Desktop/jev/v2_experiments/secalertbench_predictions.jsonl): Full audit trail containing all 800 individual predictions with sample IDs, true labels, raw model outputs, predicted choices, and correctness flags.
