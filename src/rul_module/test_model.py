import sys
import os

# ✅ ADD PROJECT ROOT TO PATH (FINAL FIX)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import joblib
import pandas as pd
from pathlib import Path
from src.rul_module.rule_engine import apply_rules

MODEL_PATH = Path("models/rul_model/fdd_model.pkl")
SCALER_PATH = Path("models/rul_model/scaler.pkl")


def load_model():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


def test_samples():
    return [
        {"H2": 50, "CO": 100, "C2H4": 10, "C2H2": 1, "rul": 1000},
        {"H2": 200, "CO": 300, "C2H4": 100, "C2H2": 20, "rul": 500},
        {"H2": 1000, "CO": 800, "C2H4": 400, "C2H2": 200, "rul": 100},
        {"H2": 0, "CO": 0, "C2H4": 0, "C2H2": 0, "rul": 1200},
    ]


def run_test():
    print("🔍 Testing Hybrid Model (ML + Rules)...\n")

    model, scaler = load_model()

    for i, sample in enumerate(test_samples()):
        df = pd.DataFrame([sample])
        df_scaled = scaler.transform(df)

        ml_pred = model.predict(df_scaled)[0]
        final_pred = apply_rules(sample, ml_pred)

        print(f"Sample {i+1}: {sample}")
        print(f"ML Prediction: {ml_pred}")
        print(f"Final Prediction (Rule Corrected): {final_pred}")
        print("-" * 50)


if __name__ == "__main__":
    run_test()