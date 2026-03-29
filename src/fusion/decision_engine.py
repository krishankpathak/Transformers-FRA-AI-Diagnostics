import joblib
import pandas as pd
from pathlib import Path

# =========================
# PATHS
# =========================
FRA_MODEL_PATH = Path("models/fra_model/fra_model.pkl")
FDD_MODEL_PATH = Path("models/rul_model/fdd_model.pkl")
SCALER_PATH = Path("models/rul_model/scaler.pkl")


# =========================
# LOAD MODELS
# =========================
def load_models():
    fra_model = joblib.load(FRA_MODEL_PATH)
    fdd_model = joblib.load(FDD_MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    return fra_model, fdd_model, scaler


# =========================
# FRA PREDICTION
# =========================
def predict_fra(fra_features, fra_model):
    df = pd.DataFrame([fra_features])
    return fra_model.predict(df)[0]


# =========================
# FDD PREDICTION
# =========================
def predict_fdd(gas_data, fdd_model, scaler):
    df = pd.DataFrame([gas_data])
    df_scaled = scaler.transform(df)
    return fdd_model.predict(df_scaled)[0]


# =========================
# FINAL DECISION LOGIC
# =========================
def combine_results(fra_result, fdd_result):

    if fdd_result == 4:
        return "CRITICAL: Severe Operational Fault Detected"

    if fra_result == "fault" and fdd_result >= 3:
        return "CRITICAL: Mechanical + Operational Fault"

    if fdd_result == 3:
        return "HIGH RISK: Developing Operational Fault"

    if fra_result == "fault":
        return "HIGH RISK: Mechanical Fault Detected"

    if fra_result == "deformation":
        return "MODERATE: Possible Winding Deformation"

    if fdd_result == 2:
        return "WARNING: Early Operational Fault"

    return "NORMAL: Transformer Healthy"