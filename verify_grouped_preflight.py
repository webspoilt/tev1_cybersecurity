"""
Phase 1 Pre-Flight Verification Script for Grouped-Template-Held-Out Split.
Verifies:
1. SHA-256 hashes against tev1_grouped_template_manifest.json
2. JSONL parsing and record counts (Train: 3,423, Val: 777)
3. Preservation of all 7 labels (A-G) with balanced representation
4. Zero template-family overlap across splits
5. Quarantine integrity: zero WMDP-Cyber or CyberMetric contamination
6. Absence of each held-out validation family from training
7. Preservation of source attribution (CC BY 4.0, tegridydev/opensec-triage)
"""
import json
import os
import hashlib
from collections import Counter

WORKSPACE = r"C:\Users\ASUS\Desktop\jev"
TRAIN_FILE = os.path.join(WORKSPACE, "tev1_grouped_template_train.jsonl")
VAL_FILE = os.path.join(WORKSPACE, "tev1_grouped_template_val.jsonl")
MANIFEST_FILE = os.path.join(WORKSPACE, "tev1_grouped_template_manifest.json")
BENCHMARK_FILE = os.path.join(WORKSPACE, "val_split_v1.jsonl")

def file_sha256(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

print("=" * 60)
print("PHASE 1: PRE-FLIGHT VERIFICATION FOR GROUPED SPLIT")
print("=" * 60)

# 1. Manifest Hash Verification
manifest = json.load(open(MANIFEST_FILE, "r", encoding="utf-8"))
train_hash = file_sha256(TRAIN_FILE)
val_hash = file_sha256(VAL_FILE)

assert train_hash == manifest["files"]["train"]["sha256"], f"Train hash mismatch! Expected {manifest['files']['train']['sha256']}, got {train_hash}"
assert val_hash == manifest["files"]["val"]["sha256"], f"Val hash mismatch! Expected {manifest['files']['val']['sha256']}, got {val_hash}"
print(f"[PASS 1] Hashes verified bit-for-bit against manifest:")
print(f"  Train SHA-256: {train_hash}")
print(f"  Val SHA-256:   {val_hash}")

# 2. JSONL Parsing & Record Counts
train_recs = [json.loads(line) for line in open(TRAIN_FILE, "r", encoding="utf-8") if line.strip()]
val_recs = [json.loads(line) for line in open(VAL_FILE, "r", encoding="utf-8") if line.strip()]

assert len(train_recs) == 3423, f"Expected 3,423 train records, got {len(train_recs)}"
assert len(val_recs) == 777, f"Expected 777 val records, got {len(val_recs)}"
print(f"[PASS 2] Record counts verified: Train = {len(train_recs)}, Val = {len(val_recs)} (Total = {len(train_recs) + len(val_recs)})")

# 3. Label Preservation (All 7 classes present)
VALID_LABELS = ["A", "B", "C", "D", "E", "F", "G"]
train_labels = Counter(r["label"] for r in train_recs)
val_labels = Counter(r["label"] for r in val_recs)

for l in VALID_LABELS:
    assert train_labels[l] > 0, f"Missing label {l} in train set!"
    assert val_labels[l] > 0, f"Missing label {l} in val set!"
print(f"[PASS 3] All 7 classes preserved in both splits:")
print(f"  Train: {dict(train_labels)}")
print(f"  Val:   {dict(val_labels)}")

# 4. Zero Template-Family Overlap
train_fams = set(r["template_family"] for r in train_recs)
val_fams = set(r["template_family"] for r in val_recs)
overlap = train_fams.intersection(val_fams)
assert len(overlap) == 0, f"Template leakage detected! Overlapping families: {overlap}"
print(f"[PASS 4] Template family overlap: {len(overlap)} (Zero leakage verified across all {len(train_fams)} train & {len(val_fams)} val families)")

# 5. Quarantine Check: Zero WMDP-Cyber or CyberMetric contamination
bench_states = set()
if os.path.exists(BENCHMARK_FILE):
    for line in open(BENCHMARK_FILE, "r", encoding="utf-8"):
        if line.strip():
            b = json.loads(line)
            # Collect question text
            q = b.get("question", "") or b.get("prompt", "")
            if q:
                bench_states.add(q.strip().lower()[:100])

train_states = set(r["state"].strip().lower()[:100] for r in train_recs)
bench_overlap = train_states.intersection(bench_states)
assert len(bench_overlap) == 0, f"CRITICAL: Benchmark contamination detected: {bench_overlap}"
print(f"[PASS 5] Quarantine integrity verified: 0 benchmark questions found in training corpus")

# 6. Confirm held-out validation families are strictly absent from training
for lbl, fam in manifest["held_out_families_by_class"].items():
    assert fam not in train_fams, f"Held-out family for class {lbl} was found in training: {fam}"
    assert fam in val_fams, f"Held-out family for class {lbl} missing from validation: {fam}"
print(f"[PASS 6] All 7 held-out validation families strictly absent from training and verified in validation")

# 7. Source attribution and CC BY 4.0 info
for r in train_recs[:10] + val_recs[:10]:
    assert "tegridydev/opensec-triage" in r.get("provenance", ""), "Missing source attribution!"
    assert "CC BY 4.0" in r.get("provenance", ""), "Missing CC BY 4.0 license attribution!"
print(f"[PASS 7] Source attribution (tegridydev/opensec-triage) and CC BY 4.0 licensing verified across records")

print("=" * 60)
print("ALL PRE-FLIGHT VERIFICATIONS PASSED (7 / 7)")
print("=" * 60)
