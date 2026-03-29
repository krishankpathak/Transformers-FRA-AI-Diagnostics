import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.fusion.decision_engine import load_models, predict_fra, predict_fdd, combine_results
from src.rul_module.rule_engine import apply_rules
from src.explanation.explanation_engine import generate_explanation


def diagnose(fra_features: dict, gas_data: dict):

    fra_model, fdd_model, scaler = load_models()

    fra_result = predict_fra(fra_features, fra_model)
    fdd_result = predict_fdd(gas_data, fdd_model, scaler)

    corrected_fdd = apply_rules(gas_data, fdd_result)

    final_decision = combine_results(fra_result, corrected_fdd)

    # 🔥 ADD THIS (MOST IMPORTANT)
    explanation = generate_explanation(fra_result, gas_data, corrected_fdd)

    return {
        "FRA_Result": fra_result,
        "FDD_Result": int(corrected_fdd),
        "Final_Diagnosis": final_decision,
        "Explanation": explanation
    }