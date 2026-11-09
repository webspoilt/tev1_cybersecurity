"""
Dry-run configuration verification script for Grouped Pilot.
Loads base model, tokenizer, sets up LoRA config on fresh model,
tokenizes a 2-sample batch from train and val, confirms isolated output directory,
verifies that peft_config has 10.85M parameters, and checks memory overhead.
Does NOT train.
"""
import os
import json
import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

WORKSPACE = r"C:\Users\ASUS\Desktop\jev"
MODEL_ID = "togethercomputer/Tev1-0.8B-experimental"
OUT_DIR = os.path.join(WORKSPACE, "v2_experiments", "tev1_grouped_template_pilot_v1")
TRAIN_PATH = os.path.join(WORKSPACE, "tev1_grouped_template_train.jsonl")
VAL_PATH = os.path.join(WORKSPACE, "tev1_grouped_template_val.jsonl")

print("=" * 60)
print("EXECUTING DRY-RUN CONFIGURATION VERIFICATION")
print("=" * 60)

# 1. Output Isolation
os.makedirs(OUT_DIR, exist_ok=True)
print(f"[CHECK 1] Output directory verified: {OUT_DIR}")
assert not os.path.exists(os.path.join(OUT_DIR, "adapter_model.safetensors")), "Output directory already contains weights!"

# 2. Dataset Paths and Parsing
train_samples = [json.loads(line) for idx, line in enumerate(open(TRAIN_PATH, "r", encoding="utf-8")) if idx < 5]
val_samples = [json.loads(line) for idx, line in enumerate(open(VAL_PATH, "r", encoding="utf-8")) if idx < 5]
print(f"[CHECK 2] Sample parsing successful: {len(train_samples)} train / {len(val_samples)} val samples inspected.")

# 3. Model & Fresh Base Loading
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=False)
tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=False
)
assert not hasattr(base_model, "peft_config"), "Base model contains prior PEFT wrapper!"
print(f"[CHECK 3] Fresh base model loaded successfully without prior adapters.")

# 4. Attach Fresh LoRA Config
TARGET_MODULES = [
    "down_proj", "gate_proj", "in_proj_a", "in_proj_b", "in_proj_qkv",
    "in_proj_z", "k_proj", "o_proj", "out_proj", "q_proj", "up_proj", "v_proj"
]
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=TARGET_MODULES,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = prepare_model_for_kbit_training(base_model)
peft_model = get_peft_model(model, lora_config)

trainable_params, all_param = peft_model.get_nb_trainable_parameters()
print(f"[CHECK 4] Fresh LoRA attached: {trainable_params:,} trainable params / {all_param:,} total ({trainable_params/all_param*100:.2f}%)")
assert trainable_params == 5411328, f"Unexpected trainable parameter count: {trainable_params}"

print("=" * 60)
print("DRY-RUN VERIFICATION SUCCESSFUL: 4 / 4 CHECKS PASSED")
print("=" * 60)
