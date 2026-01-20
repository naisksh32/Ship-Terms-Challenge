# train_gemma3_lora.py (핵심 부분만 교체)

import os, argparse
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    DataCollatorForLanguageModeling, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model

import transformers
from packaging import version

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_path", required=True)
    ap.add_argument("--eval_path", default=None)
    ap.add_argument("--base_model", default="google/gemma-3-1b-it")
    ap.add_argument("--out_dir", default="out-gemma3-lora")
    ap.add_argument("--max_len", type=int, default=1024)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch_size", type=int, default=2)
    ap.add_argument("--grad_accum", type=int, default=8)
    return ap.parse_args()

def to_chat_text(tok, ex):
    messages = [
        {"role": "user", "content": ex["input"]},
        {"role": "assistant", "content": ex["output"]},
    ]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return {"text": text}

def main():
    args = parse_args()

    # Gemma3 안전 로딩
    tok = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True, use_fast=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    if version.parse(transformers.__version__).major >= 5:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            dtype="auto",
            trust_remote_code=True,
            attn_implementation="eager",
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype="auto",
            trust_remote_code=True,
            attn_implementation="eager",
        )


    lconf = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules="all-linear",   
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lconf)
    
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    files = {"train": args.train_path}
    has_val = False
    if args.eval_path:
        files["validation"] = args.eval_path
        has_val = True

    ds = load_dataset("json", data_files=files)
    base_cols = list(ds["train"].features)
    ds = ds.map(lambda ex: to_chat_text(tok, ex), remove_columns=base_cols)
    
    def tokenize_fn(batch):
        return tok(batch["text"], truncation=True, max_length=args.max_len)
    ds = ds.map(tokenize_fn, batched=True, remove_columns=["text"])

    collator = DataCollatorForLanguageModeling(tok, mlm=False)
    model.config.use_cache = False

    # 생성자에는 평가전략을 넣지 않는다 (버전별 충돌 회피)
    targs = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        logging_steps=25,
        save_strategy="steps",
        save_steps=1000,
        fp16=True, bf16=False,          # V100은 bf16 미지원
        gradient_checkpointing=True,
        optim="adamw_torch",
        report_to="none",
    )

    # 여기서 런타임 속성으로 세팅 (v4/v5 모두 대응)
    if has_val:
        if hasattr(targs, "evaluation_strategy"):
            targs.evaluation_strategy = "steps"
            targs.eval_steps = 1000
        elif hasattr(targs, "eval_strategy"):
            targs.eval_strategy = "steps"
            targs.eval_steps = 1000
    else:
        if hasattr(targs, "evaluation_strategy"):
            targs.evaluation_strategy = "no"
        elif hasattr(targs, "eval_strategy"):
            targs.eval_strategy = "no"

    try: model.print_trainable_parameters()
    except: pass
    
    trainer = Trainer(
        model=model, args=targs,
        train_dataset=ds["train"],
        eval_dataset=ds.get("validation") if has_val else None,
        data_collator=collator,
    )
    trainer.train()
    model.save_pretrained(os.path.join(args.out_dir, "adapter"))

if __name__ == "__main__":
    main()
