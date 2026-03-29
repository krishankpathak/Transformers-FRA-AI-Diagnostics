def apply_rules(data, ml_pred):
    H2 = data.get("H2", 0)
    C2H2 = data.get("C2H2", 0)

    # 🔥 SOFT RULES (not overriding everything)
    if H2 > 900 and C2H2 > 150:
        return max(ml_pred, 4)

    if H2 > 500:
        return max(ml_pred, 3)

    return ml_pred

def get_severity(fault_type, confidence):
    """
    Professional severity classification based on IEEE C57.149 and DL/T 911-2004 standards.
    """
    fault_lower = str(fault_type).lower()
    conf = float(confidence)
    
    # Standard severity mapping
    if "healthy" in fault_lower:
        return "LOW"
    
    # Winding deformation is high risk
    if "deformation" in fault_lower or "movement" in fault_lower:
        if conf > 0.75: return "HIGH"
        return "MEDIUM"
        
    # Core issues
    if "core" in fault_lower or "displacement" in fault_lower:
        if conf > 0.85: return "HIGH"
        return "MEDIUM"
        
    # Insulation degradation
    if "insulation" in fault_lower:
        if conf > 0.80: return "HIGH"
        return "MEDIUM"
        
    return "MEDIUM"

def get_recommendations(fault_type, confidence):
    """
    Actionable maintenance recommendations based on detected signatures.
    """
    fault_lower = str(fault_type).lower()
    
    if "healthy" in fault_lower:
        return [
            "Current FRA signature shows high correlation with reference fingerprint.",
            "Transformer is mechanically stable. Continue periodic monitoring (every 2-3 years).",
            "No internal inspection or supplementary testing required at this stage."
        ]
        
    if "winding" in fault_lower or "deformation" in fault_lower:
        return [
            "Significant Spectral Deviation detected in the 2kHz - 200kHz range.",
            "Indicates potential axial or radial winding deformation from short-circuit forces.",
            "Recommended: Perform Leakage Reactance / Short-Circuit Impedance test.",
            "Action: Schedule internal inspection during the next maintenance outage."
        ]
        
    if "core" in fault_lower or "displacement" in fault_lower:
        return [
            "Low-frequency magnitude shift detected (< 2kHz).",
            "Indicates potential core displacement, clamping loose, or grounding issues.",
            "Recommended: Check Core-to-Ground insulation resistance and grounding strap.",
            "Action: Verify tightness of core clamping bolts if design allows access."
        ]
        
    if "insulation" in fault_lower:
        return [
            "High-frequency magnitude shift detected (> 200kHz).",
            "Indicates potential degradation of lead insulation or moisture in pressboard.",
            "Recommended: Perform DGA (Dissolved Gas Analysis) and Tan-Delta testing.",
            "Action: Monitor Power Factor trends and check bushing condition."
        ]
        
    return [
        "FRA signature deviates from baseline. Expert interpretation required.",
        "Perform supplementary electrical tests (TTR, Winding Resistance) to correlate findings.",
        "Repeat FRA sweep to ensure noise or connection quality is not the cause of deviation."
    ]
