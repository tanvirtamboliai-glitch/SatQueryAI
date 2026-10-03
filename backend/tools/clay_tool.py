from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.clay_service import ClayService

class ClayTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="clay",
            description="Multisensor Earth observation foundation model supporting joint optical and SAR representation.",
            accepted_modalities=["OPTICAL", "SAR", "OPTICAL_SAR"],
            capabilities=["multisensor_representation", "geospatial_embeddings", "cross_sensor_encoder"],
            input_requirements=["optical_image", "sar_image"],
            output_types=["multisensor_embeddings"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="8GB"
        )
        super().__init__(defn)
        self.service = ClayService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        opt_img = context.get("optical_pil") or context.get("image1_pil")
        sar_img = context.get("sar_pil") or context.get("image2_pil")
        opt_feat = self.service.extract_optical_features(opt_img)
        sar_feat = self.service.extract_sar_features(sar_img) if sar_img else None
        return {
            "result": {
                "optical_features_shape": list(opt_feat.shape),
                "sar_features_shape": list(sar_feat.shape) if sar_feat is not None else None,
                "model": "Clay Foundation v1"
            },
            "evidence": {
                "textual_evidence": "Clay multisensor foundation features extracted."
            },
            "confidence": 0.94
        }
