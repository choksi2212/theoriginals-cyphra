"""
CYPHRA — XGBoost Training Script
Target: >99% detection accuracy
Runs strictly in isolation to guarantee maximum 8GB VRAM availability without fragmentation.
"""

import numpy as np
import pickle
import time
import os
import gc
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = SCRIPT_DIR / "preprocessed_data.npz"
MODEL_DIR = SCRIPT_DIR / "trained_models"
MODEL_DIR.mkdir(exist_ok=True)

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

def stratified_split(X, y, test_size=0.2, seed=42):
    print(f"\nStratified Train/Test Split ({int((1-test_size)*100)}/{int(test_size*100)})...")
    from sklearn.model_selection import StratifiedShuffleSplit
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(X, y))
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    return X_train, X_test, y_train, y_test

def train_xgboost(X_tr, y_tr, X_te, y_te, name, params):
    import xgboost as xgb
    print(f"\n   [XGBoost] {name}...")
    params["tree_method"] = "hist"
    params["device"] = "cuda"

    n_pos, n_neg = int((y_tr == 1).sum()), int((y_tr == 0).sum())
    params["scale_pos_weight"] = n_neg / max(1, n_pos)
    n_est = params.pop("n_estimators", 500)

    # To save memory, use PyArrow or specify optimal DMatrix settings
    # For GPU out-of-memory, XGBoost's QDF format is lighter than DMatrix
    print("      Loading DMatrix explicitly to VRAM...")
    dtrain = xgb.DMatrix(X_tr, label=y_tr)
    # Free X_tr to save RAM mapping to VRAM
    del X_tr, y_tr; gc.collect()
    
    dtest = xgb.DMatrix(X_te, label=y_te)

    start = time.time()
    model = xgb.train(params, dtrain, num_boost_round=n_est,
                      evals=[(dtest, "valid")], early_stopping_rounds=50, verbose_eval=50)
    train_time = time.time() - start

    y_proba = model.predict(dtest)
    y_pred = (y_proba > 0.5).astype(int)
    met = calc_metrics(y_te, y_pred)
    
    print(f"      {name}: Acc={met['accuracy']*100:.2f}% | F1={met['f1']*100:.2f}% | {train_time:.1f}s")
    model.save_model(str(MODEL_DIR / f"{name}.json"))
    
    # Save metrics independently
    with open(MODEL_DIR / f"{name}_metrics.pkl", "wb") as f:
        pickle.dump(met, f)
    
    del dtrain, dtest, model; gc.collect()
    import torch; torch.cuda.empty_cache() if torch.cuda.is_available() else None

def main():
    print("=" * 70)
    print("  CYPHRA — Training XGBoost Array")
    print("=" * 70)
    
    print(f"Loading {INPUT_FILE.name}...")
    data = np.load(INPUT_FILE, allow_pickle=True)
    X, y_binary = data["X"], data["y_binary"]
    # Cast here immediately to save memory
    X = X.astype(np.float32)
    y_binary = y_binary.astype(np.float32)
    del data; gc.collect()

    X_train, X_test, y_train, y_test = stratified_split(X, y_binary)
    del X, y_binary; gc.collect()

    configs = [
        ("XGB_Deep", {"objective": "binary:logistic", "eval_metric": "logloss",
            "n_estimators": 1200, "learning_rate": 0.03, "max_depth": 10,
            "min_child_weight": 3, "subsample": 0.8, "colsample_bytree": 0.7,
            "reg_alpha": 0.05, "reg_lambda": 0.5, "gamma": 0.1}),
        ("XGB_Balanced", {"objective": "binary:logistic", "eval_metric": "logloss",
            "n_estimators": 800, "learning_rate": 0.05, "max_depth": 8,
            "min_child_weight": 5, "subsample": 0.75, "colsample_bytree": 0.8,
            "reg_alpha": 0.1, "reg_lambda": 1.0, "gamma": 0.2})
    ]

    for name, params in configs:
        train_xgboost(X_train.copy(), y_train.copy(), X_test, y_test, name, params)

if __name__ == "__main__":
    main()