"""
Independent SecAlertBench Evaluation Runner
Evaluates Base Model and Grouped LoRA Adapter across Condition A (Full Metadata)
and Condition B (Evidence-Focused / No Direct Taxonomy).

Evaluation Only - No Training - Frozen Adapters.
Uses canonical AutoProcessor, AutoModelForMultimodalLM, and apply_chat_template(enable_thinking=False).
"""

import os
import sys
import time
import json
import re
import torch
import numpy as np
from transformers import (
    AutoProcessor,
    AutoModelForMultimodalLM,
    BitsAndBytesConfig
)
from peft import PeftModel
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, matthews_corrcoef

sys.stdout.reconfigure(encoding="utf-8")

ATTACK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_independent", "secalertbench_attack.json")
NON_ATTACK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_independent", "secalertbench_non_attack.json")
BASE_MODEL_NAME = "togethercomputer/Tev1-0.8B-experimental"
GROUPED_ADAPTER_DIR = os.path.abspath("v2_experiments/tev1_grouped_template_pilot_v1")

def load_and_prepare_dataset():
    """
    Deterministically samples 100 Attack and 100 Non-Attack records using seed 42.
    Assigns balanced binary option mappings (50/50 A/B per class).
    Operates in-memory to prevent false-positive host antivirus quarantine of raw exploit payloads.
    """
    import random
    with open(ATTACK_PATH, "r", encoding="utf-8") as f:
        attacks = json.load(f)
    with open(NON_ATTACK_PATH, "r", encoding="utf-8") as f:
        non_attacks = json.load(f)

    # Sort consistently before sampling to guarantee perfect determinism
    attacks = sorted(attacks, key=lambda x: (x.get("rule_name", ""), x.get("sip", ""), x.get("uri", ""), str(x.get("parameter", ""))))
    non_attacks = sorted(non_attacks, key=lambda x: (x.get("rule_name", ""), x.get("sip", ""), x.get("uri", ""), str(x.get("parameter", ""))))

    random.seed(42)
    sampled_attacks = random.sample(attacks, 100)
    random.seed(42)
    sampled_non_attacks = random.sample(non_attacks, 100)

    # Exactly 50 A, 50 B for Attack
    attack_mappings = ["A_Attack_B_NonAttack"] * 50 + ["A_NonAttack_B_Attack"] * 50
    random.seed(42)
    random.shuffle(attack_mappings)

    # Exactly 50 A, 50 B for Non-Attack
    non_attack_mappings = ["A_NonAttack_B_Attack"] * 50 + ["A_Attack_B_NonAttack"] * 50
    random.seed(42)
    random.shuffle(non_attack_mappings)

    combined = []
    for idx, (r, m) in enumerate(zip(sampled_attacks, attack_mappings)):
        item = dict(r)
        item["sample_id"] = f"ATTACK_{idx:03d}"
        item["true_label"] = "Attack"
        item["option_mapping"] = m
        item["correct_choice"] = "A" if m == "A_Attack_B_NonAttack" else "B"
        if m == "A_Attack_B_NonAttack":
            item["options_text"] = "A: Attack (Malicious activity or exploit attempt)\nB: Non-Attack (Benign traffic, false alarm, or normal operation)"
        else:
            item["options_text"] = "A: Non-Attack (Benign traffic, false alarm, or normal operation)\nB: Attack (Malicious activity or exploit attempt)"
        combined.append(item)

    for idx, (r, m) in enumerate(zip(sampled_non_attacks, non_attack_mappings)):
        item = dict(r)
        item["sample_id"] = f"NON_ATTACK_{idx:03d}"
        item["true_label"] = "Non-Attack"
        item["option_mapping"] = m
        item["correct_choice"] = "A" if m == "A_NonAttack_B_Attack" else "B"
        if m == "A_Attack_B_NonAttack":
            item["options_text"] = "A: Attack (Malicious activity or exploit attempt)\nB: Non-Attack (Benign traffic, false alarm, or normal operation)"
        else:
            item["options_text"] = "A: Non-Attack (Benign traffic, false alarm, or normal operation)\nB: Attack (Malicious activity or exploit attempt)"
        combined.append(item)

    random.seed(42)
    random.shuffle(combined)
    return combined

def build_messages(rec, condition_name):
    system_text = (
        "You are a Security Operations Center (SOC) Tier-1 triage assistant. "
        "Analyze the supplied alert telemetry and determine whether the event represents an actual attack or a non-attack "
        "(benign traffic / false alarm). Select exactly one listed option. Return only its letter, with no explanation."
    )

    if condition_name == "A":
        # Condition A: Full alert metadata
        rule = rec.get("rule_name", "Unknown")
        cat = rec.get("attack_type", "Unknown")
        kc = rec.get("kill_chain_all", "Unknown")
        method = rec.get("method", "GET")
        uri = rec.get("uri", "/")
        param = str(rec.get("parameter", ""))[:200]
        req_body = str(rec.get("req_body", ""))[:200]
        rsp_status = rec.get("rsp_status", "Unknown")
        sip = rec.get("sip", "Unknown")
        dip = rec.get("dip", "Unknown")
        options_text = rec.get("options_text")

        user_text = (
            f"Alert Rule: {rule}\n"
            f"Attack Category: {cat}\n"
            f"Kill Chain Phase: {kc}\n"
            f"Source IP: {sip} -> Destination IP: {dip}\n"
            f"HTTP Method: {method}\n"
            f"Target URI: {uri}\n"
            f"Request Parameters: {param}\n"
            f"Request Body: {req_body}\n"
            f"HTTP Response Code: {rsp_status}\n\n"
            "Which classification best describes this alert?\n"
            f"{options_text}"
        )
    else:
        # Condition B: Evidence-focused sensitivity test (removes direct taxonomy)
        proto = rec.get("proto", "http")
        method = rec.get("method", "GET")
        uri = rec.get("uri", "/")
        param = str(rec.get("parameter", ""))[:200]
        req_body = str(rec.get("req_body", ""))[:200]
        rsp_status = rec.get("rsp_status", "Unknown")
        sip = rec.get("sip", "Unknown")
        sport = rec.get("sport", "")
        dip = rec.get("dip", "Unknown")
        dport = rec.get("dport", "")
        options_text = rec.get("options_text")

        user_text = (
            f"Network Protocol: {proto}\n"
            f"Connection: {sip}:{sport} -> {dip}:{dport}\n"
            f"HTTP Method: {method}\n"
            f"Target URI: {uri}\n"
            f"Request Parameters: {param}\n"
            f"Request Body: {req_body}\n"
            f"HTTP Response Code: {rsp_status}\n\n"
            "Which classification best describes this observed traffic?\n"
            f"{options_text}"
        )

    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text}
    ]

def extract_answer(gen_text):
    text = gen_text.strip()
    if not text:
        return None
    match = re.match(r"^([ABab])", text)
    if match:
        return match.group(1).upper()
    for ch in text:
        if ch.upper() in ("A", "B"):
            return ch.upper()
    return None

def compute_metrics(y_true_binary, y_pred_binary, y_true_choice, y_pred_choice, invalid_count):
    total = len(y_true_binary)
    correct = sum(1 for yt, yp in zip(y_true_binary, y_pred_binary) if yt == yp and yp is not None)
    acc = correct / total

    tp = sum(1 for yt, yp in zip(y_true_binary, y_pred_binary) if yt == "Attack" and yp == "Attack")
    fp = sum(1 for yt, yp in zip(y_true_binary, y_pred_binary) if yt == "Non-Attack" and yp == "Attack")
    tn = sum(1 for yt, yp in zip(y_true_binary, y_pred_binary) if yt == "Non-Attack" and yp == "Non-Attack")
    fn = sum(1 for yt, yp in zip(y_true_binary, y_pred_binary) if yt == "Attack" and yp == "Non-Attack")

    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    attack_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    attack_rec = tpr
    attack_f1 = 2 * (attack_prec * attack_rec) / (attack_prec + attack_rec) if (attack_prec + attack_rec) > 0 else 0.0

    non_prec = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    non_rec = tnr
    non_f1 = 2 * (non_prec * non_rec) / (non_prec + non_rec) if (non_prec + non_rec) > 0 else 0.0

    macro_f1 = (attack_f1 + non_f1) / 2.0
    balanced_acc = (tpr + tnr) / 2.0

    valid_yt = [1 if yt == "Attack" else 0 for yt, yp in zip(y_true_binary, y_pred_binary) if yp is not None]
    valid_yp = [1 if yp == "Attack" else 0 for yt, yp in zip(y_true_binary, y_pred_binary) if yp is not None]
    mcc = float(matthews_corrcoef(valid_yt, valid_yp)) if len(valid_yp) > 0 else 0.0

    return {
        "total_samples": total,
        "correct": correct,
        "incorrect": total - correct,
        "invalid_count": invalid_count,
        "invalid_rate": invalid_count / total,
        "accuracy": acc,
        "balanced_accuracy": balanced_acc,
        "macro_f1": macro_f1,
        "mcc": mcc,
        "tpr": tpr,
        "fpr": fpr,
        "tnr": tnr,
        "confusion_matrix": {
            "TP_attack": tp,
            "FP_attack": fp,
            "TN_non_attack": tn,
            "FN_non_attack": fn
        },
        "per_class": {
            "Attack": {
                "precision": attack_prec,
                "recall": attack_rec,
                "f1": attack_f1,
                "support": 100
            },
            "Non-Attack": {
                "precision": non_prec,
                "recall": non_rec,
                "f1": non_f1,
                "support": 100
            }
        }
    }

def run_evaluation_on_condition(model, tokenizer, records, condition_name, model_tag):
    print(f"\n>>> Running {model_tag} on Condition {condition_name} (200 records)...")

    # Warm-up pass (1 sample)
    msgs0 = build_messages(records[0], condition_name)
    p0 = tokenizer.apply_chat_template(
        msgs0,
        tokenize=False,
        add_generation_prompt=True,
        chat_template_kwargs={"enable_thinking": False}
    )
    inp0 = tokenizer(p0, return_tensors="pt").to(model.device)
    with torch.no_grad():
        _ = model.generate(**inp0, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

    start_time = time.time()

    predictions = []
    y_true_binary = []
    y_pred_binary = []
    y_true_choice = []
    y_pred_choice = []
    invalid_count = 0

    for idx, rec in enumerate(records):
        messages = build_messages(rec, condition_name)
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            chat_template_kwargs={"enable_thinking": False}
        )

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=4,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

        gen_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        raw_gen = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        pred_choice = extract_answer(raw_gen)

        target_choice = rec["correct_choice"]
        true_label = rec["true_label"]

        if pred_choice is None:
            pred_binary = None
            invalid_count += 1
            is_correct = False
        else:
            if rec["option_mapping"] == "A_Attack_B_NonAttack":
                pred_binary = "Attack" if pred_choice == "A" else "Non-Attack"
            else:
                pred_binary = "Non-Attack" if pred_choice == "A" else "Attack"
            is_correct = (pred_binary == true_label)

        y_true_binary.append(true_label)
        y_pred_binary.append(pred_binary)
        y_true_choice.append(target_choice)
        y_pred_choice.append(pred_choice)

        pred_record = {
            "model": model_tag,
            "condition": condition_name,
            "sample_id": rec["sample_id"],
            "true_label": true_label,
            "rule_name": rec.get("rule_name", ""),
            "attack_type": rec.get("attack_type", ""),
            "option_mapping": rec["option_mapping"],
            "correct_choice": target_choice,
            "generated_raw": raw_gen,
            "predicted_choice": pred_choice,
            "predicted_label": pred_binary,
            "is_correct": is_correct
        }
        predictions.append(pred_record)

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1} / 200 records...")

    if torch.cuda.is_available():
        torch.cuda.synchronize()
        peak_vram_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)
    else:
        peak_vram_mb = 0.0

    elapsed = time.time() - start_time
    ms_per_sample = (elapsed / len(records)) * 1000

    metrics = compute_metrics(y_true_binary, y_pred_binary, y_true_choice, y_pred_choice, invalid_count)
    metrics["elapsed_seconds"] = elapsed
    metrics["ms_per_sample"] = ms_per_sample
    metrics["peak_vram_mb"] = peak_vram_mb
    metrics["model"] = model_tag
    metrics["condition"] = condition_name

    print(f"Results for {model_tag} Condition {condition_name}:")
    print(f"  Accuracy: {metrics['accuracy']*100:.2f}% (Balanced Acc: {metrics['balanced_accuracy']*100:.2f}%)")
    print(f"  Attack Recall (TPR): {metrics['tpr']*100:.2f}%, FPR: {metrics['fpr']*100:.2f}%")
    print(f"  Macro F1: {metrics['macro_f1']*100:.2f}%, MCC: {metrics['mcc']:.4f}")
    print(f"  Invalid Output Rate: {metrics['invalid_rate']*100:.2f}% ({invalid_count} / 200)")
    print(f"  Latency: {ms_per_sample:.1f} ms/sample, Peak VRAM: {peak_vram_mb:.1f} MB")

    return metrics, predictions

def main():
    print("=" * 60)
    print("TEV1 INDEPENDENT SECALERTBENCH EVALUATION")
    print("=" * 60)

    records = load_and_prepare_dataset()
    print(f"Prepared {len(records)} balanced evaluation samples in-memory (100 Attack, 100 Non-Attack, 100 Option A, 100 Option B).")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    processor = AutoProcessor.from_pretrained(BASE_MODEL_NAME, trust_remote_code=False)
    tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    all_metrics = {}
    all_predictions = []

    # -------------------------------------------------------------
    # RUN 1: Base Model (No LoRA adapter)
    # -------------------------------------------------------------
    print("\n[STEP 1/2] Loading Pure Base Model (Zero LoRA)...")
    base_model = AutoModelForMultimodalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=False
    )
    assert not hasattr(base_model, "peft_config"), "ERROR: Base model has PEFT adapter attached!"

    m_base_a, p_base_a = run_evaluation_on_condition(base_model, tokenizer, records, "A", "Base_Model")
    m_base_b, p_base_b = run_evaluation_on_condition(base_model, tokenizer, records, "B", "Base_Model")

    all_metrics["base_model_condition_a"] = m_base_a
    all_metrics["base_model_condition_b"] = m_base_b
    all_predictions.extend(p_base_a)
    all_predictions.extend(p_base_b)

    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # -------------------------------------------------------------
    # RUN 2: Grouped Pilot Adapter
    # -------------------------------------------------------------
    print("\n[STEP 2/2] Loading Grouped Adapter...")
    raw_model = AutoModelForMultimodalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=False
    )
    grouped_model = PeftModel.from_pretrained(raw_model, GROUPED_ADAPTER_DIR)
    grouped_model.eval()

    m_grp_a, p_grp_a = run_evaluation_on_condition(grouped_model, tokenizer, records, "A", "Grouped_Adapter")
    m_grp_b, p_grp_b = run_evaluation_on_condition(grouped_model, tokenizer, records, "B", "Grouped_Adapter")

    all_metrics["grouped_adapter_condition_a"] = m_grp_a
    all_metrics["grouped_adapter_condition_b"] = m_grp_b
    all_predictions.extend(p_grp_a)
    all_predictions.extend(p_grp_b)

    del grouped_model
    del raw_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # -------------------------------------------------------------
    # SAVE ARTIFACTS
    # -------------------------------------------------------------
    out_comparison = "v2_experiments/secalertbench_binary_comparison.json"
    with open(out_comparison, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nSaved metrics comparison to {out_comparison}")

    out_preds = "v2_experiments/secalertbench_predictions.jsonl"
    with open(out_preds, "w", encoding="utf-8") as f:
        for p in all_predictions:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"Saved {len(all_predictions)} prediction rows to {out_preds}")

    print("\nEVALUATION COMPLETE!")

if __name__ == "__main__":
    main()
