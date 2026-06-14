"""
CYPHRA — PyTorch MLP Training Script
Target: >99% detection accuracy
Evaluates with DataLoader carefully to guarantee it stays deep within 8GB VRAM.
"""

import numpy as np
import pickle
import time
import os
import gc
import sys
import warnings
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = SCRIPT_DIR / "preprocessed_data.npz"
MODEL_DIR = SCRIPT_DIR / "trained_models"
MODEL_DIR.mkdir(exist_ok=True)

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

def train_mlp_isolated(X_tr, y_tr, X_te, y_te, name):
    print(f"\n   [PyTorch MLP] {name}...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"      GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

    n_pos = int((y_tr == 1).sum() + 1)
    n_neg = int((y_tr == 0).sum() + 1)
    pos_weight = torch.tensor([n_neg / n_pos], dtype=torch.float32).to(device)

    bs = 8192 if torch.cuda.is_available() else 4096
    
    # Load into DataLoader chunks to prevent massive array mirroring
    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32)
    train_loader = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=bs, shuffle=True)
    del X_tr, y_tr, X_tr_t, y_tr_t; gc.collect()

    X_te_t = torch.tensor(X_te, dtype=torch.float32)
    y_te_t = torch.tensor(y_te, dtype=torch.float32)
    test_loader = DataLoader(TensorDataset(X_te_t, y_te_t), batch_size=bs, shuffle=False)
    # Don't delete X_te yet, needed for calc_metrics later safely
    
    model = CyberMLP(X_te.shape[1]).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    best_f1, patience, stall_count = 0.0, 5, 0

    start = time.time()
    for epoch in range(50):
        model.train()
        train_loss = 0.0
        for b_x, b_y in train_loader:
            optimizer.zero_grad()
            y_pred_logit = model(b_x.to(device))
            loss = criterion(y_pred_logit, b_y.to(device))
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # EVALUATION (IN BATCHES TO PREVENT 14 GB OOM)
        model.eval()
        val_preds = []
        with torch.no_grad():
            for b_x, _ in test_loader:
                logits = model(b_x.to(device))
                probs = torch.sigmoid(logits).cpu().numpy()
                val_preds.append(probs)
        
        y_proba = np.concatenate(val_preds)
        y_p = (y_proba > 0.5).astype(int)
        met = calc_metrics(y_te, y_p)
        scheduler.step(met["f1"])

        print(f"      Epoch {epoch+1:02d} | Loss: {train_loss/len(train_loader):.4f} | Acc: {met['accuracy']*100:.2f}% | F1: {met['f1']*100:.2f}%")

        if met["f1"] > best_f1:
            best_f1 = met["f1"]
            stall_count = 0
            torch.save(model.state_dict(), str(MODEL_DIR / f"{name}.pth"))
            with open(MODEL_DIR / f"{name}_metrics.pkl", "wb") as f:
                pickle.dump(met, f)
        else:
            stall_count += 1
            if stall_count >= patience:
                print(f"      Early stopping at epoch {epoch+1}")
                break

    print(f"      {name} Training Time: {time.time()-start:.1f}s")
    del model, train_loader, test_loader; gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

def main():
    print("=" * 70)
    print("  CYPHRA — Training PyTorch Array")
    print("=" * 70)
    
    print(f"Loading {INPUT_FILE.name}...")
    data = np.load(INPUT_FILE, allow_pickle=True)
    X, y_binary = data["X"], data["y_binary"]
    X = X.astype(np.float32)
    y_binary = y_binary.astype(np.float32)
    del data; gc.collect()

    X_train, X_test, y_train, y_test = stratified_split(X, y_binary)
    del X, y_binary; gc.collect()

    train_mlp_isolated(X_train, y_train, X_test, y_test, "MLP_Deep")

if __name__ == "__main__":
    main()