from typing import Dict, Any, List

class ResultValidator:
    """
    Validates cross-tool consistency, ensures textual claims have visual evidence support,
    and flags contradictions (e.g., GeoChat claims water but GeoGround detects 0 water pixels).
    """
    def validate(
        self,
        intent: str,
        tool_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        warnings: List[str] = []
        contradictions: List[str] = []
        is_consistent = True

        # Check 1: Did GeoChat claim a water body while Grounding found nothing?
        geochat_res = tool_results.get("geochat", {}).get("result", {})
        geoground_res = tool_results.get("geoground", {}).get("result", {})

        answer_text = geochat_res.get("answer", "").lower()
        if "water" in answer_text or "lake" in answer_text:
            bboxes = geoground_res.get("bboxes", [])
            raw_mask = context.get("raw_mask")
            if not bboxes and raw_mask is None:
                contradictions.append("Evidence inconsistency: Textual description mentions water features, but spatial grounding detected 0 demarcated water instances.")
                is_consistent = False

        # Check 2: Optical + SAR alignment validation
        align_res = tool_results.get("multimodal_alignment", {}).get("result", {})
        if align_res:
            overlap = align_res.get("spatial_overlap_pct", 100.0)
            if overlap < 40.0:
                warnings.append(f"Low spatial overlap ({overlap}%) between Optical and SAR sensors. Fusion confidence is degraded.")

        # Check 3: Change detection evidence check
        chg_res = tool_results.get("change_detection", {}).get("result", {})
        if chg_res:
            chg_pct = chg_res.get("change_percentage", 0.0)
            bboxes = chg_res.get("bboxes", [])
            if chg_pct > 2.0 and not bboxes:
                warnings.append("Change probability detected surface variation, but discrete region clustering was fragmented.")

        agreement_level = "High" if is_consistent and not warnings else ("Moderate" if not contradictions else "Disagreement Flagged")

        return {
            "is_consistent": is_consistent,
            "agreement_level": agreement_level,
            "contradictions": contradictions,
            "warnings": warnings
        }
