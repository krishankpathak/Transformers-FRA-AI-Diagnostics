import json
import numpy as np
import pandas as pd
from pathlib import Path

# =========================
# CONFIG
# =========================
INPUT_PATH = Path("data/processed/fra/parsed_data.json")
OUTPUT_PATH = Path("data/processed/fra/fra_curves.csv")
NEWS_CSVS_PATH = Path("data/news_csvs")

FREQ_START = 20        # Hz
FREQ_END = 2_000_000   # 2 MHz
NUM_POINTS = 500       # resolution


# =========================
# UTIL
# =========================
def ensure_output_dir():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEWS_CSVS_PATH.mkdir(parents=True, exist_ok=True)


def load_parsed_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# FRA SIMULATION CORE
# =========================
def simulate_fra(R, L, C, freq):
    """
    Advanced simulation with multiple resonance peaks for realistic transformer behavior.
    """
    # Base RLC response
    w = 2 * np.pi * freq
    denominator = np.sqrt((1 - (w**2 * L * C))**2 + (w * R * C)**2)
    H_base = 1 / (denominator + 1e-12)
    
    # Add multiple resonance peaks (characteristic of real transformers)
    # Typically 3-5 major peaks in different frequency bands
    resonances = [
        {'f': 1000, 'q': 5, 'a': 0.5},    # Low freq (core)
        {'f': 50000, 'q': 10, 'a': 0.8},  # Mid freq (winding structure)
        {'f': 500000, 'q': 8, 'a': 0.4},  # High freq (leads)
    ]
    
    H_res = np.ones_like(freq)
    for res in resonances:
        # Simple Lorentzian-like peak
        peak = res['a'] / (1 + (res['q'] * (freq/res['f'] - res['f']/freq))**2 + 1e-12)
        H_res += peak
        
    H_total = H_base * H_res
    H_db = 20 * np.log10(H_total + 1e-12)
    
    return H_db


# =========================
# PARAMETER EXTRACTION
# =========================
def extract_rlc(entry):
    """
    Extract approximate R, L, C values from parsed data.
    Fallback to default if missing.
    """

    params = entry.get("parameters", {})

    R = 1.0
    L = 1e-3
    C = 1e-9

    for key, value in params.items():
        key_lower = key.lower()

        try:
            val = float(str(value).replace("μ", "e-6").replace("p", "e-12"))
        except:
            continue

        if "resistance" in key_lower or "rs" in key_lower:
            R = abs(val)

        elif "inductance" in key_lower or "ls" in key_lower:
            L = abs(val)

        elif "capacitance" in key_lower or "c" in key_lower:
            C = abs(val)

    return R, L, C


# =========================
# MAIN FUNCTION
# =========================
def run_fra_generation():
    print("⚡ Generating Professional FRA dataset...")

    ensure_output_dir()
    
    # 1. Base Grid
    freq = np.logspace(np.log10(FREQ_START), np.log10(FREQ_END), NUM_POINTS)
    
    # 2. Define Fault Scenarios with distinct physics-based parameters
    fault_scenarios = [
        {"name": "Healthy", "R": (0.5, 1.5), "L": (0.8e-3, 1.2e-3), "C": (0.8e-9, 1.2e-9), "noise": 0.1, "count": 200},
        {"name": "Winding Deformation", "R": (2.0, 4.0), "L": (2.0e-3, 4.0e-3), "C": (2.0e-9, 4.0e-9), "noise": 0.5, "count": 200},
        {"name": "Core Displacement", "R": (0.1, 0.5), "L": (6.0e-3, 9.0e-3), "C": (0.2e-9, 0.6e-9), "noise": 0.4, "count": 200},
        {"name": "Insulation Degradation", "R": (10.0, 25.0), "L": (0.2e-3, 0.6e-3), "C": (8.0e-9, 15.0e-9), "noise": 0.8, "count": 200}
    ]

    all_data = []

    for scenario in fault_scenarios:
        print(f"   -> Generating {scenario['count']} samples for {scenario['name']}...")
        for i in range(scenario['count']):
            R = np.random.uniform(*scenario['R'])
            L = np.random.uniform(*scenario['L'])
            C = np.random.uniform(*scenario['C'])
            
            mag = simulate_fra(R, L, C, freq)
            # Add scenario-specific noise
            mag += np.random.normal(0, scenario['noise'], size=NUM_POINTS)
            
            # Create sample
            sample_id = f"{scenario['name'].replace(' ', '_')}_{i}"
            
            sample_df = pd.DataFrame({
                "frequency": freq,
                "magnitude_db": mag
            })
            
            # Save individual sample to news_csvs
            sample_df.to_csv(NEWS_CSVS_PATH / f"{sample_id}.csv", index=False)
            
            sample_df["source_file"] = [sample_id] * NUM_POINTS
            # ADD LABEL AFTER DATAFRAME CREATION
            sample_df["label"] = scenario['name']
            all_data.append(sample_df)

    print("📊 Concatenating data...")
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Explicitly ensure columns are clean
    final_df.columns = [c.strip() for c in final_df.columns]
    
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Professional curves created: {OUTPUT_PATH}")
    print(f"📊 Total samples: {len(fault_scenarios) * 200}")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_fra_generation()