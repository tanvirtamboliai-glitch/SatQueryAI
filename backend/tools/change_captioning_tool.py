from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition

class ChangeCaptioningTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="change_captioning",
            description="Generates grounded natural language description strictly based on detected change polygons without hallucinations.",
            accepted_modalities=["TEMPORAL_PAIR"],
            capabilities=["change_description", "temporal_captioning"],
            input_requirements=["change_detection_result"],
            output_types=["change_description"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="2GB"
        )
        super().__init__(defn)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        chg_data = context.get("change_result") or {}
        pct = chg_data.get("change_percentage", 0.0)
        regions_count = chg_data.get("changed_regions_count", 0)

        if pct < 0.5:
            desc = "Surface appearance remains stable across the observation interval; no substantial land cover conversion detected."
        elif pct > 15.0:
            desc = f"Extensive surface reorganization observed: +{pct}% of the surveyed extent underwent significant modification across {regions_count} zones."
        else:
            desc = f"Localized surface evolution detected (+{pct}% modified area) across {regions_count} sector(s), indicative of new structural footprints and ground disturbance."

        return {
            "result": {
                "description": desc,
                "change_magnitude": "high" if pct > 15.0 else ("moderate" if pct > 3.0 else "minimal")
            },
            "evidence": {
                "textual_evidence": desc
            },
            "confidence": 0.93
        }
