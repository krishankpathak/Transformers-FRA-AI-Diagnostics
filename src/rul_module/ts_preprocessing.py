import pandas as pd
from pathlib import Path

# =========================
# PATHS
# =========================
TRAIN_FOLDER = Path("data/raw/kaggle/data_train")
LABEL_FDD = Path("data/raw/kaggle/labels_fdd_train.csv")
LABEL_RUL = Path("data/raw/kaggle/labels_rul_train.csv")

OUTPUT_PATH = Path("data/processed/kaggle/train_combined.csv")


def ensure_output_dir():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# =========================
# LOAD LABELS (STRING BASED)
# =========================
def load_labels():
    fdd = pd.read_csv(LABEL_FDD)
    rul = pd.read_csv(LABEL_RUL)

    # Normalize IDs (remove .csv if present)
    fdd["id"] = fdd["id"].astype(str).str.replace(".csv", "", regex=False)
    rul["id"] = rul["id"].astype(str).str.replace(".csv", "", regex=False)

    print("FDD sample:\n", fdd.head())
    print("RUL sample:\n", rul.head())

    return fdd, rul


# =========================
# PROCESS FILES (FINAL FIX)
# =========================
def process_files():
    print("📂 Processing Kaggle training data...")

    fdd_labels, rul_labels = load_labels()

    all_data = []
    files = list(TRAIN_FOLDER.glob("*.csv"))

    print(f"Found {len(files)} files")

    match_count = 0

    for file in files:
        try:
            df = pd.read_csv(file)

            file_id = file.stem  # e.g. 2_trans_100

            df["id"] = file_id

            # ---- FDD LABEL ----
            match_fdd = fdd_labels[fdd_labels["id"] == file_id]

            if not match_fdd.empty:
                df["category"] = match_fdd.iloc[0]["category"]
                match_count += 1
            else:
                df["category"] = None

            # ---- RUL LABEL ----
            match_rul = rul_labels[rul_labels["id"] == file_id]

            if not match_rul.empty:
                df["rul"] = match_rul.iloc[0]["predicted"]
            else:
                df["rul"] = None

            all_data.append(df)

        except Exception as e:
            print(f"[ERROR] {file}: {e}")

    print(f"\n✅ Matched files: {match_count} / {len(files)}")

    final_df = pd.concat(all_data, ignore_index=True)
    return final_df


# =========================
# MAIN
# =========================
def run_kaggle_processing():
    ensure_output_dir()

    df = process_files()

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Kaggle dataset created: {OUTPUT_PATH}")
    print(f"📊 Total rows: {len(df)}")
    print("📊 Columns:", df.columns.tolist())
    print("📊 Non-null labels:", df["category"].notnull().sum())


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_kaggle_processing()