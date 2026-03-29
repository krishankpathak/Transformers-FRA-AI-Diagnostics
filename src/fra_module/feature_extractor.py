import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import skew, kurtosis

# =========================
# CONFIG
# =========================
INPUT_PATH = Path("data/processed/fra/fra_curves.csv")
OUTPUT_PATH = Path("data/final/fra_dataset.csv")


# =========================
# UTIL
# =========================
def ensure_output_dir():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(df_group):
    """
    Extract professional signal features from one FRA curve.
    """
    freq = df_group["frequency"].values
    mag = df_group["magnitude_db"].values

    features = {}

    # 1. Basic Statistical Features
    features["mean_magnitude"] = float(np.mean(mag))
    features["std_dev"] = float(np.std(mag))
    features["min_mag"] = float(np.min(mag))
    features["max_mag"] = float(np.max(mag))
    features["rms_mag"] = float(np.sqrt(np.mean(np.square(mag))))
    features["skewness"] = float(skew(mag)) if len(mag) > 0 else 0
    features["kurtosis"] = float(kurtosis(mag)) if len(mag) > 0 else 0

    # 2. Frequency Band Energies (Professional Standard)
    # Low frequency (winding/core): 20 Hz - 2 kHz
    low_band = mag[freq < 2000]
    # Mid frequency (winding structure): 2 kHz - 200 kHz
    mid_band = mag[(freq >= 2000) & (freq < 200000)]
    # High frequency (leads/insulation): 200 kHz - 2 MHz
    high_band = mag[freq >= 200000]

    features["low_freq_energy"] = float(np.sum(np.square(low_band))) / len(low_band) if len(low_band) > 0 else 0
    features["mid_freq_energy"] = float(np.sum(np.square(mid_band))) / len(mid_band) if len(mid_band) > 0 else 0
    features["high_freq_energy"] = float(np.sum(np.square(high_band))) / len(high_band) if len(high_band) > 0 else 0
    
    features["low_mean"] = float(np.mean(low_band)) if len(low_band) > 0 else 0
    features["mid_mean"] = float(np.mean(mid_band)) if len(mid_band) > 0 else 0
    features["high_mean"] = float(np.mean(high_band)) if len(high_band) > 0 else 0

    # 3. Peak/Resonance Detection
    try:
        # Identify local maxima
        peak_idx = np.where(np.diff(np.sign(np.diff(mag))) < 0)[0] + 1
        features["num_peaks"] = int(len(peak_idx))
        if len(peak_idx) > 0:
            # Find the index of the highest peak
            highest_peak_idx = peak_idx[np.argmax(mag[peak_idx])]
            features["main_peak_freq"] = float(freq[highest_peak_idx])
            features["main_peak_mag"] = float(mag[highest_peak_idx])
        else:
            features["main_peak_freq"] = 0.0
            features["main_peak_mag"] = 0.0
    except:
        features["num_peaks"] = 0
        features["main_peak_freq"] = 0.0
        features["main_peak_mag"] = 0.0

    # 4. Slope (Trend Analysis)
    try:
        features["slope"] = float((mag[-1] - mag[0]) / (np.log10(freq[-1]) - np.log10(freq[0])))
    except:
        features["slope"] = 0.0

    return features


def feature_dict_for_ui(freq, mag, ref_freq=None, ref_mag=None):
    """
    Helper for frontend display.
    """
    df = pd.DataFrame({"frequency": freq, "magnitude_db": mag})
    feats = extract_features(df)
    
    if ref_freq is not None and ref_mag is not None:
        ref_df = pd.DataFrame({"frequency": ref_freq, "magnitude_db": ref_mag})
        ref_feats = extract_features(ref_df)
        # Calculate deltas
        feats["delta_mean"] = feats["mean_magnitude"] - ref_feats["mean_magnitude"]
        feats["delta_energy"] = feats["mid_freq_energy"] - ref_feats["mid_freq_energy"]
        
    return feats


# =========================
# MAIN
# =========================
def run_feature_extraction():
    print("📊 Extracting Professional FRA features...")

    ensure_output_dir()

    if not INPUT_PATH.exists():
        print(f"[ERROR] Input path {INPUT_PATH} does not exist. Run fra_generator.py first.")
        return

    df = pd.read_csv(INPUT_PATH)
    
    # Strip any potential whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    
    # Remove any samples that don't have enough points
    counts = df.groupby("source_file").size()
    valid_files = counts[counts >= 100].index
    df = df[df["source_file"].isin(valid_files)]
    
    print(f"DEBUG: Found {len(valid_files)} valid source files.")
    if 'label' in df.columns:
        print(f"DEBUG: Labels present in df: {df['label'].unique()}")
    else:
        print(f"DEBUG: 'label' column not found! Columns are: {df.columns.tolist()}")
    
    grouped = df.groupby("source_file")

    all_features = []

    for name, group in grouped:
        features = extract_features(group)
        features["source_file"] = name
        # Keep the original label if present
        label = "unknown"
        if "label" in group.columns:
            label = str(group["label"].iloc[0])
        features["label"] = label
        all_features.append(features)

    final_df = pd.DataFrame(all_features)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Professional feature dataset created: {OUTPUT_PATH}")
    print(f"📊 Total samples: {len(final_df)}")


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_feature_extraction()