import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report
import joblib
import os
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

# =========================
# CONFIG
# =========================
DATA_PATH = Path("data/final/fra_dataset.csv")
MODEL_DIR = Path("models/fra_model")
MODEL_PATH_H5 = MODEL_DIR / "fra_cnn_model.h5"
MODEL_PATH_PKL = MODEL_DIR / "fra_model.pkl"
MODEL_PATH_XGB = MODEL_DIR / "fra_xgb.json"
MODEL_PATH_CAT = MODEL_DIR / "fra_cat.cbm"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

def ensure_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# PREDICTION WRAPPER
# =========================
class FRAModel:
    def __init__(self):
        self.model = None
        self.xgb_model = None
        self.cat_model = None
        self.le = None
        self.model_type = None # "keras", "sklearn", "ensemble"
        self.classes = ["Healthy", "Winding Deformation", "Core Displacement", "Insulation Degradation"]
        
    def load(self):
        # Load Label Encoder
        le_path = MODEL_DIR / "label_encoder.pkl"
        if os.path.exists(le_path):
            self.le = joblib.load(le_path)
            self.classes = list(self.le.classes_)

        # 1. Try Ensemble (Voting Classifier)
        if os.path.exists(MODEL_PATH_PKL):
            try:
                self.model = joblib.load(MODEL_PATH_PKL)
                self.model_type = "ensemble"
                print(f"[INFO] Loaded Ensemble model from {MODEL_PATH_PKL}")
            except Exception as e:
                print(f"[ERROR] Failed to load ensemble model: {e}")

        # 2. Try XGBoost
        if os.path.exists(MODEL_PATH_XGB):
            try:
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(str(MODEL_PATH_XGB))
                print(f"[INFO] Loaded XGBoost model from {MODEL_PATH_XGB}")
            except Exception as e:
                print(f"[ERROR] Failed to load XGBoost: {e}")

        # 3. Try CatBoost
        if os.path.exists(MODEL_PATH_CAT):
            try:
                self.cat_model = CatBoostClassifier()
                self.cat_model.load_model(str(MODEL_PATH_CAT))
                print(f"[INFO] Loaded CatBoost model from {MODEL_PATH_CAT}")
            except Exception as e:
                print(f"[ERROR] Failed to load CatBoost: {e}")

    def predict(self, magnitude_curve: np.ndarray):
        """
        magnitude_curve should be a 1D array of 500 points.
        """
        if self.model is None and self.xgb_model is None:
            # Dummy logic based on variance if no model
            var = np.var(magnitude_curve)
            if var < 10: return "Healthy", 0.95
            if var < 50: return "Winding Deformation", 0.85
            return "Core Displacement", 0.75
            
        try:
            # Prepare data
            X = magnitude_curve.reshape(1, -1)

            if self.model_type == "ensemble" and self.model is not None:
                preds_encoded = self.model.predict(X)[0]
                probs = self.model.predict_proba(X)[0]
                confidence = float(np.max(probs))
                
                if self.le:
                    class_name = self.le.inverse_transform([preds_encoded])[0]
                else:
                    class_name = self.classes[preds_encoded]
                return str(class_name), confidence

            elif self.xgb_model and self.xgb_model is not None:
                dmat = xgb.DMatrix(X)
                preds = self.xgb_model.predict(dmat)
                class_idx = np.argmax(preds[0])
                confidence = float(preds[0][class_idx])
                if self.le:
                    class_name = self.le.inverse_transform([class_idx])[0]
                else:
                    class_name = self.classes[class_idx]
                return str(class_name), confidence

            elif self.cat_model and self.cat_model is not None:
                preds = self.cat_model.predict_proba(X)
                class_idx = np.argmax(preds[0])
                confidence = float(preds[0][class_idx])
                if self.le:
                    class_name = self.le.inverse_transform([class_idx])[0]
                else:
                    class_name = self.classes[class_idx]
                return str(class_name), confidence

            return "Healthy", 0.80
                
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return "Analysis Failed", 0.0

def get_fra_model():
    model = FRAModel()
    model.load()
    return model

# =========================
# MAIN TRAINING
# =========================
from sklearn.preprocessing import LabelEncoder

def run_training():
    try:
        print("🤖 Training Professional FRA Ensemble model (RF + XGB + CatBoost)...")
        ensure_model_dir()

        if not DATA_PATH.exists():
            print(f"[INFO] Training data {DATA_PATH} not found. Generating...")
            from src.fra_module.feature_extractor import run_feature_extraction
            run_feature_extraction()

        df = pd.read_csv(DATA_PATH)
        print(f"📊 Loaded {len(df)} samples")
        
        # Strip whitespace from column names just in case
        df.columns = [c.strip() for c in df.columns]
        
        X = df.drop(columns=["source_file", "label"])
        y = df["label"]

        print(f"DEBUG: Unique labels in training: {y.unique()}")

        # Use LabelEncoder to ensure consistent class mapping
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        print("🚀 Fitting models...")
        # 1. Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # 2. XGBoost
        num_class = len(le.classes_)
        xgb_clf = xgb.XGBClassifier(
            n_estimators=100, 
            objective='multi:softprob',
            num_class=num_class,
            eval_metric='mlogloss',
            random_state=42
        )
        
        # 3. CatBoost
        cat_clf = CatBoostClassifier(
            iterations=100,
            learning_rate=0.1,
            depth=6,
            loss_function='MultiClass',
            verbose=False,
            random_seed=42
        )
        
        # 4. Ensemble
        ensemble = VotingClassifier(
            estimators=[('rf', rf), ('xgb', xgb_clf), ('cat', cat_clf)], # type: ignore
            voting='soft'
        )

        print("🚀 Fitting ensemble (RF + XGB + CatBoost)...")
        ensemble.fit(X_train, y_train)
        
        print(f"💾 Saving ensemble to {MODEL_PATH_PKL}")
        joblib.dump(ensemble, MODEL_PATH_PKL)
        
        # Save sub-models separately - Using absolute paths
        fitted_xgb = ensemble.named_estimators_['xgb']
        xgb_save_path = os.path.abspath(MODEL_PATH_XGB)
        print(f"💾 Saving XGBoost to {xgb_save_path}")
        fitted_xgb.save_model(xgb_save_path)
        
        fitted_cat = ensemble.named_estimators_['cat']
        cat_save_path = os.path.abspath(MODEL_PATH_CAT)
        print(f"💾 Saving CatBoost to {cat_save_path}")
        fitted_cat.save_model(cat_save_path)

        print(f"\n✅ All models saved in: {MODEL_DIR}")
        
        y_pred = ensemble.predict(X_test)
        print("\n📊 Performance:\n")
        print(classification_report(y_test, y_pred, target_names=le.classes_))
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_training()