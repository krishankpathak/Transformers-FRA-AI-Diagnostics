import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

# =========================
# CONFIG
# =========================
MODEL_DIR = Path("models/anomaly")
MODEL_PATH = MODEL_DIR / "isolation_forest.pkl"

def ensure_anomaly_model():
    """
    Ensures an IsolationForest model exists. If not, it trains a basic one 
    if data is available, or returns a fallback.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[ERROR] Failed to load anomaly model: {e}")
    
    # Training fallback or fresh model
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    
    # Try to find some training data
    data_path = Path("data/final/fra_dataset.csv")
    if data_path.exists():
        try:
            df = pd.read_csv(data_path)
            # Exclude non-numeric columns
            X = df.select_dtypes(include=[np.number])
            if not X.empty:
                model.fit(X)
                joblib.dump(model, MODEL_PATH)
                print(f"[INFO] Trained and saved anomaly model to {MODEL_PATH}")
                return model
        except Exception as e:
            print(f"[WARNING] Could not train anomaly model: {e}")
            
    return model

def predict_anomaly(feature_dict, model):
    """
    Predicts anomaly score and status.
    Returns: {"is_anomaly": bool, "score": float}
    """
    try:
        # Filter for only numeric features
        numeric_feats = {k: v for k, v in feature_dict.items() if isinstance(v, (int, float, np.number))}
        X = pd.DataFrame([numeric_feats])
        
        # IsolationForest decision_function returns scores where lower is more anomalous
        # Standardize so higher is more anomalous
        raw_score = float(model.decision_function(X)[0])
        is_anomaly = bool(model.predict(X)[0] == -1)
        
        return {
            "is_anomaly": is_anomaly,
            "score": raw_score
        }
    except Exception as e:
        print(f"[ERROR] Anomaly prediction failed: {e}")
        return {"is_anomaly": False, "score": 0.0}

def score_to_anomaly_0_100(raw_score: float) -> float:
    """
    Map decision_function score (approx -0.5 to 0.5) to 0-100.
    Lower raw_score means more anomalous.
    """
    # Simple mapping: 0.5 -> 0, -0.5 -> 100
    score = (0.5 - raw_score) * 100.0
    return float(np.clip(score, 0.0, 100.0))
