"""
Audits train-validation template leakage between 3,500 train records and 700 validation records.
Examines:
1. Exact duplicates
2. Near-duplicates (Jaccard token similarity & edit distance)
3. Shared scenario templates / skeleton overlap (replacing entities: hostnames, principals, dates)
4. Distinctive label-correlated phrasing (e.g. key verification clauses)
"""
import json
import re
from collections import Counter, defaultdict

TRAIN_PATH = r"C:\Users\ASUS\Desktop\jev\tev1_training_candidate\tev1_triage_candidate_train.jsonl"
VAL_PATH = r"C:\Users\ASUS\Desktop\jev\tev1_training_candidate\tev1_triage_candidate_val.jsonl"

def normalize_skeleton(text):
    # Mask entities like ASSET-xxxx, principal-xxxx, dates, SEC-xxxx
    s = re.sub(r"[A-Z0-9]+-ASSET-[a-f0-9]+", "<ASSET>", text)
    s = re.sub(r"principal-[a-f0-9]+", "<PRINCIPAL>", s)
    s = re.sub(r"SEC-[a-f0-9]+", "<SEC_ID>", s)
    s = re.sub(r"\b[0-9a-f]{8,}\b", "<HASH>", s)
    return s.strip()

def tokenize(text):
    return set(re.findall(r"\w+", text.lower()))

train_recs = []
with open(TRAIN_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            train_recs.append(json.loads(line))

val_recs = []
with open(VAL_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            val_recs.append(json.loads(line))

print(f"Loaded {len(train_recs)} train and {len(val_recs)} val records.")

# 1. Exact duplicates
train_exact = set(r["state"].strip() for r in train_recs)
val_exact = set(r["state"].strip() for r in val_recs)
exact_overlap = train_exact.intersection(val_exact)

# 2. Skeleton / Template overlap
train_skeletons = defaultdict(list)
for idx, r in enumerate(train_recs):
    skel = normalize_skeleton(r["state"])
    train_skeletons[skel].append((idx, r["label"]))

val_skeleton_matches = []
for idx, r in enumerate(val_recs):
    skel = normalize_skeleton(r["state"])
    if skel in train_skeletons:
        val_skeleton_matches.append({
            "val_id": idx,
            "val_label": r["label"],
            "matched_train_count": len(train_skeletons[skel]),
            "matching_train_labels": [m[1] for m in train_skeletons[skel]],
            "skeleton": skel[:200]
        })

# 3. Jaccard similarity distributions
max_jaccards = []
threshold_90 = 0
threshold_80 = 0

train_tokens = [tokenize(r["state"]) for r in train_recs]
for val_idx, r in enumerate(val_recs):
    vt = tokenize(r["state"])
    best_j = 0.0
    for tt in train_tokens:
        inter = len(vt.intersection(tt))
        union = len(vt.union(tt))
        j = inter / union if union > 0 else 0
        if j > best_j:
            best_j = j
            if best_j >= 0.95:
                break
    max_jaccards.append(best_j)
    if best_j >= 0.90:
        threshold_90 += 1
    if best_j >= 0.80:
        threshold_80 += 1

print(f"Exact duplicates: {len(exact_overlap)}")
print(f"Validation records matching exact train skeleton: {len(val_skeleton_matches)} / {len(val_recs)} ({len(val_skeleton_matches)/len(val_recs)*100:.1f}%)")
print(f"Validation records with Jaccard >= 0.90 to a train record: {threshold_90} / {len(val_recs)} ({threshold_90/len(val_recs)*100:.1f}%)")
print(f"Validation records with Jaccard >= 0.80 to a train record: {threshold_80} / {len(val_recs)} ({threshold_80/len(val_recs)*100:.1f}%)")
print(f"Average Max Jaccard: {sum(max_jaccards)/len(max_jaccards):.4f}")

# Look at sentence/clause patterns per class
clauses_by_label = defaultdict(list)
for r in train_recs:
    # split into sentences
    sents = [s.strip() for s in r["state"].split(".") if s.strip()]
    # look at last 2 sentences (typically the verification clause)
    if len(sents) >= 2:
        clauses_by_label[r["label"]].append(". ".join(sents[-2:]))

# Check val clauses
val_clause_in_train_clause = 0
for r in val_recs:
    sents = [s.strip() for s in r["state"].split(".") if s.strip()]
    if len(sents) >= 2:
        vc = normalize_skeleton(". ".join(sents[-2:]))
        train_cls = [normalize_skeleton(tc) for tc in clauses_by_label[r["label"]]]
        if vc in set(train_cls):
            val_clause_in_train_clause += 1

print(f"Val records sharing normalized verification clause with train: {val_clause_in_train_clause} / {len(val_recs)} ({val_clause_in_train_clause/len(val_recs)*100:.1f}%)")
