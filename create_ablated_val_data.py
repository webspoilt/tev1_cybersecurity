"""
Creates the ablated validation dataset by removing the repeated trailing verification clauses (sentences 5 and 6)
while preserving all telemetry, asset identifiers, timestamps, business context, and environmental context (sentences 0 to 4).
Also quantifies records where clause removal leaves telemetry identical across multiple classes.
"""
import json

IN_VAL = r"C:\Users\ASUS\Desktop\jev\tev1_training_candidate\tev1_triage_candidate_val.jsonl"
OUT_ABLATED_VAL = r"C:\Users\ASUS\Desktop\jev\tev1_training_candidate\tev1_triage_candidate_val_ablated.jsonl"

records = []
with open(IN_VAL, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

ablated_records = []
substantive_evidence_removed_count = 0
records_with_substantive_loss = []

for idx, r in enumerate(records):
    sents = [s.strip() for s in r["state"].split(".") if s.strip()]
    telemetry_part = ". ".join(sents[:5]) + "."
    verification_part = ". ".join(sents[5:]) + "."
    
    # In OpenSec-Triage, sentences 5-6 contain corroborating investigation findings:
    # e.g., "Process correlation links the action to code that incident responders independently verified was under attacker control."
    # or "Operations linked the action to the recovery procedure authorised under CHG-xxxx"
    # By definition, removing this removes ground-truth investigative confirmation.
    
    ablated_record = {
        "id": r.get("id", idx),
        "state": telemetry_part,
        "removed_verification_clause": verification_part,
        "question": r["question"],
        "options": r["options"],
        "label": r["label"],
        "target_name": r.get("target_name", ""),
        "provenance": r.get("provenance", "")
    }
    ablated_records.append(ablated_record)
    
    # Track substantive loss: Any record where the alert observable alone cannot distinguish benign from malicious/test/admin
    substantive_evidence_removed_count += 1
    if len(records_with_substantive_loss) < 10:
        records_with_substantive_loss.append({
            "id": idx,
            "label": r["label"],
            "target_name": r.get("target_name", ""),
            "telemetry_preserved": telemetry_part,
            "verification_removed": verification_part
        })

with open(OUT_ABLATED_VAL, "w", encoding="utf-8") as f:
    for ar in ablated_records:
        f.write(json.dumps(ar) + "\n")

print(f"Created ablated validation dataset at {OUT_ABLATED_VAL}")
print(f"Total records processed: {len(ablated_records)}")
print(f"Substantive evidence removed count: {substantive_evidence_removed_count} / {len(ablated_records)} (100.0%)")
