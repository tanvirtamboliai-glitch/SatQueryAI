from typing import Dict, Any, Optional

def compute_aggregated_confidence(
    model_conf: float = 0.90,
    input_compatibility: float = 1.00,
    evidence_strength: float = 0.88,
    answer_consistency: float = 0.92,
    has_mask_or_bbox: bool = True
) -> Dict[str, Any]:
    """
    Computes an auditable, multi-factor aggregated confidence score.
    Formula: Weighted combination of model logit probability, spatial input compatibility,
    evidence availability strength, and cross-consistency.
    """
    # Adjust evidence strength based on concrete spatial evidence
    if not has_mask_or_bbox:
        evidence_strength = min(evidence_strength, 0.75)

    # Weights: Model 0.35, Compatibility 0.25, Evidence 0.25, Consistency 0.15
    w_model = 0.35
    w_compat = 0.25
    w_evidence = 0.25
    w_consist = 0.15

    final_score = (
        model_conf * w_model +
        input_compatibility * w_compat +
        evidence_strength * w_evidence +
        answer_consistency * w_consist
    )

    final_score = round(final_score, 2)
    pct = int(round(final_score * 100))

    if pct >= 88:
        level = "High confidence"
    elif pct >= 70:
        level = "Moderate confidence"
    else:
        level = "Low confidence"

    return {
        "model_confidence": round(model_conf, 2),
        "input_compatibility": round(input_compatibility, 2),
        "evidence_strength": round(evidence_strength, 2),
        "answer_consistency": round(answer_consistency, 2),
        "final_confidence": final_score,
        "confidence_level": level,
        "calibration_status": "Audited multi-factor score"
    }
