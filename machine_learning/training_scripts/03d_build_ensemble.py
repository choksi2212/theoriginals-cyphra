"""
CYPHRA — Stacking Ensemble Builder
Target: >99% detection accuracy
Loads all individually trained models and orchestrates the LogisticRegression Meta-Learner.
"""

import numpy as np
import pickle
import time
import os
import gc
import sys
import warnings
from pathlib import Path
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = SCRIPT_DIR / "preprocessed_data.npz"
MODEL_DIR = SCRIPT_DIR / "trained_models"

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

def get_predictions(name, X, y):
    """Load model and predict probabilities cleanly without holding model in memory."""
    print(f"   Gathering predictions from {name}...")
    import lightgbm as LGBM
    import xgboost as xgb
    import catboost as cb
    import torch
    import torch.nn as nn
    
    # Check if LightGBM
    if (MODEL_DIR / f"{name}.txt").exists():
        model = LGBM.Booster(model_file=str(MODEL_DIR / f"{name}.txt"))
        preds = model.predict(X)
        del model
        return preds
        
    # Check if XGBoost
    elif (MODEL_DIR / f"{name}.json").exists():
        model = xgb.Booster()
        model.load_model(str(MODEL_DIR / f"{name}.json"))
        dmat = xgb.DMatrix(X)
        preds = model.predict(dmat)
        del model, dmat
        return preds
        
    # Check if CatBoost
    elif (MODEL_DIR / f"{name}.cbm").exists():
        model = cb.CatBoostClassifier()
        model.load_model(str(MODEL_DIR / f"{name}.cbm"))
        preds = model.predict_proba(X)[:, 1]
        del model
        return preds
        
    # Check if PyTorch MLP
    elif (MODEL_DIR / f"{name}.pth").exists():
        class CyberMLP(nn.Module):
            def __init__(self, input_dim):
                super().__init__()
                self.net = nn.Sequential(
                    nn.Linear(input_dim, 512), nn.BatchNorm1d(512), nn.Mish(), nn.Dropout(0.4),
                    nn.Linear(512, 256), nn.BatchNorm1d(256), nn.Mish(), nn.Dropout(0.3),
                    nn.Linear(256, 128), nn.BatchNorm1d(128), nn.Mish(), nn.Dropout(0.2),
                    nn.Linear(128, 64), nn.BatchNorm1d(64), nn.Mish(), nn.Dropout(0.1),
                    nn.Linear(64, 1)
                )
            def forward(self, x):
                return self.net(x).squeeze(-1)
                
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = CyberMLP(X.shape[1]).to(device)
        model.load_state_dict(torch.load(str(MODEL_DIR / f"{name}.pth"), weights_only=True))
        model.eval()
        
        # Batch evaluation
        from torch.utils.data import TensorDataset, DataLoader
        loader = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32)), batch_size=8192)
        preds = []
        with torch.no_grad():
            for b_x, in loader:
                p = torch.sigmoid(model(b_x.to(device))).cpu().numpy()
                preds.append(p)
        del model, loader
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        return np.concatenate(preds)
        
    else:
        print(f"      [!] Model file for {name} not found, skipping...")
        return None

def main():
    print("=" * 70)
    print("  CYPHRA — Stacking Ensemble Builder")
    print("=" * 70)
    
    print(f"Loading {INPUT_FILE.name}...")
    data = np.load(INPUT_FILE, allow_pickle=True)
    X, y_binary = data["X"], data["y_binary"]
    X = X.astype(np.float32)
    del data; gc.collect()

    X_train, X_test, y_train, y_test = stratified_split(X, y_binary)
    del X, y_binary; gc.collect()

    expected_models = ["LGBM_Fast", "LGBM_Deep", "LGBM_Wide", "XGB_Deep", "XGB_Balanced", "CatBoost_Deep", "MLP_Deep"]
    
    meta_X_train = []
    meta_X_test = []
    
    for name in expected_models:
        tr_pred = get_predictions(name, X_train, y_train)
        te_pred = get_predictions(name, X_test, y_test)
        if tr_pred is not None and te_pred is not None:
            meta_X_train.append(tr_pred)
            meta_X_test.append(te_pred)
            
    if not meta_X_train:
        print("No models found. Run the standalone training scripts first.")
        sys.exit(1)

    print("\n   [META] Building Logistic Regression Stacking Ensemble...")
    # Stack features: shape becomes (n_samples, n_models)
    meta_X_train = np.column_stack(meta_X_train)
    meta_X_test = np.column_stack(meta_X_test)
    
    # Train Meta Learner
    meta_model = LogisticRegression(max_iter=1000, class_weight="balanced")
    
    t = time.time()
    meta_model.fit(meta_X_train, y_train)
    print(f"      Training Time: {time.time()-t:.1f}s")
    
    # Final Evaluate
    y_pred = meta_model.predict(meta_X_test)
    met = calc_metrics(y_test, y_pred)
    acc = met['accuracy'] * 100
    
    print("\n" + "=" * 70)
    print(f"  FINAL STACKING ENSEMBLE RESULTS")
    print("=" * 70)
    print(f"   Accuracy:  {acc:.4f}%" + (" 🌟 EXPECTATION MET!" if acc > 99.0 else ""))
    print(f"   Precision: {met['precision']*100:.3f}%")
    print(f"   Recall:    {met['recall']*100:.3f}%")
    print(f"   F1 Score:  {met['f1']*100:.3f}%")
    print("-" * 70)
    print(f"     Confusion Matrix:  TP:{met['tp']:,}  FP:{met['fp']:,}")
    print(f"                        FN:{met['fn']:,}  TN:{met['tn']:,}")
    print("=" * 70)

    # Save meta model
    with open(MODEL_DIR / "stacking_meta_model.pkl", "wb") as f:
        pickle.dump(meta_model, f)
        
    print(f"\n[OK] Meta model saved safely. Pipeline Complete.")

if __name__ == "__main__":
    main()