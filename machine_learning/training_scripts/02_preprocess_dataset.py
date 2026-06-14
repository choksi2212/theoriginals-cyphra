"""
═══════════════════════════════════════════════════════════════════
  CYPHRA — Preprocessing Script (HIGH ACCURACY BUILD)
  Target: >99% detection accuracy
  MEMORY-SAFE: Column-by-column in-place processing
═══════════════════════════════════════════════════════════════════
"""

import numpy as np
import pandas as pd
import pickle
import time
import gc
import warnings
import platform
import os
import sys
from pathlib import Path
from multiprocessing import cpu_count

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FILE = SCRIPT_DIR / "combined_dataset.parquet"
OUTPUT_FILE = SCRIPT_DIR / "preprocessed_data.npz"
SCALER_FILE = SCRIPT_DIR / "scaler.pkl"
METADATA_FILE = SCRIPT_DIR / "preprocessing_metadata.pkl"


# ═══════════════════ SYSTEM VERIFICATION ═══════════════════════

def verify_system():
    print("=" * 70)
    print("  CYPHRA — System Verification (Preprocessing)")
    print("=" * 70)
    errors = []
    hw = {"cpu_cores": cpu_count(), "cuda_available": False, "ram_gb": 0}
    try:
        import psutil
        hw["ram_gb"] = psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass
    print(f"  CPU:   {platform.processor() or 'Unknown'} ({hw['cpu_cores']} cores)")
    print(f"  RAM:   {hw['ram_gb']:.1f} GB" if hw["ram_gb"] else "  RAM:   Unknown")

    for lib in ["numpy", "pandas", "sklearn", "pyarrow"]:
        try:
            __import__(lib)
            print(f"  + {lib}: OK")
        except ImportError:
            errors.append(f"Missing: pip install {lib}")
            print(f"  X {lib}: MISSING")

    if not INPUT_FILE.exists():
        errors.append(f"Run 01_combine_datasets.py first")
        print(f"  X {INPUT_FILE.name}: NOT FOUND")
    else:
        print(f"  + {INPUT_FILE.name}: {INPUT_FILE.stat().st_size/1024**2:.1f} MB")

    if errors:
        print("\n[X] FAILED:"); [print(f"   - {e}") for e in errors]; sys.exit(1)
    print(f"[OK] System verified")
    print("=" * 70)
    return hw


# ═══════════════════ PREPROCESSING ════════════════════════════

def main():
    hw = verify_system()
    total_start = time.time()

    # ── Load ──
    print(f"\nLoading {INPUT_FILE.name}...")
    df = pd.read_parquet(INPUT_FILE)
    print(f"   {len(df):,} samples, {len(df.columns)} columns")

    meta_cols = ["label_binary", "label_family", "label_fine", "dataset_id"]

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Clean infinities + missing values (IN-PLACE, COL BY COL)
    # ═══════════════════════════════════════════════════════════
    print("\nStep 1: Cleaning infinities + missing values...")
    t = time.time()
    for col in df.columns:
        if col in meta_cols:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            # Downcast to float32 instantly to save memory
            df[col] = df[col].astype(np.float32)
            # Replace inf with nan inplace
            df[col].replace([np.inf, -np.inf], np.nan, inplace=True)
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)

    print(f"   Cleaning done ({time.time()-t:.1f}s)")
    gc.collect()

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Feature engineering (IN-PLACE)
    # ═══════════════════════════════════════════════════════════
    print("\nStep 2: Feature engineering (AGGRESSIVE)...")
    t = time.time()
    n_before = len(df.columns)

    def safe_div(a, b):
        return (a / (b + 1)).astype(np.float32)

    if "total_fwd_packets" in df.columns and "total_bwd_packets" in df.columns:
        df["fwd_bwd_packet_ratio"] = safe_div(df["total_fwd_packets"], df["total_bwd_packets"])
        df["total_packets"] = (df["total_fwd_packets"] + df["total_bwd_packets"]).astype(np.float32)
        df["fwd_packet_fraction"] = safe_div(df["total_fwd_packets"], df["total_packets"])

    if "total_length_fwd_packets" in df.columns and "total_length_bwd_packets" in df.columns:
        df["fwd_bwd_bytes_ratio"] = safe_div(df["total_length_fwd_packets"], df["total_length_bwd_packets"])
        df["total_bytes"] = (df["total_length_fwd_packets"] + df["total_length_bwd_packets"]).astype(np.float32)
        df["fwd_bytes_fraction"] = safe_div(df["total_length_fwd_packets"], df["total_bytes"])

    if "total_bytes" in df.columns and "flow_duration" in df.columns:
        df["bytes_per_second"] = safe_div(df["total_bytes"], df["flow_duration"])
    if "total_packets" in df.columns and "flow_duration" in df.columns:
        df["packets_per_second"] = safe_div(df["total_packets"], df["flow_duration"])

    if "fwd_pkt_len_mean" in df.columns and "bwd_pkt_len_mean" in df.columns:
        df["payload_ratio"] = safe_div(df["fwd_pkt_len_mean"], df["bwd_pkt_len_mean"])
        df["payload_diff"] = (df["fwd_pkt_len_mean"] - df["bwd_pkt_len_mean"]).astype(np.float32)

    if "flow_iat_mean" in df.columns and "flow_iat_std" in df.columns:
        df["iat_cv"] = safe_div(df["flow_iat_std"], df["flow_iat_mean"])

    if "fwd_header_length" in df.columns and "bwd_header_length" in df.columns:
        df["header_ratio"] = safe_div(df["fwd_header_length"], df["bwd_header_length"])

    if "total_length_fwd_packets" in df.columns and "total_fwd_packets" in df.columns:
        df["avg_fwd_pkt_size"] = safe_div(df["total_length_fwd_packets"], df["total_fwd_packets"])
    if "total_length_bwd_packets" in df.columns and "total_bwd_packets" in df.columns:
        df["avg_bwd_pkt_size"] = safe_div(df["total_length_bwd_packets"], df["total_bwd_packets"])

    if "dst_port" in df.columns:
        df["is_well_known_port"] = (df["dst_port"] < 1024).astype(np.float32)
        df["is_http_port"] = df["dst_port"].isin([80, 443, 8080, 8443]).astype(np.float32)
        df["is_dns_port"] = (df["dst_port"] == 53).astype(np.float32)
        df["dst_port_log"] = np.log1p(np.clip(df["dst_port"], 0, None)).astype(np.float32)

    skew_candidates = ["flow_duration", "total_fwd_packets", "total_bwd_packets",
                       "total_length_fwd_packets", "total_length_bwd_packets",
                       "total_bytes", "total_packets"]
    for col in skew_candidates:
        if col in df.columns:
            df[f"{col}_log"] = np.log1p(np.clip(df[col], 0, None)).astype(np.float32)

    for did in range(4):
        df[f"dataset_onehot_{did}"] = (df["dataset_id"] == did).astype(np.float32)

    all_feature_cols = [c for c in df.columns if c not in meta_cols and c != "label_fine"]
    print(f"   Created {len(df.columns) - n_before} new features ({time.time()-t:.1f}s)")
    gc.collect()

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Remove zero-variance (COL BY COL to save RAM)
    # ═══════════════════════════════════════════════════════════
    print("\nStep 3: Removing zero-variance features...")
    t = time.time()
    drop_zeros = []
    for col in all_feature_cols:
        # np.nanvar is fast and works column by column
        if np.nanvar(df[col].values) == 0:
            drop_zeros.append(col)

    if drop_zeros:
        df.drop(columns=drop_zeros, inplace=True)
        all_feature_cols = [c for c in df.columns if c not in meta_cols and c != "label_fine"]
    print(f"   Removed {len(drop_zeros)} zero-variance features ({time.time()-t:.1f}s)")
    gc.collect()

    # ═══════════════════════════════════════════════════════════
    # STEP 4: Remove highly correlated features (>0.98) on SAMPLE
    # ═══════════════════════════════════════════════════════════
    print("\nStep 4: Removing highly correlated features (>0.98)...")
    t = time.time()
    sample_size = min(100_000, len(df))
    df_sample = df[all_feature_cols].sample(n=sample_size, random_state=42)
    corr_matrix = df_sample.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > 0.98)]
    
    if to_drop:
        df.drop(columns=to_drop, inplace=True)
        all_feature_cols = [c for c in df.columns if c not in meta_cols and c != "label_fine"]
    print(f"   Removed {len(to_drop)} highly correlated features ({time.time()-t:.1f}s)")
    del df_sample, corr_matrix, upper; gc.collect()

    # ═══════════════════════════════════════════════════════════
    # STEP 5: Outlier winsorization (3x IQR, COL BY COL)
    # ═══════════════════════════════════════════════════════════
    print("\nStep 5: Outlier winsorization...")
    t = time.time()
    outlier_count = 0
    for col in all_feature_cols:
        vals = df[col].values
        valid_vals = vals[~np.isnan(vals)]
        if valid_vals.size == 0:
            df[col] = 0.0  # Force entirely missing columns to 0 safely
            continue
            
        q25, q75 = np.percentile(valid_vals, [25, 75])
        iqr = q75 - q25
        if iqr == 0: continue
        lower, upper_val = q25 - 3.0 * iqr, q75 + 3.0 * iqr
        mask = (vals < lower) | (vals > upper_val)
        outlier_count += mask.sum()
        # Assign directly back to df (avoids read-only PyArrow buffer errors)
        df[col] = np.clip(vals, lower, upper_val)
    print(f"   Winsorized {outlier_count:,} values ({time.time()-t:.1f}s)")

    # ═══════════════════════════════════════════════════════════
    # STEP 6: Custom Memory-Safe Robust Scaling (COL BY COL)
    # ═══════════════════════════════════════════════════════════
    print("\nStep 6: Robust Scaling (Memory Safe)...")
    t = time.time()
    scaler_params = {}

    for col in all_feature_cols:
        vals = df[col].values
        valid_vals = vals[~np.isnan(vals)]
        
        if valid_vals.size == 0:
            center, scale = 0.0, 1.0
        else:
            center = np.median(valid_vals)
            q25, q75 = np.percentile(valid_vals, [25, 75])
            scale = q75 - q25
            if scale == 0:
                scale = 1.0
        
        # Scale (allocates temporary array safely instead of in-place mutation)
        scaled_vals = (vals - center) / scale
        
        # Replace remaining NaN/infs from division zero
        scaled_vals = np.nan_to_num(scaled_vals, nan=0.0, posinf=0.0, neginf=0.0)
        df[col] = scaled_vals
        
        scaler_params[col] = {"center": float(center), "scale": float(scale)}

    # Save scaler parameters logic
    with open(SCALER_FILE, "wb") as f:
        pickle.dump(scaler_params, f)
    print(f"   Scaled {len(all_feature_cols)} features inplace ({time.time()-t:.1f}s)")
    gc.collect()

    # ═══════════════════════════════════════════════════════════
    # STEP 7: Save Array without Pandas allocation explosion
    # ═══════════════════════════════════════════════════════════
    print("\nStep 7: Saving to NPZ (Incremental Allocation)...")
    t = time.time()

    y_binary = df["label_binary"].values.astype(np.int8)
    y_family = df["label_family"].values.astype(np.int8)
    
    print(f"   Allocating final float32 array...")
    # Allocate empty array to avoid pandas `.values` casting huge float64 arrays
    X_final = np.empty((len(df), len(all_feature_cols)), dtype=np.float32)
    
    # Fill column by column
    print(f"   Transferring features into matrix...")
    for i, col in enumerate(all_feature_cols):
        X_final[:, i] = df[col].values
        # Free from dataframe immediately
        df.drop(columns=[col], inplace=True)
    
    del df; gc.collect()

    print(f"   Features: {X_final.shape} ({X_final.nbytes/1024**2:.1f} MB)")
    print(f"   Saving to disk...")

    np.savez_compressed(OUTPUT_FILE, X=X_final, y_binary=y_binary, y_family=y_family,
                        feature_names=np.array(all_feature_cols, dtype=object))

    meta = {"n_samples": X_final.shape[0], "n_features": X_final.shape[1],
            "feature_names": all_feature_cols}
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(meta, f)

    file_size = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"   Saved: {OUTPUT_FILE.name} ({file_size:.1f} MB, {time.time()-t:.1f}s)")

    del X_final; gc.collect()

    total = time.time() - total_start
    print(f"\n  DONE in {total/60:.1f} min | {len(all_feature_cols)} features")


if __name__ == "__main__":
    main()