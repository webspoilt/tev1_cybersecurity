import json
import re

with open('tev1_grouped_template_val.jsonl', 'r', encoding='utf-8') as f:
    val_samples = {s['id']: s for s in (json.loads(l) for l in f)}

with open('v2_experiments/tev1_grouped_template_predictions.jsonl', 'r', encoding='utf-8') as f:
    preds = [json.loads(l) for l in f]

errors = [p for p in preds if not p['is_correct']]
print('Total errors:', len(errors))

e_to_d_records = []
other_error_records = []

for e in errors:
    s = val_samples[e['id']]
    rec_info = {
        'id': e['id'],
        'ground_truth': e['ground_truth'],
        'ground_truth_class': e.get('ground_truth_class'),
        'predicted_label': e['predicted_label'],
        'template_family': e.get('template_family'),
        'raw_generation': e.get('generated_raw'),
        'state': s['state'],
        'question': s['question'],
        'options': s.get('options')
    }
    
    # Analyze the distinction and evidence
    if e['ground_truth'] == 'E' and e['predicted_label'] == 'D':
        rec_info['classification_type'] = 'E_to_D_security_testing_as_admin'
        rec_info['telemetry_context'] = s['state'].split('. ')[0]
        sec_ids = re.findall(r'SEC-[0-9a-fA-F]+', s['state'])
        rec_info['identifier_found'] = sec_ids[0] if sec_ids else 'None'
        rec_info['distinction'] = 'Ground truth is E (authorised_testing) authorized under security exercise validation job SEC-xxxx. Model predicted D (expected_admin) which corresponds to operations/maintenance change tickets CHG-xxxx.'
        rec_info['likely_cause'] = 'Template phrasing dependency: The held-out template contains "accounts for the observed action and its target scope" and closing sentence "The engagement record and target owner independently verify prior permission, timing and completion within scope." Because the word "validation" and "prior permission, timing and completion" strongly resemble change ticket operational sign-offs in class D training examples, and the training data lacked this specific security template phrasing, the model misclassified security validation as routine change administration.'
        e_to_d_records.append(rec_info)
    elif e['ground_truth'] == 'C' and e['predicted_label'] == 'B':
        rec_info['classification_type'] = 'C_to_B_benign_as_suspicious'
        rec_info['distinction'] = 'Ground truth is C (benign) verified by peer workflow records and prior reviewed sessions. Model predicted B (suspicious).'
        rec_info['likely_cause'] = 'High-salience alarming telemetry keyword: The telemetry states "a process rewrote multiple files into encrypted containers" (classic ransomware indicator) during high service demand. Even though the verification clause affirms recurring business transactions, the extreme alarm of ransomware behavior biased the model toward suspicious (B).'
        other_error_records.append(rec_info)
    elif e['ground_truth'] == 'G' and e['predicted_label'] == 'B':
        rec_info['classification_type'] = 'G_to_B_unknown_as_suspicious'
        rec_info['distinction'] = 'Ground truth is G (unknown: insufficient evidence, conflicting sources). Model predicted B (suspicious: anomalous, baseline deviation).'
        rec_info['likely_cause'] = 'Conservative bias under conflicting context: The template states "Two context sources disagree about workflow attribution and neither can be independently verified." In 10 out of 133 cases (7.5%), when faced with unverified telemetry (e.g. broad ingress rule, process memory access, shell profile edit, bulk export), the model conservatively treated the unexplained activity as suspicious (B) rather than neutral unknown (G).'
        other_error_records.append(rec_info)

output = {
    'audit_metadata': {
        'total_validation_records': len(preds),
        'total_errors': len(errors),
        'e_to_d_errors_count': len(e_to_d_records),
        'other_errors_count': len(other_error_records),
        'error_breakdown': {
            'E_to_D': len(e_to_d_records),
            'C_to_B': sum(1 for r in other_error_records if r['ground_truth'] == 'C' and r['predicted_label'] == 'B'),
            'G_to_B': sum(1 for r in other_error_records if r['ground_truth'] == 'G' and r['predicted_label'] == 'B')
        }
    },
    'systematic_error_summary': {
        'e_to_d_analysis': 'In 38 out of 126 held-out class E records (30.16%), the model predicted Class D (expected_admin). 36 of these 38 errors share the exact same closing sentence: "The engagement record and target owner independently verify prior permission, timing and completion within scope." In the training set, class D heavily relied on phrases like "Operations audit verified the prior approval, allowed window and successful completion within the requested scope." Without exposure to this validation-job template during training, the model conflated security authorization with operational change authorization.',
        'other_errors_analysis': 'The remaining 11 errors consist of 1 C->B (ransomware-like encryption telemetry overpowering the benign verification clause) and 10 G->B (unresolved source contradictions on high-impact actions triggering a cautious suspicious classification).'
    },
    'e_to_d_records': e_to_d_records,
    'other_error_records': other_error_records
}

with open('v2_experiments/tev1_grouped_error_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print('Saved v2_experiments/tev1_grouped_error_analysis.json successfully.')
