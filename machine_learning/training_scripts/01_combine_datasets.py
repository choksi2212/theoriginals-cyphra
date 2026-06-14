"""
CYPHRA - Dataset Combination Script (HIGH ACCURACY BUILD)
Target: >99% detection accuracy
MEMORY-SAFE: Processes one dataset at a time, saves to disk, frees RAM
"""

import numpy as np
import pandas as pd
import os
import sys
import time
import gc
import warnings
import platform
import psutil
import pickle
from pathlib import Path
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = SCRIPT_DIR / "combined_dataset.parquet"
METADATA_FILE = SCRIPT_DIR / "combined_metadata.pkl"
TEMP_DIR = SCRIPT_DIR / "_temp_combine"
CHUNK_SIZE = 500_000

DATASETS = [
    {"name": "ISCXVPN2016", "path": SCRIPT_DIR / "ISCXVPN2016", "id": 0,
     "label_col": "Label",
     "drop_cols": ["Flow ID", "Src IP", "Dst IP", "Timestamp",
                   "flow_start", "FirstNPkt_size", "Category",
                   "App_protocol", "Web_service"]},
    {"name": "UNSW-NB15", "path": SCRIPT_DIR / "UNSWNB15", "id": 1,
     "label_col": "label", "attack_cat_col": "attack_cat", "drop_cols": []},
    {"name": "CICIDS2017", "path": SCRIPT_DIR / "CICIDS2017", "id": 2,
     "label_col": " Label", "drop_cols": []},
    {"name": "CSE-CICIDS2018", "path": SCRIPT_DIR / "CSECICIDS2018", "id": 3,
     "label_col": "Label", "drop_cols": ["Timestamp"]},
]

# Column rename map (same as before)
COLUMN_RENAME_MAP = {
    "Flow Duration": "flow_duration", " Flow Duration": "flow_duration",
    "Tot Fwd Pkts": "total_fwd_packets", " Total Fwd Packets": "total_fwd_packets",
    "Tot Bwd Pkts": "total_bwd_packets", " Total Backward Packets": "total_bwd_packets",
    "TotLen Fwd Pkts": "total_length_fwd_packets", " Total Length of Fwd Packets": "total_length_fwd_packets",
    "TotLen Bwd Pkts": "total_length_bwd_packets", " Total Length of Bwd Packets": "total_length_bwd_packets",
    "Fwd Pkt Len Max": "fwd_pkt_len_max", " Fwd Packet Length Max": "fwd_pkt_len_max",
    "Fwd Pkt Len Min": "fwd_pkt_len_min", " Fwd Packet Length Min": "fwd_pkt_len_min",
    "Fwd Pkt Len Mean": "fwd_pkt_len_mean", " Fwd Packet Length Mean": "fwd_pkt_len_mean",
    "Fwd Pkt Len Std": "fwd_pkt_len_std", " Fwd Packet Length Std": "fwd_pkt_len_std",
    "Bwd Pkt Len Max": "bwd_pkt_len_max", " Bwd Packet Length Max": "bwd_pkt_len_max",
    "Bwd Pkt Len Min": "bwd_pkt_len_min", " Bwd Packet Length Min": "bwd_pkt_len_min",
    "Bwd Pkt Len Mean": "bwd_pkt_len_mean", " Bwd Packet Length Mean": "bwd_pkt_len_mean",
    "Bwd Pkt Len Std": "bwd_pkt_len_std", " Bwd Packet Length Std": "bwd_pkt_len_std",
    "Flow Byts/s": "flow_bytes_per_sec", " Flow Bytes/s": "flow_bytes_per_sec",
    "Flow Pkts/s": "flow_packets_per_sec", " Flow Packets/s": "flow_packets_per_sec",
    "Flow IAT Mean": "flow_iat_mean", " Flow IAT Mean": "flow_iat_mean",
    "Flow IAT Std": "flow_iat_std", " Flow IAT Std": "flow_iat_std",
    "Flow IAT Max": "flow_iat_max", " Flow IAT Max": "flow_iat_max",
    "Flow IAT Min": "flow_iat_min", " Flow IAT Min": "flow_iat_min",
    "Fwd IAT Tot": "fwd_iat_total", " Fwd IAT Total": "fwd_iat_total",
    "Fwd IAT Mean": "fwd_iat_mean", " Fwd IAT Mean": "fwd_iat_mean",
    "Fwd IAT Std": "fwd_iat_std", " Fwd IAT Std": "fwd_iat_std",
    "Fwd IAT Max": "fwd_iat_max", " Fwd IAT Max": "fwd_iat_max",
    "Fwd IAT Min": "fwd_iat_min", " Fwd IAT Min": "fwd_iat_min",
    "Bwd IAT Tot": "bwd_iat_total", " Bwd IAT Total": "bwd_iat_total",
    "Bwd IAT Mean": "bwd_iat_mean", " Bwd IAT Mean": "bwd_iat_mean",
    "Bwd IAT Std": "bwd_iat_std", " Bwd IAT Std": "bwd_iat_std",
    "Bwd IAT Max": "bwd_iat_max", " Bwd IAT Max": "bwd_iat_max",
    "Bwd IAT Min": "bwd_iat_min", " Bwd IAT Min": "bwd_iat_min",
    "Fwd PSH Flags": "fwd_psh_flags", " Fwd PSH Flags": "fwd_psh_flags",
    "Bwd PSH Flags": "bwd_psh_flags",
    "Fwd URG Flags": "fwd_urg_flags", "Bwd URG Flags": "bwd_urg_flags",
    "Fwd Header Len": "fwd_header_length", " Fwd Header Length": "fwd_header_length",
    "Bwd Header Len": "bwd_header_length", " Bwd Header Length": "bwd_header_length",
    "Fwd Pkts/s": "fwd_packets_per_sec", " Fwd Packets/s": "fwd_packets_per_sec",
    "Bwd Pkts/s": "bwd_packets_per_sec", " Bwd Packets/s": "bwd_packets_per_sec",
    "Pkt Len Min": "pkt_len_min", " Min Packet Length": "pkt_len_min",
    "Pkt Len Max": "pkt_len_max", " Max Packet Length": "pkt_len_max",
    "Pkt Len Mean": "pkt_len_mean", " Packet Length Mean": "pkt_len_mean",
    "Pkt Len Std": "pkt_len_std", " Packet Length Std": "pkt_len_std",
    "Pkt Len Var": "pkt_len_var", " Packet Length Variance": "pkt_len_var",
    "FIN Flag Cnt": "fin_flag_cnt", " FIN Flag Count": "fin_flag_cnt",
    "SYN Flag Cnt": "syn_flag_cnt", " SYN Flag Count": "syn_flag_cnt",
    "RST Flag Cnt": "rst_flag_cnt", " RST Flag Count": "rst_flag_cnt",
    "PSH Flag Cnt": "psh_flag_cnt", " PSH Flag Count": "psh_flag_cnt",
    "ACK Flag Cnt": "ack_flag_cnt", " ACK Flag Count": "ack_flag_cnt",
    "URG Flag Cnt": "urg_flag_cnt", " URG Flag Count": "urg_flag_cnt",
    "CWE Flag Count": "cwe_flag_cnt", " CWE Flag Count": "cwe_flag_cnt",
    "ECE Flag Cnt": "ece_flag_cnt", " ECE Flag Count": "ece_flag_cnt",
    "Down/Up Ratio": "down_up_ratio", " Down/Up Ratio": "down_up_ratio",
    "Pkt Size Avg": "pkt_size_avg", " Average Packet Size": "pkt_size_avg",
    "Fwd Seg Size Avg": "fwd_seg_size_avg", " Avg Fwd Segment Size": "fwd_seg_size_avg",
    "Bwd Seg Size Avg": "bwd_seg_size_avg", " Avg Bwd Segment Size": "bwd_seg_size_avg",
    "Subflow Fwd Pkts": "subflow_fwd_packets", " Subflow Fwd Packets": "subflow_fwd_packets",
    "Subflow Fwd Byts": "subflow_fwd_bytes", " Subflow Fwd Bytes": "subflow_fwd_bytes",
    "Subflow Bwd Pkts": "subflow_bwd_packets", " Subflow Bwd Packets": "subflow_bwd_packets",
    "Subflow Bwd Byts": "subflow_bwd_bytes", " Subflow Bwd Bytes": "subflow_bwd_bytes",
    "Init Fwd Win Byts": "init_fwd_win_bytes", " Init_Win_bytes_forward": "init_fwd_win_bytes",
    "Init Bwd Win Byts": "init_bwd_win_bytes", " Init_Win_bytes_backward": "init_bwd_win_bytes",
    "Fwd Act Data Pkts": "fwd_act_data_pkts", " act_data_pkt_fwd": "fwd_act_data_pkts",
    "Fwd Seg Size Min": "fwd_seg_size_min", " min_seg_size_forward": "fwd_seg_size_min",
    "Active Mean": "active_mean", " Active Mean": "active_mean",
    "Active Std": "active_std", " Active Std": "active_std",
    "Active Max": "active_max", " Active Max": "active_max",
    "Active Min": "active_min", " Active Min": "active_min",
    "Idle Mean": "idle_mean", " Idle Mean": "idle_mean",
    "Idle Std": "idle_std", " Idle Std": "idle_std",
    "Idle Max": "idle_max", " Idle Max": "idle_max",
    "Idle Min": "idle_min", " Idle Min": "idle_min",
    "Src Port": "src_port", " Source Port": "src_port",
    "Dst Port": "dst_port", " Destination Port": "dst_port",
    "Protocol": "protocol", " Protocol": "protocol",
    "Fwd Byts/b Avg": "fwd_bytes_bulk_avg",
    "Fwd Pkts/b Avg": "fwd_packets_bulk_avg",
    "Fwd Blk Rate Avg": "fwd_bulk_rate_avg",
    "Bwd Byts/b Avg": "bwd_bytes_bulk_avg",
    "Bwd Pkts/b Avg": "bwd_packets_bulk_avg",
    "Bwd Blk Rate Avg": "bwd_bulk_rate_avg",
    "dur": "flow_duration", "proto": "protocol",
    "spkts": "total_fwd_packets", "dpkts": "total_bwd_packets",
    "sbytes": "total_length_fwd_packets", "dbytes": "total_length_bwd_packets",
    "sload": "flow_bytes_per_sec", "dload": "bwd_bytes_per_sec",
    "sinpkt": "fwd_iat_mean", "dinpkt": "bwd_iat_mean",
    "sjit": "fwd_iat_std", "djit": "bwd_iat_std",
    "swin": "init_fwd_win_bytes", "dwin": "init_bwd_win_bytes",
    "smean": "fwd_pkt_len_mean", "dmean": "bwd_pkt_len_mean",
}


def map_label_to_hierarchy(label_str):
    lbl = str(label_str).strip().lower()
    if lbl in ("benign", "normal", "0", "0.0", "nan", ""):
        return 0, 0, str(label_str).strip()
    if any(k in lbl for k in ["dos", "ddos", "slowloris", "slowhttptest",
                               "hulk", "goldeneye", "heartbleed"]):
        family = 1
    elif any(k in lbl for k in ["scan", "portscan", "probe", "reconnaissance",
                                 "brute", "ssh-patator", "ftp-patator",
                                 "bruteforce", "bot"]):
        family = 2
    elif any(k in lbl for k in ["exploit", "injection", "xss", "sql",
                                 "infiltr", "web attack", "web_attack",
                                 "shellcode", "backdoor", "worms",
                                 "analysis", "generic", "fuzzers"]):
        family = 3
    else:
        family = 4
    return 1, family, str(label_str).strip()


def verify_system():
    print("=" * 70)
    print("  CYPHRA - System Verification")
    print("=" * 70)
    errors = []
    cpu_cores = cpu_count()
    ram_gb = psutil.virtual_memory().total / (1024**3)
    print(f"  CPU:   {platform.processor() or 'Unknown'} ({cpu_cores} cores)")
    print(f"  RAM:   {ram_gb:.1f} GB")
    cuda_available = False
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"  GPU:   {torch.cuda.get_device_name(0)} | CUDA {torch.version.cuda}")
        else:
            print(f"  GPU:   CUDA not available")
    except ImportError:
        print(f"  GPU:   PyTorch not installed")
    for lib in ["numpy", "pandas", "pyarrow", "psutil"]:
        try:
            m = __import__(lib)
            print(f"  + {lib}: {getattr(m, '__version__', 'OK')}")
        except ImportError:
            errors.append(f"Missing: {lib}")
    for d in DATASETS:
        if not d["path"].exists():
            errors.append(f"Missing: {d['path']}")
            print(f"  X {d['name']}: NOT FOUND")
        else:
            print(f"  + {d['name']}: OK")
    if errors:
        print("\n[X] FAILED:"); [print(f"   - {e}") for e in errors]; sys.exit(1)
    print(f"[OK] Verified")
    print("=" * 70)
    return {"cpu_cores": cpu_cores, "ram_gb": ram_gb, "cuda_available": cuda_available}


def load_csv_file(filepath):
    try:
        return pd.read_csv(filepath, low_memory=False, encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        print(f"   [!] Error {filepath.name}: {e}")
        return None


def standardize_df(df, label_col, drop_cols, dataset_id):
    """Standardize column names, extract labels, drop unwanted cols"""
    labels = df[label_col].astype(str).str.strip()
    drop = [c for c in drop_cols + [label_col] if c in df.columns]
    df.drop(columns=drop, errors="ignore", inplace=True)
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["_label_raw"] = labels.values
    df["dataset_id"] = np.int8(dataset_id)
    # Force all feature cols to float32 for schema unification and memory savings
    for col in df.columns:
        if col not in ("_label_raw", "dataset_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(np.float32)
    return df


def process_and_save_iscxvpn(cfg, hw, temp_path):
    print(f"\n[1/4] {cfg['name']}...")
    csvs = sorted(cfg["path"].glob("*.csv"))
    with Pool(min(hw["cpu_cores"], len(csvs))) as pool:
        dfs = pool.map(load_csv_file, csvs)
    dfs = [d for d in dfs if d is not None]
    df = pd.concat(dfs, ignore_index=True)
    del dfs
    df = standardize_df(df, cfg["label_col"], cfg["drop_cols"], cfg["id"])
    n = len(df)
    cols = list(df.columns)
    df.to_parquet(temp_path, index=False, engine="pyarrow")
    print(f"   -> {n:,} samples, {len(cols)} cols -> saved to disk")
    del df; gc.collect()
    return n, cols


def process_and_save_unsw(cfg, hw, temp_path):
    print(f"\n[2/4] {cfg['name']}...")
    dfs = [pd.read_parquet(p) for p in sorted(cfg["path"].glob("*.parquet"))]
    df = pd.concat(dfs, ignore_index=True)
    del dfs
    attack_cat = df["attack_cat"].astype(str).str.strip() if "attack_cat" in df.columns else pd.Series(["Normal"] * len(df))
    binary_label = df["label"].values if "label" in df.columns else np.zeros(len(df))
    raw_labels = []
    for b, a in zip(binary_label, attack_cat):
        raw_labels.append("Normal" if int(b) == 0 else (a if a and a.lower() not in ("", "nan", "normal") else "Generic"))
    drop = [c for c in ["label", "attack_cat"] + cfg["drop_cols"] if c in df.columns]
    df.drop(columns=drop, errors="ignore", inplace=True)
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["_label_raw"] = raw_labels
    df["dataset_id"] = np.int8(cfg["id"])
    
    # Force float32
    for col in df.columns:
        if col not in ("_label_raw", "dataset_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(np.float32)
    n = len(df)
    cols = list(df.columns)
    df.to_parquet(temp_path, index=False, engine="pyarrow")
    print(f"   -> {n:,} samples, {len(cols)} cols -> saved to disk")
    del df; gc.collect()
    return n, cols


def process_and_save_cicids2017(cfg, hw, temp_path):
    print(f"\n[3/4] {cfg['name']}...")
    csvs = sorted(cfg["path"].glob("*.csv"))
    with Pool(min(hw["cpu_cores"], len(csvs))) as pool:
        dfs = pool.map(load_csv_file, csvs)
    dfs = [d for d in dfs if d is not None]
    df = pd.concat(dfs, ignore_index=True)
    del dfs
    label_col = next((c for c in df.columns if c.strip().lower() == "label"), df.columns[-1])
    labels = df[label_col].astype(str).str.strip()
    drop = [c for c in df.columns if c.strip().lower() in
            ("flow id", "source ip", "destination ip", "timestamp", "src ip", "dst ip")]
    drop.append(label_col)
    df.drop(columns=[c for c in drop if c in df.columns], errors="ignore", inplace=True)
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["_label_raw"] = labels.values
    df["dataset_id"] = np.int8(cfg["id"])
    
    # Force float32
    for col in df.columns:
        if col not in ("_label_raw", "dataset_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(np.float32)
    n = len(df)
    cols = list(df.columns)
    df.to_parquet(temp_path, index=False, engine="pyarrow")
    print(f"   -> {n:,} samples, {len(cols)} cols -> saved to disk")
    del df, labels; gc.collect()
    return n, cols


def process_and_save_cse2018(cfg, hw, temp_path):
    """Process CSE-CICIDS2018 in chunks, write directly to multiple parquet parts"""
    print(f"\n[4/4] {cfg['name']} (LARGE - streaming to disk)...")
    csvs = sorted(cfg["path"].glob("*.csv"))

    # Process each CSV -> save as individual parquet part files
    part_dir = temp_path.parent / "_cse2018_parts"
    part_dir.mkdir(exist_ok=True)
    total_rows = 0
    all_cols = set()
    part_idx = 0

    for csv_file in csvs:
        print(f"   {csv_file.name} ({csv_file.stat().st_size/1024**2:.0f} MB)...", end="", flush=True)
        file_rows = 0
        try:
            for chunk in pd.read_csv(csv_file, chunksize=CHUNK_SIZE, low_memory=False, on_bad_lines="skip"):
                label_col = next((c for c in chunk.columns if c.strip().lower() == "label"), chunk.columns[-1])
                labels = chunk[label_col].astype(str).str.strip()
                drop = [c for c in chunk.columns if c.strip().lower() in
                        ("timestamp", "flow id", "source ip", "destination ip", "src ip", "dst ip")]
                drop.append(label_col)
                chunk.drop(columns=[c for c in drop if c in chunk.columns], errors="ignore", inplace=True)
                chunk.rename(columns=COLUMN_RENAME_MAP, inplace=True)
                chunk.columns = [c.strip().lower().replace(" ", "_") for c in chunk.columns]
                chunk["_label_raw"] = labels.values
                chunk["dataset_id"] = np.int8(cfg["id"])
                # Force all feature cols to float32 for uniform PyArrow schema across chunks
                for col in chunk.columns:
                    if col not in ("_label_raw", "dataset_id"):
                        chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype(np.float32)
                # Save this chunk directly to disk
                part_file = part_dir / f"part_{part_idx:04d}.parquet"
                chunk.to_parquet(part_file, index=False, engine="pyarrow")
                all_cols.update(chunk.columns)
                file_rows += len(chunk)
                part_idx += 1
                del chunk
            print(f" {file_rows:,} rows ({part_idx} parts)")
            total_rows += file_rows
        except Exception as e:
            print(f" ERROR: {e}")
        gc.collect()

    # Now read back all parts and write a single combined parquet
    # But we do it in batches to avoid OOM
    print(f"   Combining {part_idx} parts ({total_rows:,} rows) into single file...")
    import pyarrow.parquet as pq
    import pyarrow as pa

    part_files = sorted(part_dir.glob("*.parquet"))
    # Read all parts using pyarrow (much more memory efficient than pandas)
    tables = []
    for pf in part_files:
        tables.append(pq.read_table(pf))
    combined_table = pa.concat_tables(tables, promote_options="default")
    pq.write_table(combined_table, temp_path)

    # Cleanup parts
    for pf in part_files:
        pf.unlink()
    part_dir.rmdir()

    cols = [c.name for c in combined_table.schema]
    del tables, combined_table; gc.collect()
    print(f"   -> {total_rows:,} samples -> saved to disk")
    return total_rows, cols


def main():
    hw = verify_system()
    start_time = time.time()

    TEMP_DIR.mkdir(exist_ok=True)

    # ============================================================
    # STEP 1: Process each dataset INDEPENDENTLY -> save to disk
    #          Only 1 dataset in RAM at a time!
    # ============================================================
    print("\n" + "=" * 70)
    print("STEP 1: Loading Datasets (disk-streaming)")
    print("=" * 70)

    temp_files = []
    all_columns = {}

    # Dataset 1
    temp1 = TEMP_DIR / "temp_iscxvpn.parquet"
    n1, c1 = process_and_save_iscxvpn(DATASETS[0], hw, temp1)
    temp_files.append(temp1)
    all_columns["ISCXVPN2016"] = c1

    # Dataset 2
    temp2 = TEMP_DIR / "temp_unsw.parquet"
    n2, c2 = process_and_save_unsw(DATASETS[1], hw, temp2)
    temp_files.append(temp2)
    all_columns["UNSW-NB15"] = c2

    # Dataset 3
    temp3 = TEMP_DIR / "temp_cicids2017.parquet"
    n3, c3 = process_and_save_cicids2017(DATASETS[2], hw, temp3)
    temp_files.append(temp3)
    all_columns["CICIDS2017"] = c3

    # Dataset 4 (LARGE - streams to disk in chunks)
    temp4 = TEMP_DIR / "temp_cse2018.parquet"
    n4, c4 = process_and_save_cse2018(DATASETS[3], hw, temp4)
    temp_files.append(temp4)
    all_columns["CSE-CICIDS2018"] = c4

    total_samples = n1 + n2 + n3 + n4
    print(f"\n   Total: {total_samples:,} samples across 4 datasets")

    # ============================================================
    # STEP 2: Combine using PyArrow (memory efficient)
    # ============================================================
    print("\n" + "=" * 70)
    print("STEP 2: Combining with PyArrow (memory efficient)")
    print("=" * 70)

    import pyarrow.parquet as pq
    import pyarrow as pa

    # Read all temp files using pyarrow
    tables = []
    for tf in temp_files:
        print(f"   Reading {tf.name}...", end="", flush=True)
        t = pq.read_table(tf)
        print(f" {t.num_rows:,} rows, {t.num_columns} cols")
        tables.append(t)

    print("   Concatenating...")
    combined = pa.concat_tables(tables, promote_options="default")
    del tables; gc.collect()
    print(f"   Combined: {combined.num_rows:,} rows, {combined.num_columns} cols")

    # Convert to pandas for label processing
    # But only the _label_raw column first
    print("   Processing labels...")
    labels_arrow = combined.column("_label_raw")
    labels_list = labels_arrow.to_pylist()

    label_binary = []
    label_family = []
    label_fine = []
    for lbl in labels_list:
        b, f, fine = map_label_to_hierarchy(lbl)
        label_binary.append(b)
        label_family.append(f)
        label_fine.append(fine)

    del labels_list; gc.collect()

    # Add label columns to the arrow table
    combined = combined.drop_columns(["_label_raw"])
    combined = combined.append_column("label_binary", pa.array(label_binary, type=pa.int8()))
    combined = combined.append_column("label_family", pa.array(label_family, type=pa.int8()))
    combined = combined.append_column("label_fine", pa.array(label_fine, type=pa.string()))

    del label_binary, label_family, label_fine; gc.collect()

    benign = sum(1 for b in combined.column("label_binary").to_pylist() if b == 0)
    malicious = combined.num_rows - benign
    print(f"   Benign:    {benign:>12,} ({benign/combined.num_rows*100:.1f}%)")
    print(f"   Malicious: {malicious:>12,} ({malicious/combined.num_rows*100:.1f}%)")

    # ============================================================
    # STEP 3: Save final combined parquet
    # ============================================================
    print("\n" + "=" * 70)
    print("STEP 3: Saving final output")
    print("=" * 70)

    pq.write_table(combined, OUTPUT_FILE)
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"   File:  {OUTPUT_FILE.name} ({file_size_mb:.1f} MB)")
    print(f"   Rows:  {combined.num_rows:,}")
    print(f"   Cols:  {combined.num_columns}")

    feature_cols = [c for c in combined.column_names
                    if c not in ("label_binary", "label_family", "label_fine", "dataset_id")]
    metadata = {
        "n_samples": combined.num_rows,
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "datasets": [d["name"] for d in DATASETS],
        "class_distribution": {"benign": benign, "malicious": malicious},
    }
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)

    del combined; gc.collect()

    # Cleanup temp files
    print("   Cleaning temp files...")
    for tf in temp_files:
        if tf.exists():
            tf.unlink()
    if TEMP_DIR.exists():
        try:
            TEMP_DIR.rmdir()
        except:
            pass

    elapsed = time.time() - start_time
    print(f"\n  DONE in {elapsed/60:.1f} min | {total_samples:,} samples | {len(feature_cols)} features")
    print("=" * 70)


if __name__ == "__main__":
    main()