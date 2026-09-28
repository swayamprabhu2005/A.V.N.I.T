from typing import Dict, Any, Optional
from ..config import (
    WEIGHT_VEHICLE_TYPE,
    WEIGHT_COLOR,
    WEIGHT_OCR_CONFIDENCE,
    WEIGHT_MAKE_MODEL,
    THRESHOLD_LOW_RISK,
    THRESHOLD_MED_RISK
)
from ..database import get_vehicle_by_plate

# Equivalent vehicle types grouping
TYPE_ALIASES = {
    "car": {"car", "sedan", "suv", "hatchback", "jeep"},
    "motorcycle": {"motorcycle", "bike", "scooter", "two-wheeler"},
    "truck": {"truck", "pickup", "lorry"},
    "bus": {"bus", "van", "minibus"}
}

def are_types_compatible(observed: str, registered: str) -> bool:
    obs = observed.lower().strip()
    reg = registered.lower().strip()
    if obs == reg:
        return True
    for group in TYPE_ALIASES.values():
        if obs in group and reg in group:
            return True
    return False

def are_colors_compatible(observed: str, registered: str) -> float:
    obs = observed.lower().strip()
    reg = registered.lower().strip()
    if obs == reg:
        return 1.0
    # Similar shades
    neutral_light = {"white", "silver_grey", "silver", "grey"}
    if obs in neutral_light and reg in neutral_light:
        return 0.70
    return 0.0

def evaluate_identity_risk(
    plate_number: str,
    ocr_confidence: float,
    observed_type: str,
    observed_color: str,
    observed_make: Optional[str] = "",
    observed_model: Optional[str] = "",
    is_night_mode: bool = False
) -> Dict[str, Any]:
    """
    Computes explainable 4-Factor Identity Risk Score.
    Standard Weights:
      - Type Match: 35%
      - Color Match: 20%
      - OCR Confidence: 20%
      - Make/Model Match: 25%
    Adaptive Night Mode Weights (Monochrome IR lighting compensation):
      - Type Match: 40%
      - Color Match: 5% (Monochrome IR compensation)
      - OCR Confidence: 35%
      - Make/Model Match: 20%
    """
    vehicle_record = get_vehicle_by_plate(plate_number)

    # 1. Unregistered Plate Check
    if not vehicle_record:
        return {
            "plate_number": plate_number,
            "registered": False,
            "registration_record": None,
            "observed_attributes": {
                "type": observed_type,
                "color": observed_color,
                "make": observed_make or "Unknown",
                "model": observed_model or "Unknown",
                "ocr_confidence": round(ocr_confidence, 2)
            },
            "factor_scores": {
                "type_match": 0.0,
                "color_match": 0.0,
                "ocr_confidence": ocr_confidence,
                "make_model_match": 0.0
            },
            "risk_score": 88.0,
            "risk_level": "RED",
            "reason": f"Unregistered Plate Alert: Number plate '{plate_number}' is not found in the authorized vehicle database.",
            "is_tampered": True
        }

    # If vehicle registration is Suspended/Flagged
    reg_status = vehicle_record.get("registration_status", "Active")
    status_penalty = 30.0 if reg_status.lower() != "active" else 0.0

    # 2. Factor 1: Vehicle Type Match (Weight: 35%)
    reg_type = vehicle_record.get("vehicle_type", "").lower()
    type_matched = are_types_compatible(observed_type, reg_type)
    score_type = 1.0 if type_matched else 0.0

    # 3. Factor 2: Color Match (Weight: 20%)
    reg_color = vehicle_record.get("color", "").lower()
    score_color = are_colors_compatible(observed_color, reg_color)

    # 4. Factor 3: OCR Confidence (Weight: 20%)
    # Clamped between 0.0 and 1.0
    score_ocr = min(1.0, max(0.0, ocr_confidence))

    # 5. Factor 4: Make & Model Match (Weight: 25%)
    reg_make = vehicle_record.get("make", "").lower()
    reg_model = vehicle_record.get("model", "").lower()
    
    if observed_make and reg_make:
        score_make_model = 1.0 if observed_make.lower() == reg_make else 0.0
    else:
        # If visual make/model is not detected by basic model, neutral credit is given
        score_make_model = 0.85

    # Weighted Overall Similarity (0.0 to 1.0) with Adaptive Night Weighting
    if is_night_mode:
        w_type, w_color, w_ocr, w_model = 0.40, 0.05, 0.35, 0.20
    else:
        w_type, w_color, w_ocr, w_model = WEIGHT_VEHICLE_TYPE, WEIGHT_COLOR, WEIGHT_OCR_CONFIDENCE, WEIGHT_MAKE_MODEL

    similarity = (
        (w_type * score_type) +
        (w_color * score_color) +
        (w_ocr * score_ocr) +
        (w_model * score_make_model)
    )

    # Risk Score = (1.0 - similarity) * 100 + status_penalty
    raw_risk = (1.0 - similarity) * 100.0 + status_penalty
    risk_score = round(min(100.0, max(0.0, raw_risk)), 1)

    # Risk Level & Granular Explanations
    reasons = []
    if is_night_mode:
        reasons.append("Auto Night Mode: Infrared glare suppression & adaptive low-light weighting active.")
    if not type_matched:
        reasons.append(f"Vehicle Type Mismatch: Observed '{observed_type.capitalize()}', but registered as '{reg_type.capitalize()}'.")
    if score_color < 0.5:
        if is_night_mode:
            reasons.append(f"Color Notice (Night Vision): Observed '{observed_color.capitalize()}', registered as '{reg_color.capitalize()}'.")
        else:
            reasons.append(f"Color Mismatch: Observed '{observed_color.capitalize()}', but registered as '{reg_color.capitalize()}'.")
    elif score_color < 1.0:
        reasons.append(f"Color Variance: Observed '{observed_color.capitalize()}', registered as '{reg_color.capitalize()}'.")
    
    if score_ocr < 0.65:
        reasons.append(f"Low OCR Confidence ({int(ocr_confidence*100)}%): Plate character recognition may be partially degraded or obstructed.")

    if reg_status.lower() != "active":
        reasons.append(f"Registration Status Flagged: Vehicle record status is '{reg_status}'.")

    if not reasons:
        reasons.append("All observed vehicle attributes match the authorized registration record.")

    if risk_score <= THRESHOLD_LOW_RISK:
        risk_level = "GREEN"
    elif risk_score <= THRESHOLD_MED_RISK:
        risk_level = "YELLOW"
    else:
        risk_level = "RED"

    return {
        "plate_number": plate_number,
        "registered": True,
        "registration_record": vehicle_record,
        "observed_attributes": {
            "type": observed_type,
            "color": observed_color,
            "make": observed_make or reg_make,
            "model": observed_model or reg_model,
            "ocr_confidence": round(ocr_confidence, 2)
        },
        "factor_scores": {
            "type_match": score_type,
            "color_match": score_color,
            "ocr_confidence": round(score_ocr, 2),
            "make_model_match": round(score_make_model, 2)
        },
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason": " | ".join(reasons),
        "is_tampered": risk_level == "RED"
    }
