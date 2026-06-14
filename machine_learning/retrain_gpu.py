"""
CYPHRA — Full Model Retraining (GPU Optimized)
═══════════════════════════════════════════════════════════════
Hardware: Ryzen 9 9955HX | RTX 5070 Ti 12GB | 32GB DDR5
Target: 7-model ensemble with GPU acceleration
Output: machine_learning/models/ (all model files overwritten)

Usage:
    cd n:\craftathon\machine_learning
    python retrain_gpu.py
"""

import gc
import json
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DATA_PATH = Path(__file__).parent / "preprocessing" / "preprocessed_data.npz"
OUTPUT_DIR = Path(__file__).parent / "models_retrained"
OUTPUT_DIR.mkdir(exist_ok=True)

# Verify GPU
print("═" * 70)
print("  CYPHRA — Full GPU Retraining")
print("═" * 70)
print(f"  Data: {DATA_PATH}")
print(f"  Output: {OUTPUT_DIR}")

import torch
if torch.cuda.is_available():
    try:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  GPU: {gpu_name} ({gpu_mem:.1f} GB)")
        TORCH_DEVICE = "cuda"
    except Exception as e:
        gpu_name = f"GPU error: {e}"
        print(f"  GPU: {gpu_name}")
        TORCH_DEVICE = "cpu"
else:
    print("  GPU: NOT AVAILABLE")
    gpu_name = "CPU"
    TORCH_DEVICE = "cpu"

import psutil
cpu_count = psutil.cpu_count(logical=True)
ram_gb = psutil.virtual_memory().total / 1024**3
print(f"  CPU: {cpu_count} threads")
print(f"  RAM: {ram_gb:.1f} GB")
print("═" * 70)
print()

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════════

print("Loading preprocessed_data.npz...")
t0 = time.time()
data = np.load(str(DATA_PATH), allow_pickle=True)

# Data has: X, y_binary, y_family, feature_names
X = data['X']
y = data['y_binary']
feature_names = data['feature_names']

print(f"  Total: {X.shape[0]:,} samples, {X.shape[1]} features")
print(f"  Benign: {(y==0).sum():,} | Malicious: {(y==1).sum():,}")

# Stratified train/test split (80/20)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
del X, y  # Free ~3GB RAM
gc.collect()

print(f"  Train: {X_train.shape[0]:,} samples")
print(f"  Test:  {X_test.shape[0]:,} samples")
print(f"  Loaded + split in {time.time()-t0:.1f}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ═══════════════════════════════════════════════════════════════════════════════

results = []

def evaluate(name, y_pred):
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    print(f"  {name}: Acc={acc*100:.3f}% | Prec={prec*100:.3f}% | Rec={rec*100:.3f}% | F1={f1*100:.3f}%")
    return {"name": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


# ── 1. LightGBM (3 variants, CPU — histogram is already fast) ────────────────
print("=" * 70)
print("  TRAINING: LightGBM (3 variants)")
print("=" * 70)
import lightgbm as lgb

lgbm_configs = [
    ("LGBM_Deep", {"n_estimators": 1500, "num_leaves": 255, "max_depth": 12, "learning_rate": 0.05, "min_child_samples": 20}),
    ("LGBM_Wide", {"n_estimators": 1000, "num_leaves": 511, "max_depth": 8, "learning_rate": 0.05, "min_child_samples": 30}),
    ("LGBM_Fast", {"n_estimators": 600, "num_leaves": 127, "max_depth": 6, "learning_rate": 0.1, "min_child_samples": 50}),
]

lgbm_models = []
for name, params in lgbm_configs:
    print(f"\n  [{name}] Training...")
    t0 = time.time()
    
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    full_params = {
        **params,
        "objective": "binary",
        "metric": "binary_logloss",
        "is_unbalance": True,
        "num_threads": cpu_count,
        "verbose": -1,
    }
    
    callbacks = [lgb.log_evaluation(period=500), lgb.early_stopping(50)]
    model = lgb.train(full_params, train_data, valid_sets=[valid_data], callbacks=callbacks)
    
    elapsed = time.time() - t0
    
    # Predict
    y_prob = model.predict(X_test)
    y_pred = (y_prob >= 0.5).astype(int)
    
    r = evaluate(name, y_pred)
    r["train_time"] = elapsed
    r["prob"] = y_prob
    results.append(r)
    lgbm_models.append((name, model))
    
    # Save
    model.save_model(str(OUTPUT_DIR / f"{name}.txt"))
    print(f"  Saved: {name}.txt ({elapsed:.1f}s)")
    gc.collect()


# ── 2. XGBoost (2 variants, GPU — 12GB should handle it) ─────────────────────
print("\n" + "=" * 70)
print("  TRAINING: XGBoost (2 variants, GPU CUDA)")
print("=" * 70)
import xgboost as xgb

xgb_configs = [
    ("XGB_Deep", {"n_estimators": 1200, "max_depth": 10, "learning_rate": 0.05}),
    ("XGB_Balanced", {"n_estimators": 800, "max_depth": 8, "learning_rate": 0.1}),
]

xgb_models = []
for name, params in xgb_configs:
    print(f"\n  [{name}] Training (GPU)...")
    t0 = time.time()
    
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    full_params = {
        **params,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "device": "cuda",  # GPU acceleration
        "scale_pos_weight": (y_train == 0).sum() / (y_train == 1).sum(),
    }
    
    model = xgb.train(
        full_params, dtrain,
        num_boost_round=params["n_estimators"],
        evals=[(dtest, "valid")],
        early_stopping_rounds=50,
        verbose_eval=200,
    )
    
    elapsed = time.time() - t0
    
    # Predict
    y_prob = model.predict(dtest)
    y_pred = (y_prob >= 0.5).astype(int)
    
    r = evaluate(name, y_pred)
    r["train_time"] = elapsed
    r["prob"] = y_prob
    results.append(r)
    xgb_models.append((name, model))
    
    # Save
    model.save_model(str(OUTPUT_DIR / f"{name}.json"))
    print(f"  Saved: {name}.json ({elapsed:.1f}s)")
    gc.collect()


# ── 3. CatBoost (GPU) ────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  TRAINING: CatBoost (GPU)")
print("=" * 70)
from catboost import CatBoostClassifier, Pool

print(f"\n  [CatBoost_Deep] Training (GPU)...")
t0 = time.time()

cat_model = CatBoostClassifier(
    iterations=1500,
    learning_rate=0.05,
    depth=10,
    loss_function='Logloss',
    eval_metric='Logloss',
    task_type='GPU',
    devices='0',
    auto_class_weights='Balanced',
    verbose=200,
    early_stopping_rounds=50,
)

cat_model.fit(X_train, y_train, eval_set=(X_test, y_test), use_best_model=True)
elapsed = time.time() - t0

y_prob_cat = cat_model.predict_proba(X_test)[:, 1]
y_pred = (y_prob_cat >= 0.5).astype(int)

r = evaluate("CatBoost_Deep", y_pred)
r["train_time"] = elapsed
r["prob"] = y_prob_cat
results.append(r)

cat_model.save_model(str(OUTPUT_DIR / "CatBoost_Deep.cbm"))
print(f"  Saved: CatBoost_Deep.cbm ({elapsed:.1f}s)")
gc.collect()


# ── 4. PyTorch MLP (GPU) ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  TRAINING: PyTorch MLP (GPU)")
print("=" * 70)
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

device = torch.device(TORCH_DEVICE)
print(f"  Device: {device}")

class MLPNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 1),
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)

print(f"\n  [MLP_Deep] Training...")
t0 = time.time()

# Convert to tensors
X_train_t = torch.FloatTensor(X_train).to(device)
y_train_t = torch.FloatTensor(y_train).to(device)
X_test_t = torch.FloatTensor(X_test).to(device)

# DataLoader with batches that fit in 12GB VRAM
batch_size = 8192
train_dataset = TensorDataset(X_train_t, y_train_t)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

model_mlp = MLPNet(X_train.shape[1]).to(device)
optimizer = torch.optim.Adam(model_mlp.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([(y_train==0).sum()/(y_train==1).sum()]).to(device))

best_f1 = 0
patience = 0
max_patience = 7

for epoch in range(30):
    model_mlp.train()
    total_loss = 0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        out = model_mlp(X_batch)
        loss = criterion(out, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    # Evaluate
    model_mlp.eval()
    with torch.no_grad():
        # Predict in chunks to avoid OOM
        y_prob_mlp = []
        for i in range(0, len(X_test_t), batch_size):
            chunk = X_test_t[i:i+batch_size]
            y_prob_mlp.append(torch.sigmoid(model_mlp(chunk)).cpu().numpy())
        y_prob_mlp = np.concatenate(y_prob_mlp)
        y_pred_mlp = (y_prob_mlp >= 0.5).astype(int)
        f1 = f1_score(y_test, y_pred_mlp, zero_division=0)
        acc = accuracy_score(y_test, y_pred_mlp)
    
    avg_loss = total_loss / len(train_loader)
    scheduler.step(avg_loss)
    print(f"    Epoch {epoch+1:02d} | Loss: {avg_loss:.4f} | Acc: {acc*100:.2f}% | F1: {f1*100:.2f}%")
    
    if f1 > best_f1:
        best_f1 = f1
        torch.save(model_mlp.state_dict(), str(OUTPUT_DIR / "MLP_Deep.pth"))
        patience = 0
    else:
        patience += 1
        if patience >= max_patience:
            print(f"    Early stopping at epoch {epoch+1}")
            break

elapsed = time.time() - t0

# Final eval with best model
model_mlp.load_state_dict(torch.load(str(OUTPUT_DIR / "MLP_Deep.pth")))
model_mlp.eval()
with torch.no_grad():
    y_prob_mlp = []
    for i in range(0, len(X_test_t), batch_size):
        chunk = X_test_t[i:i+batch_size]
        y_prob_mlp.append(torch.sigmoid(model_mlp(chunk)).cpu().numpy())
    y_prob_mlp = np.concatenate(y_prob_mlp)
    y_pred_mlp = (y_prob_mlp >= 0.5).astype(int)

r = evaluate("MLP_Deep", y_pred_mlp)
r["train_time"] = elapsed
r["prob"] = y_prob_mlp
results.append(r)
print(f"  Saved: MLP_Deep.pth ({elapsed:.1f}s)")

# Cleanup GPU memory
del X_train_t, y_train_t, X_test_t, model_mlp
torch.cuda.empty_cache()
gc.collect()


# ═══════════════════════════════════════════════════════════════════════════════
# ENSEMBLE EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ENSEMBLE EVALUATION")
print("=" * 70)

# Collect all probabilities
all_probs = [r["prob"] for r in results]
model_names = [r["name"] for r in results]

# Soft voting (mean of all probabilities)
soft_vote_prob = np.mean(all_probs, axis=0)
soft_vote_pred = (soft_vote_prob >= 0.5).astype(int)

print("\n  Method: Soft Voting (all 7 models)")
r_ensemble = evaluate("Soft_Voting_7Model", soft_vote_pred)

# Also try without MLP (6-model like before)
probs_no_mlp = [r["prob"] for r in results if r["name"] != "MLP_Deep"]
soft_vote_6 = np.mean(probs_no_mlp, axis=0)
soft_vote_6_pred = (soft_vote_6 >= 0.5).astype(int)
print("\n  Method: Soft Voting (6 models, no MLP)")
evaluate("Soft_Voting_6Model", soft_vote_6_pred)

# Confusion matrix for best
cm = confusion_matrix(y_test, soft_vote_pred)
print(f"\n  Confusion Matrix (7-model):")
print(f"    TP: {cm[1,1]:,} | FN: {cm[1,0]:,}")
print(f"    FP: {cm[0,1]:,} | TN: {cm[0,0]:,}")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

# Save ensemble results JSON
ensemble_results = {
    "best_method": "soft_voting_7model",
    "best_metrics": {
        "accuracy": r_ensemble["accuracy"],
        "precision": r_ensemble["precision"],
        "recall": r_ensemble["recall"],
        "f1": r_ensemble["f1"],
        "tp": int(cm[1,1]),
        "tn": int(cm[0,0]),
        "fp": int(cm[0,1]),
        "fn": int(cm[1,0]),
    },
    "model_metrics": [{k: v for k, v in r.items() if k != "prob"} for r in results],
    "training_hardware": f"Ryzen 9 9955HX | {gpu_name} 12GB | 32GB DDR5",
    "training_date": time.strftime("%Y-%m-%d"),
    "total_training_time_min": sum(r["train_time"] for r in results) / 60,
}

with open(str(OUTPUT_DIR / "ensemble_results.json"), "w") as f:
    json.dump(ensemble_results, f, indent=2)

# Save MLP metrics separately
mlp_r = next(r for r in results if r["name"] == "MLP_Deep")
with open(str(OUTPUT_DIR / "MLP_Deep_metrics.pkl"), "wb") as f:
    pickle.dump({k: v for k, v in mlp_r.items() if k != "prob"}, f)

print("\n" + "═" * 70)
print(f"  TRAINING COMPLETE")
print(f"  Total time: {sum(r['train_time'] for r in results)/60:.1f} minutes")
print(f"  Best ensemble accuracy: {r_ensemble['accuracy']*100:.3f}%")
print(f"  Models saved to: {OUTPUT_DIR}")
print("═" * 70)
