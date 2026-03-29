def generate_explanation(fra_result, gas_data, fdd_result):
    """
    Generate human-readable explanation
    """

    explanations = []

    H2 = gas_data["H2"]
    CO = gas_data["CO"]
    C2H4 = gas_data["C2H4"]
    C2H2 = gas_data["C2H2"]

    # FRA explanation
    if fra_result == "deformation":
        explanations.append("FRA indicates winding deformation")

    if fra_result == "fault":
        explanations.append("FRA indicates mechanical fault")

    # Gas-based explanation
    if H2 > 800:
        explanations.append("High H2 → severe thermal fault")

    elif H2 > 300:
        explanations.append("Moderate H2 → developing thermal fault")

    if C2H2 > 150:
        explanations.append("High C2H2 → arcing detected")

    if CO > 200:
        explanations.append("High CO → insulation degradation")

    # Final interpretation
    if fdd_result == 4:
        explanations.append("System classified as CRITICAL condition")

    elif fdd_result == 3:
        explanations.append("System classified as HIGH risk")

    elif fdd_result == 2:
        explanations.append("System classified as WARNING")

    else:
        explanations.append("System operating in NORMAL condition")

    return explanations