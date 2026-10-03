from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..app.models.prithvi_service import PrithviService

class PrithviTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="prithvi",
            description="NASA-IBM Earth observation foundation model backbone for multi-temporal and multi-spectral representation.",
            accepted_modalities=["OPTICAL", "MULTISPECTRAL"],
            capabilities=["eo_foundation_backbone", "representation_extraction", "landcover_embeddings"],
            input_requirements=["optical_image"],
            output_types=["embeddings", "feature_summary"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="8GB"
        )
        super().__init__(defn)
        self.service = PrithviService()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        image = context.get("optical_pil") or context.get("image1_pil")
        features = self.service.extract_features(image)
        return {
            "result": {
                "embedding_dim": features["embedding_dim"],
                "backbone": "Prithvi-EO-2.0"
            },
            "evidence": {
                "textual_evidence": f"Prithvi-EO-2.0 extracted {features['embedding_dim']}-dim representation vectors."
            },
            "confidence": 0.95
        }
