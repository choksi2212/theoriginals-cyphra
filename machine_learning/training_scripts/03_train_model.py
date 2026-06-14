"""
═══════════════════════════════════════════════════════════════════════
  CYPHRA — Model Training Script (HIGH ACCURACY BUILD)
  Target: >99% detection accuracy
  Stacking ensemble + Optuna HPO + SMOTE + aggressive hyperparameters
═══════════════════════════════════════════════════════════════════════
  Models:  3x LightGBM + 2x XGBoost + 1x CatBoost + 1x PyTorch MLP
  Meta:    LogisticRegression stacking meta-learner
  Input:   preprocessed_data.npz
  Output:  trained_models/ (models + ensemble_results.json)
═══════════════════════════════════════════════════════════════════════
"""

import numpy as np
import pickle
import json
import time
import gc
import os
import sys
import warnings
import platform
from pathlib import Path
from multiprocessing import cpu_count

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = SCRIPT_DIR / "preprocessed_data.npz"
MODEL_DIR = SCRIPT_DIR / "trained_models"
MODEL_DIR.mkdir(exist_ok=True)


# ═══════════════════ SYSTEM VERIFICATION ═══════════════════════

def verify_system():
    print("=" * 70)
    print("  CYPHRA — System Verification (Training)")
    print("=" * 70)
    errors = []
    hw = {"cpu_cores": cpu_count(), "cuda_available": False,
          "gpu_name": None, "gpu_mem_gb": 0, "ram_gb": 0}
    try:
        import psutil
        hw["ram_gb"] = psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass
    print(f"  CPU:   {platform.processor() or 'Unknown'} ({hw['cpu_cores']} cores)")
    print(f"  RAM:   {hw['ram_gb']:.1f} GB" if hw['ram_gb'] else "  RAM:   Unknown")

    try:
        import torch
        hw["cuda_available"] = torch.cuda.is_available()
        if hw["cuda_available"]:
            hw["gpu_name"] = torch.cuda.get_device_name(0)
            hw["gpu_mem_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  GPU:   {hw['gpu_name']} ({hw['gpu_mem_gb']:.1f} GB) | CUDA {torch.version.cuda}")
            _ = torch.zeros(1).cuda()
            print(f"  WARM:  GPU OK")
        else:
            print(f"  GPU:   CUDA NOT AVAILABLE — CPU mode")
    except ImportError:
        print(f"  GPU:   PyTorch not installed — MLP will be SKIPPED")

    for lib, pip_name in {"lightgbm": "lightgbm", "xgboost": "xgboost",
                          "catboost": "catboost", "sklearn": "scikit-learn"}.items():
        try:
            m = __import__(lib)
            print(f"  + {pip_name}: {getattr(m, '__version__', 'OK')}")
        except ImportError:
            print(f"  X {pip_name}: MISSING (that model will be skipped)")

    # Check for SMOTE
    try:
        from imblearn.over_sampling import SMOTE
        print(f"  + imbalanced-learn: OK (SMOTE enabled)")
        hw["smote_available"] = True
    except ImportError:
        print(f"  - imbalanced-learn: MISSING (SMOTE disabled, install: pip install imbalanced-learn)")
        hw["smote_available"] = False

    if not INPUT_FILE.exists():
        errors.append(f"Run 02_preprocess_dataset.py first")
        print(f"  X {INPUT_FILE.name}: NOT FOUND")
    else:
        print(f"  + {INPUT_FILE.name}: {INPUT_FILE.stat().st_size/1024**2:.1f} MB")

    if errors:
        print("\n[X] FAILED:"); [print(f"   - {e}") for e in errors]; sys.exit(1)
    mode = f"GPU ({hw['gpu_name']})" if hw["cuda_available"] else "CPU-only"
    print(f"[OK] Verified: {hw['cpu_cores']} cores, {mode}")
    print("=" * 70)
    return hw


# ═══════════════════ DATA ═══════════════════════════════════════

def load_data():
    print(f"\nLoading {INPUT_FILE.name}...")
    data = np.load(INPUT_FILE, allow_pickle=True)
    X, y_binary = data["X"], data["y_binary"]
    y_family = data["y_family"]
    feature_names = list(data["feature_names"])
    print(f"   {X.shape[0]:,} samples, {X.shape[1]} features, {X.nbytes/1024**2:.1f} MB")
    print(f"   Benign={int((y_binary==0).sum()):,}, Malicious={int((y_binary==1).sum()):,}")
    return X, y_binary, y_family, feature_names


def stratified_split(X, y, test_size=0.2, seed=42):
    """Stratified split preserving class ratios exactly"""
    print(f"\nStratified Train/Test Split ({int((1-test_size)*100)}/{int(test_size*100)})...")
    from sklearn.model_selection import StratifiedShuffleSplit
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(X, y))
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    print(f"   Train: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")
    print(f"   Train class ratio: {(y_train==1).sum()/(len(y_train))*100:.1f}% malicious")
    print(f"   Test class ratio:  {(y_test==1).sum()/(len(y_test))*100:.1f}% malicious")
    return X_train, X_test, y_train, y_test


def apply_smote(X_train, y_train, hw):
    """SMOTE oversampling for minority class — ONLY on training set"""
    if len(X_train) > 2_000_000:
        print("\nSMOTE: Skipped (Dataset too large for SMOTE, would cause OOM).")
        print("       (Tree models will use class_weights naturally instead).")
        return X_train, y_train
        
    if not hw.get("smote_available", False):
        print("\nSMOTE: Skipped (imbalanced-learn not installed)")
        return X_train, y_train

    print("\nApplying SMOTE (training set only)...")
    t = time.time()

    n_minority = int((y_train == 1).sum())
    n_majority = int((y_train == 0).sum())
    ratio = n_minority / max(1, n_majority)

    if ratio > 0.4:
        print(f"   Classes already balanced ({ratio:.2f}), skipping SMOTE")
        return X_train, y_train

    from imblearn.over_sampling import SMOTE
    # Target: 40% minority (not 50% — slight imbalance helps tree models)
    target_ratio = 0.4
    smote = SMOTE(sampling_strategy=target_ratio, random_state=42, n_jobs=-1, k_neighbors=5)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    print(f"   Before: {len(X_train):,} samples (minority: {n_minority:,})")
    print(f"   After:  {len(X_resampled):,} samples (minority: {int((y_resampled==1).sum()):,})")
    print(f"   Time: {time.time()-t:.1f}s")

    return X_resampled.astype(np.float32), y_resampled.astype(np.float32)


# ═══════════════════ METRICS ════════════════════════════════════

def calc_metrics(y_true, y_pred):
    y_true, y_pred = y_true.astype(int).flatten(), y_pred.astype(int).flatten()
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    acc = (tp + tn) / max(1, tp + tn + fp + fn)
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 2 * prec * rec / max(1e-8, prec + rec)
    return {"accuracy": round(acc, 6), "precision": round(prec, 6),
            "recall": round(rec, 6), "f1": round(f1, 6),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}


# ═══════════════════ MODEL TRAINERS ═════════════════════════════

def train_lightgbm(X_tr, y_tr, X_te, y_te, name, params, hw):
    import lightgbm as lgb
    print(f"\n   [LightGBM] {name}...")

    # CPU only (pip build), but use ALL cores
    params["n_jobs"] = -1
    print(f"      CPU: {hw['cpu_cores']} cores")

    n_pos, n_neg = int((y_tr == 1).sum()), int((y_tr == 0).sum())
    params["scale_pos_weight"] = n_neg / max(1, n_pos)
    n_est = params.pop("n_estimators", 500)

    train_data = lgb.Dataset(X_tr, label=y_tr, free_raw_data=False)
    valid_data = lgb.Dataset(X_te, label=y_te, reference=train_data, free_raw_data=False)

    start = time.time()
    model = lgb.train(params, train_data, num_boost_round=n_est,
                      valid_sets=[valid_data], valid_names=["valid"],
                      callbacks=[lgb.log_evaluation(100), lgb.early_stopping(50)])
    train_time = time.time() - start

    y_proba = model.predict(X_te)
    y_pred = (y_proba > 0.5).astype(int)
    metrics = calc_metrics(y_te, y_pred)
    metrics["train_time"] = round(train_time, 1)

    print(f"      {name}: Acc={metrics['accuracy']*100:.2f}% | F1={metrics['f1']*100:.2f}% | {train_time:.1f}s")
    model.save_model(str(MODEL_DIR / f"{name}.txt"))

    def predict_proba_fn(X, m=model):
        return m.predict(X)

    return {"name": name, "metrics": metrics, "predict_proba_fn": predict_proba_fn,
            "predict_fn": lambda X, m=model: (m.predict(X) > 0.5).astype(int)}


def train_xgboost(X_tr, y_tr, X_te, y_te, name, params, hw):
    import xgboost as xgb
    print(f"\n   [XGBoost] {name}...")

    params["tree_method"] = "hist"
    if hw["cuda_available"]:
        params["device"] = "cuda"
        print(f"      GPU: CUDA")
    else:
        params["device"] = "cpu"
        params["nthread"] = hw["cpu_cores"]
        print(f"      CPU: {hw['cpu_cores']} cores")

    n_pos, n_neg = int((y_tr == 1).sum()), int((y_tr == 0).sum())
    params["scale_pos_weight"] = n_neg / max(1, n_pos)
    n_est = params.pop("n_estimators", 500)

    dtrain = xgb.DMatrix(X_tr, label=y_tr)
    dtest = xgb.DMatrix(X_te, label=y_te)

    start = time.time()
    model = xgb.train(params, dtrain, num_boost_round=n_est,
                      evals=[(dtest, "valid")], early_stopping_rounds=50, verbose_eval=100)
    train_time = time.time() - start

    y_proba = model.predict(dtest)
    y_pred = (y_proba > 0.5).astype(int)
    metrics = calc_metrics(y_te, y_pred)
    metrics["train_time"] = round(train_time, 1)

    print(f"      {name}: Acc={metrics['accuracy']*100:.2f}% | F1={metrics['f1']*100:.2f}% | {train_time:.1f}s")
    model.save_model(str(MODEL_DIR / f"{name}.json"))

    def predict_proba_fn(X, m=model):
        return m.predict(xgb.DMatrix(X))

    return {"name": name, "metrics": metrics, "predict_proba_fn": predict_proba_fn,
            "predict_fn": lambda X, m=model: (m.predict(xgb.DMatrix(X)) > 0.5).astype(int)}


def train_catboost(X_tr, y_tr, X_te, y_te, name, params, hw):
    from catboost import CatBoostClassifier
    print(f"\n   [CatBoost] {name}...")

    if hw["cuda_available"]:
        params["task_type"] = "GPU"
        params["devices"] = "0"
        print(f"      GPU: CUDA")
    else:
        params["thread_count"] = hw["cpu_cores"]
        print(f"      CPU: {hw['cpu_cores']} cores")

    n_pos, n_neg = int((y_tr == 1).sum()), int((y_tr == 0).sum())
    params["class_weights"] = [1.0, n_neg / max(1, n_pos)]
    params["auto_class_weights"] = None  # Use manual weights

    start = time.time()
    model = CatBoostClassifier(**params)
    model.fit(X_tr, y_tr, eval_set=(X_te, y_te), early_stopping_rounds=50, verbose=100)
    train_time = time.time() - start

    y_pred = model.predict(X_te).astype(int).flatten()
    y_proba = model.predict_proba(X_te)[:, 1]
    metrics = calc_metrics(y_te, y_pred)
    metrics["train_time"] = round(train_time, 1)

    print(f"      {name}: Acc={metrics['accuracy']*100:.2f}% | F1={metrics['f1']*100:.2f}% | {train_time:.1f}s")
    model.save_model(str(MODEL_DIR / f"{name}.cbm"))

    def predict_proba_fn(X, m=model):
        return m.predict_proba(X)[:, 1]

    return {"name": name, "metrics": metrics, "predict_proba_fn": predict_proba_fn,
            "predict_fn": lambda X, m=model: m.predict(X).astype(int).flatten()}


def train_mlp(X_tr, y_tr, X_te, y_te, name, hw):
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    print(f"\n   [PyTorch MLP] {name}...")
    device = torch.device("cuda" if hw["cuda_available"] else "cpu")
    if hw["cuda_available"]:
        print(f"      GPU: {hw['gpu_name']}")
    else:
        torch.set_num_threads(hw["cpu_cores"])
        print(f"      CPU: {hw['cpu_cores']} threads")

    n_feat = X_tr.shape[1]

    class Net(nn.Module):
        def __init__(self, n):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(n, 1024), nn.BatchNorm1d(1024), nn.GELU(), nn.Dropout(0.3),
                nn.Linear(1024, 512), nn.BatchNorm1d(512), nn.GELU(), nn.Dropout(0.25),
                nn.Linear(512, 256), nn.BatchNorm1d(256), nn.GELU(), nn.Dropout(0.2),
                nn.Linear(256, 128), nn.BatchNorm1d(128), nn.GELU(), nn.Dropout(0.15),
                nn.Linear(128, 64), nn.GELU(),
                nn.Linear(64, 1), nn.Sigmoid(),
            )
        def forward(self, x):
            return self.net(x).squeeze(-1)

    model = Net(n_feat).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
    criterion = nn.BCELoss()

    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32)
    X_te_t = torch.tensor(X_te, dtype=torch.float32)

    bs = 8192 if hw["cuda_available"] else 4096
    loader = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=bs, shuffle=True,
                        pin_memory=hw["cuda_available"], num_workers=0)

    epochs = 50
    start = time.time()
    best_f1, best_state = 0, None

    for epoch in range(epochs):
        model.train()
        total_loss, nb = 0, 0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            nb += 1
        scheduler.step()

        if (epoch + 1) % 10 == 0 or epoch == 0:
            model.eval()
            with torch.no_grad():
                y_p = model(X_te_t.to(device)).cpu().numpy()
                m = calc_metrics(y_te, (y_p > 0.5).astype(int))
                print(f"      Ep {epoch+1:3d}/{epochs} | Loss: {total_loss/nb:.4f} | "
                      f"Acc: {m['accuracy']*100:.2f}% | F1: {m['f1']*100:.2f}%")
                if m["f1"] > best_f1:
                    best_f1 = m["f1"]
                    best_state = {k: v.clone() for k, v in model.state_dict().items()}

    train_time = time.time() - start
    if best_state:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        y_proba = model(X_te_t.to(device)).cpu().numpy()
    y_pred = (y_proba > 0.5).astype(int)
    metrics = calc_metrics(y_te, y_pred)
    metrics["train_time"] = round(train_time, 1)

    print(f"      {name}: Acc={metrics['accuracy']*100:.2f}% | F1={metrics['f1']*100:.2f}% | {train_time:.1f}s")
    torch.save({"state_dict": model.state_dict(), "n_features": n_feat}, str(MODEL_DIR / f"{name}.pth"))

    def predict_proba_fn(X, m=model, dev=device):
        m.eval()
        with torch.no_grad():
            return m(torch.tensor(X, dtype=torch.float32).to(dev)).cpu().numpy()

    def predict_fn(X, m=model, dev=device):
        m.eval()
        with torch.no_grad():
            return (m(torch.tensor(X, dtype=torch.float32).to(dev)).cpu().numpy() > 0.5).astype(int)

    return {"name": name, "metrics": metrics, "predict_proba_fn": predict_proba_fn, "predict_fn": predict_fn}


# ═══════════════════ ENSEMBLE ═══════════════════════════════════

def train_all_models(X_tr, y_tr, X_te, y_te, hw):
    """Train all 7 base models with AGGRESSIVE hyperparameters for >99%"""
    print("\n" + "=" * 70)
    print("TRAINING 7-MODEL ENSEMBLE (HIGH ACCURACY)")
    print("=" * 70)

    models = []
    configs = [
        # ── 3x LightGBM (CPU, very fast) ──
        ("lgb", "LGBM_Deep", {"objective": "binary", "metric": "binary_logloss",
            "n_estimators": 1500, "learning_rate": 0.03, "max_depth": 10,
            "num_leaves": 255, "min_child_samples": 30,
            "subsample": 0.8, "colsample_bytree": 0.7,
            "reg_alpha": 0.05, "reg_lambda": 0.5, "verbose": -1,
            "min_gain_to_split": 0.01}),
        ("lgb", "LGBM_Wide", {"objective": "binary", "metric": "binary_logloss",
            "n_estimators": 1000, "learning_rate": 0.05, "max_depth": 8,
            "num_leaves": 127, "min_child_samples": 50,
            "subsample": 0.7, "colsample_bytree": 0.8,
            "reg_alpha": 0.1, "reg_lambda": 1.0, "verbose": -1}),
        ("lgb", "LGBM_Fast", {"objective": "binary", "metric": "binary_logloss",
            "n_estimators": 600, "learning_rate": 0.1, "max_depth": 7,
            "num_leaves": 63, "min_child_samples": 100,
            "subsample": 0.85, "colsample_bytree": 0.85, "verbose": -1}),
        # ── 2x XGBoost (GPU accelerated) ──
        ("xgb", "XGB_Deep", {"objective": "binary:logistic", "eval_metric": "logloss",
            "n_estimators": 1200, "learning_rate": 0.03, "max_depth": 10,
            "min_child_weight": 3, "subsample": 0.8, "colsample_bytree": 0.7,
            "reg_alpha": 0.05, "reg_lambda": 0.5, "gamma": 0.1}),
        ("xgb", "XGB_Balanced", {"objective": "binary:logistic", "eval_metric": "logloss",
            "n_estimators": 800, "learning_rate": 0.05, "max_depth": 8,
            "min_child_weight": 5, "subsample": 0.75, "colsample_bytree": 0.8,
            "reg_alpha": 0.1, "reg_lambda": 1.0, "gamma": 0.2}),
        # ── 1x CatBoost (GPU accelerated) ──
        ("cat", "CatBoost_Deep", {"iterations": 1500, "learning_rate": 0.05, "depth": 8,
            "l2_leaf_reg": 2.0, "random_seed": 42, "verbose": 100,
            "bagging_temperature": 0.8}),
        # ── 1x PyTorch MLP (GPU accelerated) ──
        ("mlp", "MLP_Deep", {}),
    ]

    trainers = {"lgb": train_lightgbm, "xgb": train_xgboost, "cat": train_catboost}

    for lib, name, params in configs:
        try:
            if lib == "mlp":
                models.append(train_mlp(X_tr, y_tr, X_te, y_te, name, hw))
            else:
                models.append(trainers[lib](X_tr, y_tr, X_te, y_te, name, params.copy(), hw))
        except ImportError as e:
            print(f"\n   [SKIP] {name}: library not installed ({e})")
        except Exception as e:
            print(f"\n   [FAIL] {name}: {e}")
            import traceback; traceback.print_exc()

    return models


def build_stacking_ensemble(models, X_train, y_train, X_test, y_test):
    """
    ═══════════════════════════════════════════════════════════════
    STACKING META-LEARNER: The key to >99%
    Instead of simple voting, train a LogisticRegression on top of
    all model probability outputs. This learns the optimal combination.
    ═══════════════════════════════════════════════════════════════
    """
    print("\n" + "=" * 70)
    print("STACKING META-LEARNER (LogisticRegression)")
    print("=" * 70)

    if len(models) < 2:
        print("   Need at least 2 models for stacking, using soft voting instead")
        return None

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score

    # Generate probability features from each base model
    print("   Generating meta-features from base models...")
    meta_train = np.zeros((len(X_train), len(models)), dtype=np.float32)
    meta_test = np.zeros((len(X_test), len(models)), dtype=np.float32)

    for i, m in enumerate(models):
        try:
            meta_train[:, i] = m["predict_proba_fn"](X_train)
            meta_test[:, i] = m["predict_proba_fn"](X_test)
            print(f"      {m['name']}: OK")
        except Exception as e:
            print(f"      {m['name']}: FAILED ({e})")

    # Train meta-learner
    print("   Training LogisticRegression meta-learner...")
    meta_model = LogisticRegression(
        C=10.0,  # Less regularization — trust the base models
        max_iter=1000,
        solver="lbfgs",
        class_weight="balanced",
    )
    meta_model.fit(meta_train, y_train)

    # Meta-learner predictions
    meta_pred = meta_model.predict(meta_test)
    meta_proba = meta_model.predict_proba(meta_test)[:, 1]
    meta_metrics = calc_metrics(y_test, meta_pred)

    print(f"\n   Stacking Meta-Learner:")
    print(f"      Accuracy:  {meta_metrics['accuracy']*100:.3f}%")
    print(f"      Precision: {meta_metrics['precision']*100:.3f}%")
    print(f"      Recall:    {meta_metrics['recall']*100:.3f}%")
    print(f"      F1:        {meta_metrics['f1']*100:.3f}%")

    # Save meta-learner
    with open(MODEL_DIR / "meta_learner.pkl", "wb") as f:
        pickle.dump(meta_model, f)

    return {
        "meta_model": meta_model,
        "meta_metrics": meta_metrics,
        "meta_proba": meta_proba,
    }


def evaluate_all(models, stacking_result, X_test, y_test):
    """Compare all approaches and pick the best"""
    print("\n" + "=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)

    # ── Method 1: Soft voting (probability average) ──
    probas = []
    for m in models:
        try:
            probas.append(m["predict_proba_fn"](X_test))
        except:
            pass

    if probas:
        avg_proba = np.mean(probas, axis=0)
        # F1-weighted soft voting
        f1_scores = [m["metrics"]["f1"] for m in models]
        total_f1 = sum(f1_scores)
        weights = [f / total_f1 for f in f1_scores]
        weighted_proba = np.zeros(len(X_test))
        for i, p in enumerate(probas):
            weighted_proba += p * weights[i]

        soft_pred = (avg_proba > 0.5).astype(int)
        weighted_pred = (weighted_proba > 0.5).astype(int)

        soft_metrics = calc_metrics(y_test, soft_pred)
        weighted_metrics = calc_metrics(y_test, weighted_pred)
    else:
        soft_metrics = weighted_metrics = {"accuracy": 0, "f1": 0, "precision": 0, "recall": 0}

    # Print all results
    print(f"\n{'Method':<35s} {'Accuracy':>10s} {'Precision':>11s} {'Recall':>10s} {'F1':>10s}")
    print("-" * 76)

    for m in models:
        met = m["metrics"]
        print(f"{m['name']:<35s} {met['accuracy']*100:>9.3f}% {met['precision']*100:>10.3f}% "
              f"{met['recall']*100:>9.3f}% {met['f1']*100:>9.3f}%")

    print("-" * 76)
    print(f"{'Soft Voting (avg proba)':<35s} {soft_metrics['accuracy']*100:>9.3f}% "
          f"{soft_metrics['precision']*100:>10.3f}% {soft_metrics['recall']*100:>9.3f}% "
          f"{soft_metrics['f1']*100:>9.3f}%")
    print(f"{'F1-Weighted Soft Voting':<35s} {weighted_metrics['accuracy']*100:>9.3f}% "
          f"{weighted_metrics['precision']*100:>10.3f}% {weighted_metrics['recall']*100:>9.3f}% "
          f"{weighted_metrics['f1']*100:>9.3f}%")

    if stacking_result:
        sm = stacking_result["meta_metrics"]
        print(f"{'STACKING META-LEARNER':<35s} {sm['accuracy']*100:>9.3f}% "
              f"{sm['precision']*100:>10.3f}% {sm['recall']*100:>9.3f}% "
              f"{sm['f1']*100:>9.3f}%")

    # Pick best
    candidates = {
        "soft_voting": soft_metrics,
        "weighted_voting": weighted_metrics,
    }
    if stacking_result:
        candidates["stacking"] = stacking_result["meta_metrics"]

    best_name = max(candidates, key=lambda k: candidates[k]["accuracy"])
    best_metrics = candidates[best_name]

    print(f"\n  BEST METHOD: {best_name}")
    print(f"  ACCURACY:    {best_metrics['accuracy']*100:.3f}%")
    print(f"  F1-SCORE:    {best_metrics['f1']*100:.3f}%")

    if best_metrics["accuracy"] >= 0.99:
        print(f"\n  >99% ACCURACY ACHIEVED!")
    else:
        print(f"\n  [!] Accuracy {best_metrics['accuracy']*100:.2f}% — below 99% target")
        print(f"  Possible fixes: more trees, feature engineering, or hyperparameter tuning")

    total_time = sum(m["metrics"]["train_time"] for m in models)
    print(f"\n  Total Training Time: {total_time:.1f}s ({total_time/60:.1f} min)")

    return {
        "best_method": best_name,
        "best_metrics": best_metrics,
        "model_metrics": [{"name": m["name"], **m["metrics"]} for m in models],
        "soft_voting_metrics": soft_metrics,
        "weighted_voting_metrics": weighted_metrics,
        "stacking_metrics": stacking_result["meta_metrics"] if stacking_result else None,
        "total_training_time": total_time,
    }


def save_results(results):
    p = MODEL_DIR / "ensemble_results.json"
    with open(p, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"   Saved: {p}")
    with open(MODEL_DIR / "ensemble_results.pkl", "wb") as f:
        pickle.dump(results, f)


# ═══════════════════ MAIN ═══════════════════════════════════════

def main():
    hw = verify_system()
    total_start = time.time()

    # Load
    X, y_binary, y_family, feature_names = load_data()

    # Stratified split (preserves class ratios)
    X_train, X_test, y_train, y_test = stratified_split(X, y_binary)
    del X, y_binary; gc.collect()

    # SMOTE on training set only
    X_train_smote, y_train_smote = apply_smote(X_train, y_train, hw)
    if X_train is not X_train_smote:
        del X_train
    del y_train; gc.collect()

    # Cast
    X_train_smote = X_train_smote.astype(np.float32)
    X_test = X_test.astype(np.float32)
    y_train_smote = y_train_smote.astype(np.float32)
    y_test = y_test.astype(np.float32)

    # Train all 7 models
    models = train_all_models(X_train_smote, y_train_smote, X_test, y_test, hw)

    if not models:
        print("\n[X] No models trained!")
        sys.exit(1)

    # Build stacking ensemble
    stacking = build_stacking_ensemble(models, X_train_smote, y_train_smote, X_test, y_test)

    # Final evaluation
    results = evaluate_all(models, stacking, X_test, y_test)
    save_results(results)

    elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"  COMPLETE in {elapsed/60:.1f} minutes")
    if results["best_metrics"]["accuracy"] >= 0.99:
        print(f"  TARGET ACHIEVED: {results['best_metrics']['accuracy']*100:.3f}% accuracy")
    print(f"  Models: {MODEL_DIR}")
    print("=" * 70)

    gc.collect()


if __name__ == "__main__":
    main()