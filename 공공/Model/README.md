# Finetuning Models

### 1. [Qwen3-1.7b-LOMO](https://huggingface.co/naisksh32/Qwen3-1.7B-LOMO-Shipbuilding-Marine)

### 2. [Qwen3-0.6b-LOMO](https://huggingface.co/naisksh32/Qwen3-0.6B-LOMO-Shipbuilding-Marine)

### 3. [Gemma3-1b-LOMO](https://huggingface.co/naisksh32/Gemma3-1B-LOMO-Shipbuilding-Marine)

### 4. [Gemma3-270m-LOMO](https://huggingface.co/naisksh32/Gemma3-270m-LOMO-Shipbuilding-Marine)


[Models HuggingFace](https://huggingface.co/naisksh32)

---
# Best Model
### Qwen3 1.7b
**Hyperparameters**
```
# Learning Rate (5x10^-5 ~ 5x10^-4)
learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)

# Epoch (1 ~ 3)
num_train_epochs = trial.suggest_int("num_train_epochs", 1, 3)

# Batch Size (2, 4, 8)
per_device_train_batch_size = trial.suggest_categorical("per_device_train_batch_size", [2, 4, 8])

# Weight Decay (0.0 ~ 0.05)
weight_decay = trial.suggest_float("weight_decay", 0.0, 0.05)

# Warm Up Ratio (0.0 ~ 0.1)
warmup_ratio = trial.suggest_float("warmup_ratio", 0.0, 0.1)

# Scheduler Type ("linear", "cosine", "cosine_with_restarts")
lr_scheduler_type = trial.suggest_categorical("lr_scheduler_type", ["linear", "cosine", "cosine_with_restarts"])
```

- train 4000개, test 1000개
- bitsandbytes, gradient_checkpointing, TrialPruned, clip_grad_norm_ 방법 사용
- n_trial : 10

- 최고 점수 (loss): 0.09597801646590233
```
최적 하이퍼파라미터: {'learning_rate': 1.6785114767103908e-05, 'num_train_epochs': 2, 'per_device_train_batch_size': 8, 'weight_decay': 0.01507083712209732, 'warmup_ratio': 0.09580697981215358, 'lr_scheduler_type': 'linear'}
```
---
