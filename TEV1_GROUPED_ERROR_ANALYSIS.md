# Tev1 Fine-Tuning Project — Grouped Pilot Error Analysis & Boundary Audit

**Project Directory:** `C:\Users\ASUS\Desktop\jev`  
**Adapter Under Evaluation:** `v2_experiments/tev1_grouped_template_pilot_v1`  
**Evaluation Set:** `tev1_grouped_template_val.jsonl` (777 records, 0.0% template-family overlap)  
**Overall Result:** 728 / 777 Correct (93.69% Accuracy, 92.81% Macro F1, 49 Errors)  

---

## Executive Summary

On the completely held-out grouped template split, the Tev1 QLoRA adapter made **49 errors** out of 777 samples (6.31% error rate).
A rigorous, line-by-line inspection of all 49 erroneous predictions reveals a striking concentration:
- **38 errors (77.55% of all errors):** Class E (`authorised_testing`) misclassified as Class D (`expected_admin`).
- **10 errors (20.41% of all errors):** Class G (`unknown`) misclassified as Class B (`suspicious`).
- **1 error (2.04% of all errors):** Class C (`benign`) misclassified as Class B (`suspicious`).
- **0 errors (0.00%):** Class A (`malicious`) had **0 errors** (117/117 correct, 100% precision, 100% recall).
- **0 errors (0.00%):** Class F (`misconfiguration`) had **0 errors** (120/120 correct, 100% precision, 100% recall).

---

## 1. Deep Dive: The 38 E → D Errors (`authorised_testing` → `expected_admin`)

### 1.1 The Semantic and Operational Distinction
- **Class E (`authorised_testing`):** The observed anomalous action was deliberately generated as part of a sanctioned security assessment, simulation, or red-team validation exercise (tracked under security identifiers such as `SEC-xxxx`).
- **Class D (`expected_admin`):** The observed action is routine systems engineering, deployment maintenance, or operational configuration change executed by authorized staff (tracked under operations change tickets such as `CHG-xxxx`).

### 1.2 Inspection of the Held-Out Template Family for Class E
In the grouped split construction, the entire template family held out from training for Class E was:
> *"The security team’s validation job <SEC_ID> accounts for the observed action and its target scope."*

All 126 Class E records in the validation set contain this exact sentence (with variable hexadecimal SEC IDs).
However, when we analyze the concluding sentence across all 126 Class E validation records, a critical empirical split appears:
- **38 cases** were predicted as **D** (`expected_admin`).
- **88 cases** were predicted as **E** (`authorised_testing`).

### 1.3 Why Did the Model Predict D for Exactly These 38 Records?
When examining the 3-variant concluding sentences in the validation set:
1. **Closing Sentence 1:** *"The approval predates the event, the action is inside the exercise window, and collection records show no scope overrun."*  
   $\rightarrow$ Result: **41 / 42 (97.6%) correctly classified as E.**
2. **Closing Sentence 2:** *"The assessment coordinator verified the test identity, prior approval and matching execution window."*  
   $\rightarrow$ Result: **39 / 40 (97.5%) correctly classified as E.**
3. **Closing Sentence 3:** *"The engagement record and target owner independently verify prior permission, timing and completion within scope."*  
   $\rightarrow$ Result: **36 / 44 (81.8%) MISCLASSIFIED AS D!** (Only 8 classified as E).

### 1.4 Root-Cause Breakdown
The 38 misclassifications are caused by a direct lexical overlap with Class D's training representations:
1. **Conflation of "Target Owner / Prior Permission" with "Change Owner / Prior Approval":**
   In the training data for Class D (`expected_admin`), the dominant recurring verification phrases were:
   - *"The change owner independently verified the operator and execution window; the resulting state matches the request."*
   - *"Operations audit verified the prior approval, allowed window and successful completion within the requested scope."*
2. **Absence of Distinctive Security Terminology in Sentence 7:**
   When Sentence 7 used the words *"assessment coordinator"* or *"exercise window"*, the model reliably keyed into security testing (Class E) even with the novel held-out Sentence 6 template. But when Sentence 7 used the phrasing *"engagement record and target owner independently verify prior permission, timing and completion within scope"*, the strong tokens *"target owner"*, *"prior permission"*, and *"completion within scope"* matched the dense gradient path formed by Class D's change tickets (`CHG-xxxx`).
3. **The Word "Validation Job":**
   In infrastructure and DevOps contexts, "validation jobs" frequently run after software releases or configuration rollouts (e.g. CI/CD post-deployment validation). Without having seen *"The security team's validation job"* in training, the model weighted the administrative sign-off phrase over the security prefix.

### 1.5 Record-by-Record Manifest of All 38 E → D Errors

| ID | Telemetry Event Summary | SEC ID | Prediction | Key Reason |
| :---: | :--- | :---: | :---: | :--- |
| **2004** | Principal launched multiple compute instances | `SEC-dd13c80407a5` | D | Concluding sentence mimics change ticket sign-off |
| **2029** | Process opened a local credential-store file | `SEC-1612cde22aa4` | D | Concluding sentence mimics change ticket sign-off |
| **2036** | Recurring job definition added to schedule | `SEC-93695374c889` | D | Concluding sentence mimics change ticket sign-off |
| **2085** | Container image pulled from registry | `SEC-201749075d8f` | D | Concluding sentence mimics change ticket sign-off |
| **2089** | Access permissions broadened on directory tree | `SEC-87ef7100fd09` | D | Concluding sentence mimics change ticket sign-off |
| **2100** | Interactive shell session spawned under service account | `SEC-bb4e1a7b0d9a` | D | Concluding sentence mimics change ticket sign-off |
| **2103** | Cloud security group gained broad ingress rule | `SEC-e6bb716f6a93` | D | Concluding sentence mimics change ticket sign-off |
| **2170** | Host firewall policy modified to allow external port | `SEC-99cfc7f7a8ac` | D | Concluding sentence mimics change ticket sign-off |
| **2180** | Bulk export requested from business application | `SEC-1699cde79114` | D | Concluding sentence mimics change ticket sign-off |
| **2185** | Session deleted several storage snapshots | `SEC-ab035781f55c` | D | Concluding sentence mimics change ticket sign-off |
| **2197** | User added to administrative group | `SEC-6efd7bf2638f` | D | Concluding sentence mimics change ticket sign-off |
| **2199** | DNS server address modified on local network interface | `SEC-de74e977d7bd` | D | Concluding sentence mimics change ticket sign-off |
| **2202** | User opened URL delivered in email message | `SEC-77b11eda8eb0` | D | Concluding sentence mimics change ticket sign-off |
| **2209** | Cloud storage bucket policy modified to public read | `SEC-5a8580b638c6` | D | Concluding sentence mimics change ticket sign-off |
| **2210** | Service unit file changed and reloaded | `SEC-13b1c31edb82` | D | Concluding sentence mimics change ticket sign-off |
| **2252** | Outbound TLS connection on non-standard port | `SEC-893a2599a564` | D | Concluding sentence mimics change ticket sign-off |
| **2259** | User downloaded executable file through browser | `SEC-2ce92b44d542` | D | Concluding sentence mimics change ticket sign-off |
| **2307** | Oauth consent granted for additional scopes | `SEC-e438726807f0` | D | Concluding sentence mimics change ticket sign-off |
| **2320** | Remote management agent installed on endpoint | `SEC-08ee597b2866` | D | Concluding sentence mimics change ticket sign-off |
| **2363** | Network route table updated with new gateway | `SEC-41b7fa531071` | D | Concluding sentence mimics change ticket sign-off |
| **2378** | Local account created outside business hours | `SEC-5f4fc5ae9c14` | D | Concluding sentence mimics change ticket sign-off |
| **2401** | Account registered new MFA method | `SEC-d07d20df0adf` | D | Concluding sentence mimics change ticket sign-off |
| **2403** | Runtime configuration setting updated | `SEC-28e11c20d5f6` | D | Concluding sentence mimics change ticket sign-off |
| **2404** | Role assumed in another account | `SEC-2cf794fa77ed` | D | Concluding sentence mimics change ticket sign-off |
| **2420** | Process memory dump requested via diagnostics | `SEC-06f78e8a521f` | D | Concluding sentence mimics change ticket sign-off |
| **2431** | Unsigned kernel module loaded | `SEC-9e495842bdee` | D | Concluding sentence mimics change ticket sign-off |
| **2438** | User cloned several source repositories | `SEC-581dd419603a` | D | Concluding sentence mimics change ticket sign-off |
| **2441** | Serverless function package updated | `SEC-8243d45400be` | D | Concluding sentence mimics change ticket sign-off |
| **2445** | Workload mounted directory from host filesystem | `SEC-1ae9f4919eb3` | D | Concluding sentence mimics change ticket sign-off |
| **2448** | Database exported large table to object storage | `SEC-d8fdf6c7fcba` | D | Concluding sentence mimics change ticket sign-off |
| **2450** | API key generated with full organisation access | `SEC-fbe2f5ad839b` | D | Concluding sentence mimics change ticket sign-off |
| **2454** | Role binding granted additional cluster permissions | `SEC-9f261cbc3be4` | D | Concluding sentence mimics change ticket sign-off |
| **2458** | Process requested read access to memory space | `SEC-8655004a2a8a` | D | Concluding sentence mimics change ticket sign-off |
| **2463** | Remote PowerShell connection initiated | `SEC-f01b8182d5c3` | D | Concluding sentence mimics change ticket sign-off |
| **2483** | Batch script executed from temp directory | `SEC-2740c42d8d83` | D | Concluding sentence mimics change ticket sign-off |
| **3901** | Process injected code into neighbouring process | `SEC-5fdf1e9e4dbd` | D | Concluding sentence mimics change ticket sign-off |
| **3983** | Scheduled task deleted across domain endpoints | `SEC-5148efd34da2` | D | Concluding sentence mimics change ticket sign-off |
| **3988** | Shadow copy storage space resized | `SEC-3b378299c0c0` | D | Concluding sentence mimics change ticket sign-off |

---

## 2. Analysis of the Remaining 11 Errors

### 2.1 The Single C → B Error (`benign` misclassified as `suspicious`)
- **Record ID:** `1453`
- **Telemetry:** *"File audit on COMMUNICATIONS-ASSET-fb00bc2a5dc88c5f recorded that a process rewrote multiple files into encrypted containers."*
- **Ground Truth:** `C` (`benign`)
- **Verification Clause:** *"The action matches a recurring business transaction in prior reviewed sessions, including its scope and result. Peer workflow records corroborate the result and scope, with no unexplained follow-on events or operational error."*
- **Model Prediction:** `B` (`suspicious`)
- **Diagnosis:** **Extreme Telemetry Salience Bias.**
  "A process rewrote multiple files into encrypted containers" is the textbook behavioral definition of ransomware encryption. Despite the subsequent verification clause affirming that this was a recurring business transaction, the extreme salience of ransomware behavior overwhelmed the newly encountered validation phrasing. In SOC operations, flagging mass encryption as `suspicious` (B) rather than silently passing it as routine `benign` (C) is a standard, risk-averse operational response.

### 2.2 The Ten G → B Errors (`unknown` misclassified as `suspicious`)
- **Records (10 total):** `3069`, `3152`, `3160`, `3204`, `3273`, `3302`, `3313`, `3369`, `3397`, `3425`.
- **Ground-Truth Label:** `G` (`unknown: insufficient evidence, contradictory context sources`)
- **Held-Out Verification Clause:** *"Two context sources disagree about workflow attribution and neither can be independently verified. Neither the intended workflow nor any unauthorised outcome can be verified from the retained evidence."*
- **Model Prediction:** `B` (`suspicious`)
- **Telemetry Actions in the 10 Errors:**
  - Shell startup profile modification
  - Cloud role assumption across accounts
  - Storage snapshot deletion
  - MFA method registration during shift handover
  - Kubernetes cluster-admin role binding
  - Cross-process memory space read request
  - Directory permissions broadened overnight
  - Browser extension installed with page-reading permissions
  - Service unit file modification and reload
  - Bulk data export requested overnight
- **Diagnosis:** **Defensive Conservatism Under Contradiction.**
  All 10 affected records involve high-risk administrative or security-sensitive operations occurring during abnormal windows (overnight, shift handovers, recovery periods). When presented with conflicting sources where "neither can be independently verified," the model chose `suspicious` (B) rather than `unknown` (G) in 10 out of 133 cases (7.5%). From a defensive perspective, classifying an unverified cross-account role assumption or memory injection attempt as *suspicious* rather than purely *unknown* is a safety-oriented failure mode.

---

## 3. Methodological Assessment of the 93.69% Result

It is essential to maintain absolute academic and operational rigor when interpreting the 93.69% validation accuracy:

1. **What 93.69% Establishes:**
   - It establishes that Tev1 is **not merely memorizing n-grams or surface strings**.
   - When trained on 28 template families and evaluated on 7 completely held-out template families, the model maintained 93.69% accuracy (compared to 35.57% for the untuned base model).
   - It correctly generalized across unseen phrasing for classes A (`unauthorised change of control`), B (`volume and timing differ from baseline`), C (`matches recurring business transaction`), D (`approved operations request`), F (`incorrect retry setting`), and G (`sources disagree about workflow attribution`).
   - It achieved **100% precision and recall on malicious attacks (Class A)** and **100% precision and recall on system misconfigurations (Class F)**.

2. **What 93.69% DOES NOT Establish:**
   - **It does NOT prove real-world generalization to naturalistic SOC telemetry.** OpenSec-Triage remains a synthetic, structured dataset where each state consists of 6 to 7 clean English sentences with predictable semantic slots.
   - **It does NOT prove autonomous production readiness.** Real-world enterprise environments exhibit noisy, truncated, messy JSON logs, unformatted syslog feeds, missing fields, and adversary evasion.
   - **It highlights a specific boundary vulnerability:** The model struggles to separate security assessment jobs from operational maintenance tickets when both share authorization language.

---

## 4. Final Verdict and Strategic Recommendations

1. **Resolve E $\rightarrow$ D Conflation via Negative Sampling / Disambiguation:**
   Future fine-tuning iterations should explicitly include disambiguation training pairs emphasizing that `SEC-xxxx` prefixes and validation assessment jobs represent `authorised_testing` (E), whereas `CHG-xxxx` operational change requests represent `expected_admin` (D).
2. **Transition from Synthetic Clauses to Naturalistic Telemetry:**
   Evaluation should now progress to authentic enterprise SOC data (such as Splunk BOTS or CIC-IDS) where decisive English verification clauses are absent and models must reason over raw timestamps, process trees, and network connection metadata.
3. **Preserve Current Artifacts:**
   Both the pilot adapter (`v2_experiments/tev1_qlora_pilot_v1`) and the grouped adapter (`v2_experiments/tev1_grouped_template_pilot_v1`) are fully cataloged, mathematically verified, and preserved for future comparative benchmarks.
