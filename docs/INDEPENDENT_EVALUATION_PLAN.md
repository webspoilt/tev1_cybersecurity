# Independent Evaluation Plan: Real-World Enterprise Alert Triage

**Document Version:** 1.0  
**Project Directory:** `C:\Users\ASUS\Desktop\jev`  
**Execution Environment:** Isolated Evaluation Directory (`eval_independent/`)  
**Safety Status:** `CONFIRM_FINETUNE = False` (Inference / Evaluation Only)

---

## 1. Evaluation Purpose and Scope

Following the rigorous findings from the OpenSec-Triage audit—where synthetic verification clauses accounted for model accuracy drops from 97.0% down to 14.7% upon ablation—this plan establishes an independent evaluation protocol using **SecAlertBench** (`Dxsssu/SecAlertBench`).

### Objectives
1. Measure whether Tev1 can distinguish genuine real-world enterprise attacks from non-attack noise without synthetic English explanation boilerplate.
2. Compare the zero-shot base model (`togethercomputer/Tev1-0.8B-experimental`) against the grouped-template QLoRA adapter (`v2_experiments/tev1_grouped_template_pilot_v1`).
3. Preserve absolute dataset integrity: **zero label translation, zero evidence fabrication, and zero artificial context injection.**

---

## 2. Dataset Specifications & Verification

- **Upstream Repository:** `https://github.com/Dxsssu/SecAlertBench`
- **Data Files:**
  - `secalertbench_attack.json` (SHA-256: `4ce14a3439746d53f2634f90bff176ec904d91c3c7f5de5b9edcc53043eaab61`)
  - `secalertbench_non_attack.json` (SHA-256: `8fc6301c1915524d0c1eaa0f84e49cc600daf413edfe0ea0c61897d71496da27`)
- **Data Format:** Normalized JSON records representing actual enterprise Web Application Firewall (WAF) and IDS alert streams.
- **Fields Provided:** `rule_name`, `attack_type`, `method`, `uri`, `parameter`, `req_body`, `req_header`, `rsp_status`, `rsp_header`, `rsp_body`, `sip`, `sport`, `dip`, `dport`.

---

## 3. Evaluation Protocol: Binary Alert Triage Task

Because SecAlertBench provides native `Attack` vs. `Non-Attack` ground truth, we do not force the model into the synthetic 7-class A–G interface. Instead, we define a natural binary triage decision prompt:

```text
<|im_start|>system
You are a Security Operations Center (SOC) Tier-1 triage assistant. Analyze the incoming alert telemetry and decide whether the event represents an actual attack or a non-attack (benign traffic / false alarm). Respond strictly with A or B.
<|im_end|>
<|im_start|>user
Alert Rule: {rule_name}
Attack Category: {attack_type}
HTTP Method: {method}
Target URI: {uri}
Request Parameters: {parameter}
Request Body: {req_body}
HTTP Response Code: {rsp_status}

Which classification best describes this alert?
A: Attack (Malicious activity or exploit attempt)
B: Non-Attack (Benign traffic, false alarm, or normal operation)
<|im_end|>
<|im_start|>assistant
```

---

## 4. Sampling Strategy for Manual Reviewability

To ensure manageable compute time and 100% human-auditable results on local hardware (RTX 3050 Laptop GPU):
- **Sample Size:** 200 total alerts (100 Attack samples, 100 Non-Attack samples).
- **Sampling Method:** Stratified deterministic sampling using a fixed seed (`seed=42`).
- **Reviewable Samples:** Pre-stored in `eval_independent/` for full inspection before evaluation execution.

---

## 5. Metrics and Reporting

For both the Base Model and the Grouped LoRA Adapter:
1. Overall Accuracy on real-world enterprise alerts.
2. Attack Detection Rate (Recall on Class A / True Positive Rate).
3. False Alarm Rate (False Positive Rate on Class B).
4. Qualitative inspection of payload interpretations (e.g. Log4Shell JNDI injection, SQLi, traversal).

---

## 6. Execution Safety Rules

1. **Frozen Adapters:** Neither adapter's weights nor config files will be modified.
2. **Read-Only Data:** The raw JSON datasets in `eval_independent/` are immutable.
3. **Hardware Overhead:** Batch size 1, inference only, peak VRAM under 1.2 GB.
