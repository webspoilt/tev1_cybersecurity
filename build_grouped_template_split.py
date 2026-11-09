"""
Constructs a genuine grouped split where entire verification-template families are held out.
Input: all 4,200 records from tev1_triage_candidate_train.jsonl and tev1_triage_candidate_val.jsonl.
Methodology:
- Groups records by class and verification lead family (Sentence 5 template).
- Each class has exactly 5 independent lead template families.
- Holds out 1 complete, independent template family per class for Validation.
- Allocates the remaining 4 template families per class to Training.
- Ensures ZERO verification-template family overlap between Train and Val.
- Preserves all 7 original classes, full original telemetry, business context, timestamps, and authentic ground-truth evidence.
- Preserves source attribution: tegridydev/opensec-triage (CC BY 4.0).
Outputs:
- tev1_grouped_template_train.jsonl
- tev1_grouped_template_val.jsonl
- tev1_grouped_template_manifest.json
"""
import json
import os
import re
import hashlib
from collections import defaultdict, Counter

WORKSPACE = r"C:\Users\ASUS\Desktop\jev"
IN_TRAIN = os.path.join(WORKSPACE, "tev1_training_candidate", "tev1_triage_candidate_train.jsonl")
IN_VAL = os.path.join(WORKSPACE, "tev1_training_candidate", "tev1_triage_candidate_val.jsonl")

OUT_TRAIN = os.path.join(WORKSPACE, "tev1_grouped_template_train.jsonl")
OUT_VAL = os.path.join(WORKSPACE, "tev1_grouped_template_val.jsonl")
OUT_MANIFEST = os.path.join(WORKSPACE, "tev1_grouped_template_manifest.json")

all_records = []
for p in [IN_TRAIN, IN_VAL]:
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_records.append(json.loads(line))

print(f"Loaded {len(all_records)} total candidate records.")

def get_template_family(state_text):
    sents = [s.strip() for s in state_text.split(".") if s.strip()]
    lead = sents[5]
    lead = re.sub(r"CHG-[a-f0-9]+", "<CHG_ID>", lead)
    lead = re.sub(r"SEC-[a-f0-9]+", "<SEC_ID>", lead)
    return lead

recs_by_label = defaultdict(list)
for idx, r in enumerate(all_records):
    fam = get_template_family(r["state"])
    r["template_family"] = fam
    r["record_id"] = idx
    recs_by_label[r["label"]].append(r)

train_records = []
val_records = []

train_families_by_class = {}
val_family_by_class = {}

for lbl in sorted(recs_by_label.keys()):
    items = recs_by_label[lbl]
    fams = sorted(list(set(it["template_family"] for it in items)))
    assert len(fams) == 5, f"Expected 5 families for class {lbl}, got {len(fams)}"
    
    # 4 families for train, 1 held-out family for val
    t_fams = fams[:4]
    v_fam = fams[4]
    
    train_families_by_class[lbl] = t_fams
    val_family_by_class[lbl] = v_fam
    
    t_recs = [it for it in items if it["template_family"] in t_fams]
    v_recs = [it for it in items if it["template_family"] == v_fam]
    
    train_records.extend(t_recs)
    val_records.extend(v_recs)

# Verify zero overlap between train and val template families
train_fam_set = set(r["template_family"] for r in train_records)
val_fam_set = set(r["template_family"] for r in val_records)
overlap = train_fam_set.intersection(val_fam_set)
assert len(overlap) == 0, f"ERROR: Template family leakage detected: {overlap}"

# Write train file
with open(OUT_TRAIN, "w", encoding="utf-8") as f:
    for r in train_records:
        clean_rec = {
            "id": r["record_id"],
            "state": r["state"],
            "question": r["question"],
            "options": r["options"],
            "label": r["label"],
            "target_name": r["target_name"],
            "template_family": r["template_family"],
            "provenance": "tegridydev/opensec-triage (CC BY 4.0)"
        }
        f.write(json.dumps(clean_rec) + "\n")

# Write val file
with open(OUT_VAL, "w", encoding="utf-8") as f:
    for r in val_records:
        clean_rec = {
            "id": r["record_id"],
            "state": r["state"],
            "question": r["question"],
            "options": r["options"],
            "label": r["label"],
            "target_name": r["target_name"],
            "template_family": r["template_family"],
            "provenance": "tegridydev/opensec-triage (CC BY 4.0)"
        }
        f.write(json.dumps(clean_rec) + "\n")

# Compute hashes
def file_sha256(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

train_hash = file_sha256(OUT_TRAIN)
val_hash = file_sha256(OUT_VAL)

manifest = {
    "dataset_name": "Tev1 Grouped Template-Held-Out Split",
    "upstream_source": "tegridydev/opensec-triage",
    "license": "CC BY 4.0",
    "split_methodology": "Grouped K-Fold Template Holdout (1 entire template family held out per class)",
    "template_families_per_class": 5,
    "train_template_families_per_class": 4,
    "val_template_families_per_class": 1,
    "template_family_overlap_count": len(overlap),
    "total_records": len(all_records),
    "train_records": len(train_records),
    "val_records": len(val_records),
    "train_class_distribution": dict(Counter(r["label"] for r in train_records)),
    "val_class_distribution": dict(Counter(r["label"] for r in val_records)),
    "files": {
        "train": {
            "path": "tev1_grouped_template_train.jsonl",
            "record_count": len(train_records),
            "sha256": train_hash
        },
        "val": {
            "path": "tev1_grouped_template_val.jsonl",
            "record_count": len(val_records),
            "sha256": val_hash
        }
    },
    "held_out_families_by_class": val_family_by_class
}

with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("\n=== GROUPED SPLIT GENERATION COMPLETE ===")
print(f"Train records: {len(train_records)} (SHA-256: {train_hash})")
print(f"Val records:   {len(val_records)} (SHA-256: {val_hash})")
print(f"Template family overlap: {len(overlap)} (VERIFIED ZERO OVERLAP)")
print(f"Manifest saved to: {OUT_MANIFEST}")
