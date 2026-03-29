import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import joblib
import xgboost as xgb

# =========================
# PATHS
# =========================
DATA_PATH = Path("data/processed/kaggle/train_combined.csv")
MODEL_DIR = Path("models/rul_model")
MODEL_PATH = MODEL_DIR / "fdd_model.pkl"
MODEL_PATH_XGB = MODEL_DIR / "fdd_xgb.json"
SCALER_PATH = MODEL_DIR / "scaler.pkl"


def ensure_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def preprocess(df):
    y = df["category"]
    X = df.select_dtypes(include=["number"])

    df_clean = X.copy()
    df_clean["category"] = y
    df_clean = df_clean.dropna(subset=["category"])

    return df_clean


def run_training():
    print("🤖 Training FDD model (XGBoost) with limited data...")

    ensure_model_dir()

    if not DATA_PATH.exists():
        print(f"[ERROR] Training data {DATA_PATH} not found.")
        return

    # Load only a subset to avoid memory issues
    print(f"📂 Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, nrows=200000)
    print(f"📊 Loaded dataset shape: {df.shape}")

    df = preprocess(df)
    print(f"📊 After preprocessing: {df.shape}")

    X = df.drop(columns=["category"])
    y = df["category"]

    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Use XGBoost for RUL as it's faster
    label_map = {name: i for i, name in enumerate(np.unique(y))}
    y_train_int = y_train.map(label_map)
    y_test_int = y_test.map(label_map)
    
    print("🚀 Fitting XGBoost...")
    xgb_clf = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=3)
    xgb_clf.fit(X_train, y_train_int)
    
    print(f"💾 Saving XGBoost to {MODEL_PATH_XGB}")
    xgb_clf.save_model(str(MODEL_PATH_XGB))
    
    # Save a simple RandomForest as a fallback for the .pkl expectation
    # print("🚀 Fitting RandomForest...")
    # rf = RandomForestClassifier(n_estimators=50, random_state=42)
    # rf.fit(X_train, y_train)
    # joblib.dump(rf, MODEL_PATH)

    print(f"\n✅ Models saved at: {MODEL_DIR}")
    print(f"✅ Scaler saved at: {SCALER_PATH}")


if __name__ == "__main__":
    run_training()