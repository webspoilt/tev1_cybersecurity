# Tev1 Fine-Tuning Project — Independent Cybersecurity Dataset Audit

**Project Directory:** `C:\Users\ASUS\Desktop\jev`  
**Execution Timestamp:** 2026-11-09  
**Status:** Audit Complete & Validated  
**Safety Status:** `CONFIRM_FINETUNE = False` (All training runners locked; adapters frozen)

---

## Executive Summary

Following the completion of the 50-step grouped-template-held-out QLoRA experiment (93.69% accuracy on unseen synthetic template families), this audit investigates independent, public cybersecurity datasets to determine whether and how Tev1 can be evaluated on naturalistic enterprise telemetry.

We evaluated five candidate datasets against strict data governance and anti-fabrication standards:
1. **Splunk Boss of the SOC (BOTS v1, v2, v3)**
2. **CIC-IDS2017 (Canadian Institute for Cybersecurity)**
3. **LANL Unified Host and Network Data Set (Los Alamos National Laboratory)**
4. **SecAlertBench (Enterprise Tier-1 SOC Alert Dataset)**
5. **ALERT-BENCH / SecLog-Bench (Agentic SIEM Investigation Benchmarks)**

---

## 1. Candidate Dataset Audit Matrix

| Candidate Dataset | Official Source & Version | License & Redistribution | Data Nature | Format & Hardware Footprint | Telemetry & Context Richness | Ground-Truth Labels & Granularity | Direct A–G Compatibility? | Verdict & Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Splunk BOTS (v1, v2, v3)** | Splunk Inc. (`splunk/botsv1`, `botsv2`, `botsv3`) | **CC0-1.0 (Public Domain)** for data; Splunk Enterprise software proprietary | Realistic enterprise attack simulations + organic background noise | Pre-indexed Splunk `.tgz`, JSON/CSV by sourcetype. v1: 6.1 GB tgz (~120 GB uncompressed); v2: 16.4 GB; v3: 320 MB. | **Exceptional.** Multi-sourcetype: Windows Security, Sysmon, Suricata IDS, Stream (HTTP, DNS, SMB), IIS, Firewall. | **CTF Investigation Q&A.** Ground truth exists at investigation/CTF level (specific attacker IP, hash, CVE, infected host). | **NO.** Cannot map CTF questions directly to A–G without inventing narratives. | **Gold standard for agentic investigation**; unusable for direct zero-shot 7-class MCQ triage. |
| **CIC-IDS2017** | Canadian Institute for Cybersecurity, UNB (Sharafaldin et al., 2018) | Academic Terms of Use (CC BY-NC-SA 4.0 equivalent; mandatory citation) | Synthetic lab network traffic (B-Profile generator) | Tabular CSVs (CICFlowMeter 3, 78–85 numerical flow features). ~2.8M rows across 3.1 GB CSV; PCAPs >50 GB. | **Extremely Narrow.** Statistical network flow aggregates only (packet counts, IAT, bytes/sec). Zero host/endpoint context. | **Flow-level attack types.** `BENIGN` vs 14 attack categories (`DoS Hulk`, `PortScan`, `FTP-Patator`, etc.). | **FATAL MISMATCH.** Cannot map network flows to operational triage (`expected_admin`, `misconfiguration`, etc.). | **REJECTED.** Converting numerical CSV rows into synthetic English paragraphs would violate anti-fabrication rules. |
| **LANL Unified Host & Network** | Los Alamos National Lab (Kent et al., 2015) | US Government Open Data / Public Domain | Real enterprise network & host events over 89 days | Delimited text / JSON. >1.6 billion events; >12 GB compressed, >50 GB uncompressed. | Real anonymized Windows Event Logs (4624, 4625, 4768) and router Netflows (`CompXXXX`, `UserXXXX`). | **UNLABELLED.** No incident-level labels; only a sparse list of 749 red-team authentication events. | **NO.** Intended strictly for unsupervised anomaly detection. | **INCOMPATIBLE.** Lacks ground-truth labels required for supervised triage evaluation. |
| **SecAlertBench** | GitHub `Dxsssu/SecAlertBench` (2024) | Open research repository (Public GitHub, no formal license file) | Real-world Tier-1 enterprise SOC alert logs | Normalized JSON. Total 8,322 records (2,496 Attack, 5,826 Non-Attack). Total size: **~21.7 MB**. | **High.** Contains rule name, attack type, HTTP method, URI, payload parameters, request/response headers and bodies, status codes, IPs, ports. | **Alert-level binary ground truth:** `Attack` (true positive security threat) vs. `Non-Attack` (benign / false alarm). | **PARTIAL.** Can evaluate binary attack detection (`Attack` vs `Non-Attack`), but lacks 7-class taxonomy. | **Best lightweight candidate for realistic alert-level empirical testing** under an adapted binary triage protocol. |
| **ALERT-BENCH / AIDA** | Virginia Tech & Collaborators (arXiv:2610.10608, 2026) | Academic preprint / Open source | Replayed enterprise telemetry through Wazuh SIEM | Dynamic SIEM interaction via Model Context Protocol (MCP) | **Full interactive SIEM telemetry.** Requires agent to issue live queries. | Dynamic escalation decisions (Escalate vs Dismiss). | **NO.** Designed for multi-turn agentic tool calling, not single-turn classification. | Excellent architecture for future Bounty Hunter agent, but exceeds single-model prompt scope. |

---

## 2. Deep-Dive Findings on Candidate Datasets

### 2.1 Splunk Boss of the SOC (BOTS)
- **Strengths:** BOTS represents the most authentic, multi-dimensional security telemetry available in the public domain. It provides genuine Windows Sysmon process execution lines, DNS requests, and Suricata alert headers.
- **Fundamental Limitation for Direct Tev1 Evaluation:** BOTS was designed as a Capture-the-Flag (CTF) investigation benchmark. The ground truth exists as specific answers to analytical questions (e.g., *"What is the MD5 hash of the malicious executable uploaded by Po1s0n1vy?"*), not as pre-packaged categorization labels attached to individual log events.
- **Scientific Implication:** To evaluate Tev1's existing A–G prompt on BOTS data, an analyst would have to manually synthesize prompt paragraphs, embed selected log lines, and arbitrarily assign labels like `D` (`expected_admin`) or `E` (`authorised_testing`). Doing so would merely recreate the synthetic template problem that compromised OpenSec-Triage.

### 2.2 CIC-IDS2017
- **Methodological Assessment:** CIC-IDS2017 is a network intrusion detection dataset consisting of numerical statistical vectors generated by CICFlowMeter.
- **Why Direct Conversion is Inadmissible:** Converting tabular features (e.g., `Flow Duration: 12053`, `Total Fwd Packets: 4`, `Flow Bytes/s: 331.8`) into English text prompts does not represent naturalistic security telemetry; it is simply stringified tabular data. Furthermore, network flow labels like `DoS Hulk` or `PortScan` cannot be legitimately equated to operational classes such as `expected_admin`, `misconfiguration`, or `unknown`.

### 2.3 SecAlertBench (Dxsssu/SecAlertBench)
- **Format and Feasibility:** SecAlertBench provides 8,322 normalized JSON alert records directly from an enterprise SOC, containing raw HTTP request/response payloads, rule names, and alert metadata.
- **Evaluation Feasibility:** The dataset has verified SHA-256 hashes:
  - `secalertbench_attack.json`: `4ce14a3439746d53f2634f90bff176ec904d91c3c7f5de5b9edcc53043eaab61` (2,496 samples, 3.88 MB)
  - `secalertbench_non_attack.json`: `8fc6301c1915524d0c1eaa0f84e49cc600daf413edfe0ea0c61897d71496da27` (5,826 samples, 17.84 MB)
- **Label Alignment:** It provides binary labels: `Attack` vs. `Non-Attack`. While it does not support OpenSec-Triage's 7-class taxonomy, it provides a clean, un-fabricated test of whether Tev1 can differentiate real-world attacks from benign noise without synthetic verification clauses.

---

## 3. Scientific and Methodological Verdict

> [!IMPORTANT]
> **DIRECT EVALUATION OF TEV1'S 7-CLASS A–G ADAPTER ON RAW EXTERNAL LOGS IS SCIENTIFICALLY INVALID WITHOUT LABEL FABRICATION.**
> 
> OpenSec-Triage's 7-class schema (`malicious`, `suspicious`, `benign`, `expected_admin`, `authorised_testing`, `misconfiguration`, `unknown`) is a specialized taxonomy that does not exist natively in any raw telemetry dataset. Forcing raw Splunk logs or network flows into this 7-class interface would require an LLM or human to write artificial verification sentences—reintroducing the exact synthetic template dependencies discovered during our generalization audits.

---

## 4. Strategic Recommendations

1. **Best Candidate for Immediate Independent Evaluation:**
   - **SecAlertBench (Binary Attack Triage Evaluation):** Test the base model and adapter on a subset of 100 Attack and 100 Non-Attack real-world enterprise alerts under a binary classification prompt (`A: Malicious / Attack` vs. `B: Benign / Non-Attack`). This evaluates real payload interpretation without fabricating 7-class context.
2. **Best Candidate for Future Training & Integration:**
   - **Splunk BOTS (v1 / v3):** BOTS is the premier dataset for training multi-turn investigation agents. It should be reserved for the **Bounty Hunter project**, where an agent can run SPL queries against raw Sysmon/Suricata logs rather than being forced into a multiple-choice prompt.
3. **Hardware & Resource Considerations:**
   - The available RTX 3050 Laptop GPU (4.00 GB VRAM) and 234 GB free disk space can easily handle SecAlertBench (~22 MB JSON) and BOTSv3 (~320 MB), but cannot host uncompressed multi-terabyte SIEM instances without dedicated external indexing storage.
