from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..preprocessing.sar import process_sar_image

class SARAnalysisTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="sar_analysis",
            description="Analyzes synthetic aperture radar microwave backscatter (dB), roughness, double-bounce structural reflection, and specular water signatures.",
            accepted_modalities=["SAR"],
            capabilities=["sar_preprocessing", "backscatter_db", "microwave_structural_analysis"],
            input_requirements=["sar_file_path"],
            output_types=["sar_features", "backscatter_metrics", "despeckled_radar"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="2GB"
        )
        super().__init__(defn)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        file_path = context.get("sar_path") or context.get("image2_path")
        if not file_path:
            raise ValueError("SAR file path required for SAR analysis.")

        raw_sar, pil_sar, meta = process_sar_image(file_path)
        metrics = meta.get("sar_metrics", {})
        return {
            "result": {
                "polarizations": meta.get("polarizations", []),
                "mean_backscatter_db": metrics.get("mean_backscatter_db", -12.0),
                "double_bounce_urban_pct": metrics.get("double_bounce_high_pct", 0.0),
                "specular_water_pct": metrics.get("specular_low_pct", 0.0)
            },
            "evidence": {
                "sar_pil": pil_sar,
                "sar_arr": raw_sar,
                "sar_meta": meta,
                "textual_evidence": f"SAR radar backscatter calibrated: {metrics.get('mean_backscatter_db', -12.0)} dB mean, {metrics.get('double_bounce_high_pct', 0.0)}% urban double-bounce."
            },
            "confidence": 0.96
        }
