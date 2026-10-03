from typing import Dict, Any

class TransparentConfidence:
    """
    Transparent multi-factor confidence calculator considering model certainty,
    input quality/alignment, evidence strength, and cross-tool consistency.
    Clearly returned as a system confidence estimate, not a calibrated probability.
    """
    def estimate(
        self,
        tool_results: Dict[str, Any],
        validation_report: Dict[str, Any],
        has_spatial_evidence: bool
    ) -> Dict[str, Any]:
        # 1. Model score average
        conf_scores = [
            t.get("confidence", 0.90) for t in tool_results.values()
            if isinstance(t, dict) and "confidence" in t and t.get("confidence", 0) > 0
        ]
        model_score = float(sum(conf_scores) / len(conf_scores)) if conf_scores else 0.90

        # 2. Input compatibility & alignment
        input_comp = 1.00
        if validation_report.get("warnings"):
            input_comp = 0.88

        # 3. Evidence strength
        evidence_str = 0.95 if has_spatial_evidence else 0.85

        # 4. Cross-tool consistency
        if validation_report.get("contradictions"):
            consistency = 0.65
        elif validation_report.get("agreement_level") == "High":
            consistency = 0.95
        else:
            consistency = 0.88

        # Formula: 0.35 * model + 0.25 * input + 0.25 * evidence + 0.15 * consistency
        raw_final = (
            0.35 * model_score +
            0.25 * input_comp +
            0.25 * evidence_str +
            0.15 * consistency
        )
        final_conf = round(float(raw_final), 2)

        level = "High" if final_conf >= 0.88 else ("Medium" if final_conf >= 0.70 else "Low")

        return {
            "model_confidence": round(model_score, 2),
            "input_compatibility": round(input_comp, 2),
            "evidence_strength": round(evidence_str, 2),
            "answer_consistency": round(consistency, 2),
            "final_confidence": final_conf,
            "confidence_level": level,
            "calibration_status": "System Confidence Estimate (Multi-Factor Aggregation)"
        }
