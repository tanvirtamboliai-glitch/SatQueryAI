from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.clay_service import ClayService

class MultimodalFusionTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="multimodal_fusion",
            description="Deep multimodal latent feature fusion combining optical multi-spectral reflectance with SAR microwave backscatter.",
            accepted_modalities=["OPTICAL_SAR"],
            capabilities=["latent_fusion", "optical_sar_joint_representation", "cross_sensor_analysis"],
            input_requirements=["aligned_optical", "aligned_sar", "query"],
            output_types=["joint_features", "fused_prediction", "cross_modal_explanation"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="4GB"
        )
        super().__init__(defn)
        self.clay_service = ClayService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        opt_pil = context.get("optical_pil") or context.get("image1_pil")
        sar_pil = context.get("sar_pil") or context.get("image2_pil")
        query = context.get("query", "Analyze optical and SAR jointly.")
        meta = context.get("optical_meta") or context.get("image1_meta") or {}

        fusion_res = self.clay_service.analyze_optical_sar_pair(opt_pil, sar_pil, query, meta)
        return {
            "result": {
                "answer": fusion_res["answer"],
                "latent_norm": fusion_res.get("latent_norm", 1.0),
                "fusion_mode": "intermediate_latent_projection"
            },
            "evidence": {
                "textual_evidence": fusion_res["evidence_text"]
            },
            "confidence": fusion_res["confidence"]
        }
